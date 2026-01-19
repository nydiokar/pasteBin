# Paste Server

Self-hosted paste service with ChatGPT-style interface for seamless text sharing between phone and PC.

## What is this?

**The whole point:** Share text on phone → instantly on PC. No apps, no forms, 2 seconds.

A web app with ChatGPT-style interface for your personal text dumps:
- **🎯 Android share menu**: Select text → Share → "Paste Server" → DONE
- **Sidebar**: Date-grouped paste history (Today, Yesterday, etc.)
- **Main area**: Clean reading space with latest paste always visible
- **Dark mode**: Built-in toggle, persists preference
- **Password protected**: Simple single-password auth
- **Infinite history**: No limits, lazy loading

## Why?

Tired of:
- Slow app loading times (Telegram, Signal, etc.)
- Relying on 3rd party services
- Apps that need to "catch up" when offline

Browser-based = instant, reliable, always works.

## Features

- ✅ **ChatGPT-style UI**: Familiar sidebar + main area layout
- ✅ **Fast**: Browser loads instantly vs app startup
- ✅ **Private**: Your server, your data, your rules
- ✅ **Secure**: Password protected, rate limited, HTTPS
- ✅ **Dark mode**: Toggle and persist preference
- ✅ **Infinite pastes**: Lazy loading, no 100-item limits
- ✅ **Mobile-friendly**: Responsive design, Android share integration

## Quick Start

### Prerequisites
- Docker & docker-compose
- Domain via DuckDNS (free)
- Home server or VPS

### Setup (5 minutes)
```bash
# Clone/copy this project
cd paste-server

# Generate password (coming soon)
python scripts/init_password.py

# Configure environment
cp deployment/.env.example deployment/.env
# Edit .env with your password hash

# Start services
docker-compose -f deployment/docker-compose.yml up -d

# Access at http://localhost
```

For full deployment with HTTPS + DuckDNS, see [docs/SETUP.md](docs/SETUP.md)

## Project Structure

```
paste-server/
├── backend/       # Python/Flask API (one simple file)
├── frontend/      # HTML + CSS + JS (chat-like UI)
├── deployment/    # Docker + Nginx configs
├── docs/          # Documentation
└── scripts/       # Utility scripts
```

## Documentation

**Start here:**
- [**🎯 ANDROID_FIRST.md**](docs/ANDROID_FIRST.md) - THE WHOLE POINT: Phone share menu integration
- [**ANDROID_INTEGRATION.md**](docs/ANDROID_INTEGRATION.md) - Detailed Android setup with troubleshooting

**Architecture:**
- [**FINAL_PLAN.md**](docs/FINAL_PLAN.md) - Complete architecture and features
- [**UI_MOCKUP.md**](docs/UI_MOCKUP.md) - Visual design reference
- [**CHECKLIST.md**](docs/CHECKLIST.md) - Implementation tracking

**Deployment:** _(coming soon)_
- [**SETUP.md**](docs/SETUP.md) - Full deployment guide (DuckDNS + Docker + SSL)

## Tech Stack

- **Backend**: Python + Flask + SQLite (~200 lines)
- **Frontend**: Vanilla JS + CSS (~400 lines, no build step)
- **Deployment**: Docker + Nginx + Let's Encrypt
- **Auth**: Single password (bcrypt) + rate limiting

## Development Status

**Current Phase**: Planning complete, ready to build

See [docs/CHECKLIST.md](docs/CHECKLIST.md) for implementation progress.

## License

MIT - Use however you want

---

_Built because browsers are faster than apps, and ChatGPT's interface is perfect for reading._
