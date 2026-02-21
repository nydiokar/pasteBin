"""
Paste Server Backend - Clean, secure, minimal Flask API
~200 LOC with enterprise-grade practices
"""
import os
import sqlite3
import mimetypes
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any, List, Tuple

import bcrypt
from flask import Flask, request, jsonify, session, Response, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from werkzeug.utils import secure_filename


# ============================================================================
# Configuration
# ============================================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-change-in-prod')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3650)  # ~10 years - set once and forget
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'  # HTTPS only in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

CORS(app, supports_credentials=True)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"],
    storage_uri="memory://"
)

DB_PATH = os.environ.get('DB_PATH', 'data/pastes.db')
PASSWORD_HASH = os.environ.get('PASSWORD_HASH', '')  # bcrypt hash from env
API_KEY = os.environ.get('API_KEY', '')  # API key for headless/app access

UPLOAD_DIR = os.path.join(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else 'data', 'uploads')
MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


# ============================================================================
# Database Layer - Pure functions, no hidden state
# ============================================================================

def get_db() -> sqlite3.Connection:
    """Get database connection with Row factory for dict-like access"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database schema - idempotent"""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pastes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON pastes(created_at DESC)")

    # File upload columns — idempotent, silently skip if already present
    for col, typedef in [('filename', 'TEXT'), ('filepath', 'TEXT'), ('mimetype', 'TEXT')]:
        try:
            conn.execute(f"ALTER TABLE pastes ADD COLUMN {col} {typedef}")
        except sqlite3.OperationalError:
            pass  # column already exists

    conn.commit()
    conn.close()


def create_paste(content: str) -> int:
    """Insert paste, return ID"""
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO pastes (content, created_at) VALUES (?, ?)",
        (content, datetime.utcnow().isoformat())
    )
    paste_id: int = cursor.lastrowid
    conn.commit()
    conn.close()
    return paste_id


def sanitize_filename(filename: str) -> str:
    """Strip path traversal, leading dots/spaces. Returns '' if nothing remains."""
    name = secure_filename(os.path.basename(filename))
    name = name.lstrip('. ')
    return name


def dedupe_filename(name: str) -> str:
    """If name already exists in UPLOAD_DIR, append _1, _2, … until unique."""
    dest = os.path.join(UPLOAD_DIR, name)
    if not os.path.exists(dest):
        return name
    base, ext = os.path.splitext(name)
    counter = 1
    while os.path.exists(os.path.join(UPLOAD_DIR, f"{base}_{counter}{ext}")):
        counter += 1
    return f"{base}_{counter}{ext}"


def create_file_entry(original_filename: str, stored_filename: str, mimetype: str) -> int:
    """Insert a file entry (content=''), return ID."""
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO pastes (content, created_at, filename, filepath, mimetype) VALUES (?, ?, ?, ?, ?)",
        ('', datetime.utcnow().isoformat(), original_filename, stored_filename, mimetype)
    )
    file_id: int = cursor.lastrowid
    conn.commit()
    conn.close()
    return file_id


