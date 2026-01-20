# Paste Server - Project Context

**Branch:** `main` • **Last Updated:** 2026-01-19 • **Status:** 🟢 Active Development

---

## 🎯 Project Goal

**Phone-to-PC text sharing in 2 seconds** - Share text from Android → instantly appears on PC browser. No apps, no Telegram/Signal, just works.

**Core workflow:** Select text on phone → Share → "Paste Server" → Text appears on PC

---

## 📋 Current Status

| Component | Status | Notes |
|:----------|:------:|:------|
| Backend API | ✅ | Flask + SQLite, sessions working |
| Frontend UI | ✅ | Dark mode, shows last 3 pastes, refresh button |
| Docker Setup | ✅ | Local HTTP testing ready |
| Android Integration | ✅ | HTTP Shortcuts configured and working |
| Production Deployment | 📝 | Pending HTTPS + DuckDNS setup |

---

## 🏗️ Architecture

### Stack
- **Backend:** Python Flask, SQLite, bcrypt auth
- **Frontend:** Vanilla JS, no frameworks
- **Deployment:** Docker Compose (nginx + backend)
- **Android:** HTTP Shortcuts app (no custom app needed)

### Key Files
```
paste-server/
├── backend/
│   └── app.py                 # Flask API (~250 LOC)
├── frontend/
│   ├── index.html
│   ├── app.js                 # Main frontend logic
│   └── style.css
├── deployment/
│   ├── docker-compose.yml
│   ├── .env                   # SESSION_SECRET, PASSWORD_HASH
│   └── env.example
└── scripts/
    ├── generate_secret.py     # Generate SESSION_SECRET
    └── init_password.py       # Generate PASSWORD_HASH (wrapped in quotes)
```

---

## 📅 Recent Activity

### January 19, 2026

| ID | T | Title | Scope | Notes |
|:--:|:-:|:------|:-----:|:------|
| 19.1 | ✅ | Password hash escaping fix | 🔹 | Bcrypt hashes contain `$` - wrapped in single quotes to prevent Docker variable substitution |
| 19.2 | ✅ | Copy button fix for HTTP/mobile | 🔸 | Added fallback using `document.execCommand` for HTTP (modern clipboard API requires HTTPS) |
| 19.3 | ✅ | Session persistence | 🔹 | Added auth check on page load - no more logout on refresh |
| 19.4 | ✅ | Show multiple pastes | 🔹 | Main area now shows selected paste + next 2 (instead of just 1) |
| 19.5 | ✅ | Refresh button | 🔹 | Added manual refresh button (🔄) to fetch latest pastes without page reload |
| 19.6 | ✅ | HTTP Shortcuts Android setup | 🔸 | Configured share target with global variable - working end-to-end |

**Summary:**

**19.1:** Fixed Docker environment variable parsing issue. Bcrypt password hashes start with `$2b$12$...` which Docker interprets as variables. Modified `init_password.py` to output hash wrapped in single quotes: `PASSWORD_HASH='$2b$12$...'`

**19.2:** Copy button failed on mobile HTTP. Modern `navigator.clipboard` API requires HTTPS. Added `fallbackCopy()` function using deprecated-but-working `document.execCommand('copy')` for HTTP compatibility.

**19.3:** Users were logged out on every page refresh. Added `checkAuth()` function that tests session validity on page load by attempting to fetch pastes. If successful, stays logged in. Sessions last 30 days per backend config.

**19.4:** Changed `renderMainArea()` to display selected paste plus the next 2 pastes (total 3) instead of just one. Uses `Array.slice(selectedIndex, selectedIndex + 3)` to get consecutive pastes.

**19.5:** Added refresh button to top bar that fetches latest pastes without full page reload. Shows visual feedback: ⏳ → ✓ → 🔄. Re-selects current paste if it still exists, otherwise selects latest.

**19.6:** Figured out HTTP Shortcuts configuration. Key insight: Must create global variable with "Allow 'Share...'" checkbox enabled, then insert variable into request body using **{}** button (not just typing variable name). Shortcut now appears in Android share menu and successfully POSTs shared text to server.

---

## 🔧 Configuration Notes

### Environment Variables (`deployment/.env`)

```env
SESSION_SECRET=<generated-random-string>
PASSWORD_HASH='$2b$12$...'              # MUST be wrapped in single quotes!
DOMAIN=localhost
FLASK_ENV=development                   # Allows HTTP cookies for local testing
```

**Critical:** `PASSWORD_HASH` must be in single quotes to prevent shell/Docker from interpreting `$` symbols.

### HTTP Shortcuts Setup (Android)

1. **Create Global Variable:**
   - Top menu → Global Variables → +
   - Type: Static Variable
   - Name: `shared_text`
   - **CHECK:** "Allow 'Share...'"
   - Select: Text
   - Save

2. **Create Shortcut:**
   - Name: Paste to Server
   - URL: `http://192.168.1.19/api/paste` (use your PC's local IP)
   - Method: POST
   - Request Body Type: Custom Text
   - Request Body: Click **{}** button → select `shared_text` variable
   - Content-Type: `application/json`
   - Headers → Add: `Cookie` = `session=<your-session-cookie>`
   - Trigger & Execution → Enable "Show as app shortcut on launcher"
   - Save

3. **Get Session Cookie:**
   - Login on phone browser at `http://<your-pc-ip>`
   - Browser settings → Cookies → Copy `session` value
   - Paste into HTTP Shortcuts header

**Key insight:** Must use **{}** button to insert variable - typing `{shared_text}` manually doesn't work.

---

## ⚠️ Known Issues

| Severity | Issue | Workaround | Status |
|:--------:|:------|:-----------|:------:|
| 🟡 | Copy button may not work on some mobile browsers (HTTP) | Use HTTPS in production | Expected |
| 🟡 | Browser cache issues on mobile | Hard refresh or clear cache | User action |
| 🟡 | Session cookie expires after 30 days | Re-login and update HTTP Shortcuts cookie | By design |

---

## 📝 Next Steps (Not Started)

1. **Production Deployment:**
   - Set up DuckDNS dynamic DNS
   - Configure HTTPS with Let's Encrypt
   - Port forwarding on router (443)
   - Update HTTP Shortcuts to use `https://yourname.duckdns.org`

2. **Optional Enhancements:**
   - API token auth (instead of session cookies for Android)
   - PWA (Progressive Web App) for native share menu
   - WebSocket for real-time sync (instead of manual refresh)

---

## 💡 Development Commands

```powershell
# Generate secrets (run once)
python scripts/generate_secret.py
python scripts/init_password.py

# Start services
docker-compose -f deployment/docker-compose.yml up -d --build

# View logs
docker-compose -f deployment/docker-compose.yml logs -f

# Restart after code changes
docker-compose -f deployment/docker-compose.yml restart

# Stop everything
docker-compose -f deployment/docker-compose.yml down

# Complete cleanup (removes data)
docker-compose -f deployment/docker-compose.yml down -v
```

**Local access:** http://localhost (or http://192.168.1.19 from phone)

---

**Last Updated:** 2026-01-19 • **Branch:** `main`
