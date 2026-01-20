# START HERE - Quick Setup Guide

## Step 1: Start Docker Desktop

**Open Docker Desktop application on Windows**
- Wait until Docker Desktop is fully running
- You should see the Docker icon in system tray

---

## Step 2: Generate Configuration

Open PowerShell in this directory and run:

```powershell
# 1. Generate session secret
python scripts/generate_secret.py
```

**Copy the SESSION_SECRET line** (the long random string)

```powershell
# 2. Generate password hash (use a password you'll remember, like "test1234")
python scripts/init_password.py
```

**Copy the PASSWORD_HASH line** (starts with $2b$12$...)

---

## Step 3: Create .env File

1. Go to `deployment` folder
2. Copy `env.example` to `.env`
3. Edit `.env` file and replace:
   - `SESSION_SECRET=...` with your generated secret
   - `PASSWORD_HASH=...` with your generated hash

**Your `deployment/.env` should look like:**

```env
SESSION_SECRET=QYROCXRXwK3WA91T49pMOAxLWAk-r_lF7jCkbNREFTMcIbgf7fSCYvRAXM5e7F5gXnNatv-jvsCtzehFyuHVKg
PASSWORD_HASH=$2b$12$coAliSO0s6UIzIH5BjgTq.Um2wtd5zbL5OSDO1tfseBYp.3in1gP6
DOMAIN=localhost
FLASK_ENV=development
```

*(Use YOUR generated values, not these examples)*

---

## Step 4: Start the Application

```powershell
# Build and start containers
docker-compose -f deployment/docker-compose.yml up -d --build
```

**Wait 1-2 minutes for build to complete**

---

## Step 5: Verify It's Running

```powershell
# Check containers
docker ps
```

You should see:
- `paste-server-backend` (healthy)
- `paste-server-nginx` (healthy)

```powershell
# Test health endpoint
curl http://localhost/health
```

Should return: `{"status":"healthy","timestamp":"..."}`

---

## Step 6: Open in Browser

1. Open browser: **http://localhost**
2. Login with the password you created in Step 2
3. Click "+ New Dump"
4. Create your first paste!

---

## Quick Commands

```powershell
# View logs
docker-compose -f deployment/docker-compose.yml logs -f

# Stop services
docker-compose -f deployment/docker-compose.yml down

# Restart services
docker-compose -f deployment/docker-compose.yml restart

# Complete cleanup (removes all data)
docker-compose -f deployment/docker-compose.yml down -v
```

---

## Troubleshooting

**"Docker daemon not running"**
→ Start Docker Desktop and wait for it to fully load

**"Port 80 already in use"**
→ Edit `deployment/docker-compose.yml`, change port to `8080:80`, access at http://localhost:8080

**"Invalid password"**
→ Regenerate password hash with `python scripts/init_password.py` and update `.env`

**Container won't start**
→ Check logs: `docker-compose -f deployment/docker-compose.yml logs backend`

---

## That's It!

Once working locally, see `docs/SETUP.md` for production deployment with HTTPS.
