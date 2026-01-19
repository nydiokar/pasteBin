# Implementation Checklist

Simple tracking for building the paste server.

---

## Backend (app.py)

### Setup
- [ ] Flask app initialization
- [ ] Load config from .env (PASSWORD_HASH, SESSION_SECRET)
- [ ] SQLite connection (one table: pastes)
- [ ] Flask-Limiter for rate limiting

### Endpoints
- [ ] `POST /api/login` - Password auth, create session
- [ ] `POST /api/paste` - Create new paste
- [ ] `GET /api/pastes` - List pastes (with pagination for lazy loading)
- [ ] `GET /api/paste/<id>` - Get specific paste
- [ ] `DELETE /api/paste/<id>` - Delete paste
- [ ] `GET /health` - Health check

### Security
- [ ] Auth middleware (session check)
- [ ] Rate limiting (5 login attempts, 30 pastes/min)
- [ ] Password hash verification (bcrypt)
- [ ] CORS configuration

### Database
- [ ] Create table: id, content, created_at
- [ ] INSERT paste
- [ ] SELECT with pagination (ORDER BY created_at DESC)
- [ ] DELETE paste

---

## Frontend

### Structure (index.html)
- [ ] Login page (if not authenticated)
- [ ] Main app layout:
  - [ ] Top bar (New Dump button, dark mode toggle, logout)
  - [ ] Sidebar (date-grouped paste list)
  - [ ] Main reading area
  - [ ] "New Dump" modal

### Styling (style.css)
- [ ] CSS Grid layout (sidebar + main area)
- [ ] Light mode colors
- [ ] Dark mode colors (CSS variables)
- [ ] Mobile responsive (sidebar overlay)
- [ ] Typography and spacing
- [ ] Button styles
- [ ] Modal styles

### JavaScript (app.js)
- [ ] Login handler
- [ ] Load pastes from API
- [ ] Group pastes by date (Today, Yesterday, Jan 18, etc.)
- [ ] Render sidebar with groups
- [ ] Select paste (show in main area)
- [ ] Auto-select latest paste on load
- [ ] "New Dump" modal open/close
- [ ] Create paste (POST /api/paste)
- [ ] Copy to clipboard
- [ ] Delete paste (with confirmation)
- [ ] Dark mode toggle (persist to localStorage)
- [ ] Lazy loading (infinite scroll in sidebar)

---

## Deployment

### Docker
- [ ] Dockerfile (Python base, Flask app)
- [ ] docker-compose.yml (app + nginx)
- [ ] Named volume for database persistence

### Nginx
- [ ] nginx.conf (reverse proxy to Flask)
- [ ] Static file serving (frontend)
- [ ] SSL configuration placeholders

### Configuration
- [ ] .env.example (PASSWORD_HASH, SESSION_SECRET)
- [ ] Script to generate password hash

---

## Documentation

- [ ] SETUP.md - Full deployment guide (DuckDNS + Docker + nginx + SSL)
- [ ] ANDROID.md - HTTP Shortcuts setup for share menu
- [ ] README.md - Quick start

---

## Testing

- [ ] Login works
- [ ] Create paste works
- [ ] Pastes grouped by date correctly
- [ ] Click sidebar shows paste in main area
- [ ] Latest paste auto-selected on load
- [ ] Copy button works
- [ ] Delete button works (with confirmation)
- [ ] Dark mode toggles and persists
- [ ] Lazy loading (scroll sidebar loads more)
- [ ] Rate limiting blocks after 5 failed logins
- [ ] Mobile responsive (sidebar overlay)
- [ ] HTTPS works
- [ ] Android share integration works
- [ ] Database persists after container restart

---

## Success Criteria

✅ Looks like ChatGPT/Claude interface
✅ Latest paste visible immediately on open
✅ Sidebar groups by date (Today, Yesterday, etc.)
✅ Dark mode works and persists
✅ Can create paste via "+ New Dump" button
✅ Can copy/delete any paste
✅ Infinite scroll works
✅ Android share works
✅ Password protected
✅ HTTPS enabled

---

_Estimated time: ~9 hours focused work_
