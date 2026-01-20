"""
Paste Server Backend - Clean, secure, minimal Flask API
~200 LOC with enterprise-grade practices
"""
import os
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any, List, Tuple

import bcrypt
from flask import Flask, request, jsonify, session, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS


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


def get_pastes(limit: int = 50, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
    """Get pastes with pagination, return (pastes, total_count)"""
    conn = get_db()

    # Get total count
    total: int = conn.execute("SELECT COUNT(*) as count FROM pastes").fetchone()['count']

    # Get paginated results
    rows = conn.execute(
        "SELECT id, content, created_at FROM pastes ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()

    pastes: List[Dict[str, Any]] = [dict(row) for row in rows]
    conn.close()

    return pastes, total


def get_paste_by_id(paste_id: int) -> Optional[Dict[str, Any]]:
    """Get single paste by ID"""
    conn = get_db()
    row = conn.execute(
        "SELECT id, content, created_at FROM pastes WHERE id = ?",
        (paste_id,)
    ).fetchone()
    conn.close()

    return dict(row) if row else None


def delete_paste(paste_id: int) -> bool:
    """Delete paste, return success"""
    conn = get_db()
    cursor = conn.execute("DELETE FROM pastes WHERE id = ?", (paste_id,))
    success: bool = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


# ============================================================================
# Auth Middleware
# ============================================================================

def require_auth(f):
    """Decorator: require valid session"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
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


# ============================================================================
# Initialization
# ============================================================================

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else 'data', exist_ok=True)

# Initialize database on startup
init_db()


if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')