def get_pastes(limit: int = 50, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
    """Get pastes with pagination, return (pastes, total_count)"""
    conn = get_db()

    # Get total count
    total: int = conn.execute("SELECT COUNT(*) as count FROM pastes").fetchone()['count']

    # Get paginated results
    rows = conn.execute(
        "SELECT id, content, created_at, filename, filepath, mimetype FROM pastes ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()

    pastes: List[Dict[str, Any]] = [dict(row) for row in rows]
    conn.close()

    return pastes, total


def get_paste_by_id(paste_id: int) -> Optional[Dict[str, Any]]:
    """Get single paste by ID"""
    conn = get_db()
    row = conn.execute(
        "SELECT id, content, created_at, filename, filepath, mimetype FROM pastes WHERE id = ?",
        (paste_id,)
    ).fetchone()
    conn.close()

    return dict(row) if row else None


def delete_paste(paste_id: int) -> bool:
    """Delete paste (and file from disk if applicable), return success"""
    conn = get_db()
    row = conn.execute("SELECT filepath FROM pastes WHERE id = ?", (paste_id,)).fetchone()
    if row and row['filepath']:
        file_path = os.path.join(UPLOAD_DIR, row['filepath'])
        if os.path.isfile(file_path):
            os.remove(file_path)
    cursor = conn.execute("DELETE FROM pastes WHERE id = ?", (paste_id,))
    success: bool = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


# ============================================================================
# Auth Middleware
# ============================================================================

def require_auth(f):
    """Decorator: require valid session OR API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check session authentication (for web UI)
        if session.get('authenticated'):
            return f(*args, **kwargs)

        # Check API key authentication (for apps/scripts)
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer ') and API_KEY:
            provided_key = auth_header[7:]  # Remove "Bearer " prefix
            if provided_key == API_KEY:
                return f(*args, **kwargs)

        return jsonify({'error': 'Unauthorized'}), 401
    return decorated_function


def verify_password(password: str) -> bool:
    """Verify password against bcrypt hash from env"""
    if not PASSWORD_HASH:
        return False
    return bcrypt.checkpw(password.encode('utf-8'), PASSWORD_HASH.encode('utf-8'))


# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/health', methods=['GET'])
def health() -> Response:
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login() -> Response:
    """Authenticate with password, create session"""
    data = request.get_json()
    password: str = data.get('password', '')

    if not password or not verify_password(password):
        return jsonify({'error': 'Invalid password'}), 401

    session['authenticated'] = True
    session.permanent = True

    return jsonify({'success': True, 'message': 'Logged in successfully'})


@app.route('/api/logout', methods=['POST'])
def logout() -> Response:
    """Clear session"""
    session.clear()
    return jsonify({'success': True})


@app.route('/api/paste', methods=['POST'])
@require_auth
@limiter.limit("30 per minute")
def create_paste_endpoint() -> Response:
    """Create new paste"""
    data = request.get_json()
    content: str = data.get('content', '').strip()

    if not content:
        return jsonify({'error': 'Content cannot be empty'}), 400

    if len(content) > 1_000_000:  # 1MB limit
        return jsonify({'error': 'Content too large (max 1MB)'}), 400

    paste_id = create_paste(content)

    return jsonify({
        'id': paste_id,
        'created_at': datetime.utcnow().isoformat()
    }), 201


@app.route('/api/pastes', methods=['GET'])
@require_auth
def get_pastes_endpoint() -> Response:
    """Get paginated pastes"""
    try:
        limit: int = min(int(request.args.get('limit', 50)), 100)  # Max 100 per request
        offset: int = int(request.args.get('offset', 0))
    except ValueError:
        return jsonify({'error': 'Invalid pagination parameters'}), 400

    pastes, total = get_pastes(limit, offset)

    return jsonify({
        'pastes': pastes,
        'total': total,
        'limit': limit,
        'offset': offset
    })


@app.route('/api/paste/<int:paste_id>', methods=['GET'])
@require_auth
def get_paste_endpoint(paste_id: int) -> Response:
    """Get single paste"""
    paste = get_paste_by_id(paste_id)

    if not paste:
        return jsonify({'error': 'Paste not found'}), 404

    return jsonify(paste)


@app.route('/api/paste/<int:paste_id>', methods=['DELETE'])
@require_auth
@limiter.limit("10 per minute")
def delete_paste_endpoint(paste_id: int) -> Response:
    """Delete paste"""
    success = delete_paste(paste_id)

    if not success:
        return jsonify({'error': 'Paste not found'}), 404

    return jsonify({'success': True, 'message': 'Paste deleted'})


@app.route('/api/upload', methods=['POST'])
@require_auth
@limiter.limit("10 per minute")
def upload_file_endpoint() -> Response:
    """Upload a file (max 25 MB)"""
    if request.content_length and request.content_length > MAX_UPLOAD_SIZE:
        return jsonify({'error': 'File too large (max 25 MB)'}), 413

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No filename'}), 400

    original_name = sanitize_filename(file.filename)
    if not original_name:
        return jsonify({'error': 'Invalid filename'}), 400

    stored_name = dedupe_filename(original_name)
    dest = os.path.join(UPLOAD_DIR, stored_name)

    # Final path-escape check
    if not os.path.realpath(dest).startswith(os.path.realpath(UPLOAD_DIR)):
        return jsonify({'error': 'Invalid filename'}), 400

    file.save(dest)

    # Verify size on disk (in case Content-Length was missing/wrong)
    if os.path.getsize(dest) > MAX_UPLOAD_SIZE:
        os.remove(dest)
        return jsonify({'error': 'File too large (max 25 MB)'}), 413

    mime = mimetypes.guess_type(stored_name)[0] or 'application/octet-stream'
    file_id = create_file_entry(original_name, stored_name, mime)

    return jsonify({
        'id': file_id,
        'filename': original_name,
        'created_at': datetime.utcnow().isoformat()
    }), 201


@app.route('/api/file/<int:paste_id>', methods=['GET'])
@require_auth
def serve_file_endpoint(paste_id: int) -> Response:
    """Serve an uploaded file"""
    paste = get_paste_by_id(paste_id)
    if not paste or not paste.get('filepath'):
        return jsonify({'error': 'File not found'}), 404

    file_path = os.path.join(UPLOAD_DIR, paste['filepath'])

    # Path-escape check
    if not os.path.realpath(file_path).startswith(os.path.realpath(UPLOAD_DIR)):
        return jsonify({'error': 'Invalid file path'}), 400

    if not os.path.isfile(file_path):
        return jsonify({'error': 'File not found on disk'}), 404

    ext = paste['filepath'].rsplit('.', 1)[-1].lower() if '.' in paste['filepath'] else ''
    disposition = 'inline' if ext in ALLOWED_IMAGE_EXTENSIONS else 'attachment'

    return send_file(
        file_path,
        mimetype=paste['mimetype'],
        download_name=paste['filename'] if disposition == 'attachment' else None,
        as_attachment=(disposition == 'attachment')
    )


# ============================================================================
# Initialization
# ============================================================================

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else 'data', exist_ok=True)

# Ensure uploads directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize database on startup
init_db()


if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')
