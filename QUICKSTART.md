# Paste Server - Quick Start

Get running in 3 minutes.

---

## Windows (PowerShell)

### Prerequisites
```powershell
# Check Docker is installed
docker --version

# Check Python is installed
python --version  # Should be 3.11+
```

### Setup
```powershell
# 1. Navigate to project
cd paste-server

# 2. Install bcrypt for password hashing
pip install bcrypt

# 3. Generate session secret
python scripts\generate_secret.py
# Copy the SESSION_SECRET output

# 4. Generate password hash
python scripts\init_password.py
# Enter your desired password
# Copy the PASSWORD_HASH output

# 5. Create .env file
# Create deployment\.env with:
```

**Create `deployment\.env`:**
```env
SESSION_SECRET=<paste_from_step_3>
PASSWORD_HASH=<paste_from_step_4>
DOMAIN=localhost
```

```powershell
# 6. Start services
docker-compose -f deployment\docker-compose.yml up -d --build

# 7. Access
# Open http://localhost in browser
# Login with the password you created in step 4
```

---

## Linux / macOS

### Prerequisites
```bash
# Check Docker
docker --version

# Check Python
python3 --version  # Should be 3.11+
```

### Setup
```bash
# 1. Navigate to project
cd paste-server

# 2. Install bcrypt
pip3 install bcrypt

# 3. Generate session secret
python3 scripts/generate_secret.py

# 4. Generate password hash
python3 scripts/init_password.py

# 5. Create deployment/.env
# (Copy outputs from steps 3 & 4)

# 6. Start services
docker-compose -f deployment/docker-compose.yml up -d --build

# 7. Access http://localhost
```

---

## Verify Installation

```powershell
# Check containers are running
docker ps
# Should see: paste-server-backend, paste-server-nginx

# Check logs
docker-compose -f deployment\docker-compose.yml logs -f

# Test health endpoint
curl http://localhost/health
# Should return: {"status":"healthy","timestamp":"..."}
```

---

## First Login

1. Open http://localhost
2. Enter the password you created
3. Click "Login"
4. Click "+ New Dump"
5. Paste some text
6. Click "Save"

That's it! Your paste server is running.

---

## Stop Services

```powershell
docker-compose -f deployment\docker-compose.yml down
```

---

## Next Steps

- **Production deployment**: See [docs/SETUP.md](docs/SETUP.md)
- **Android integration**: See [docs/ANDROID_INTEGRATION.md](docs/ANDROID_INTEGRATION.md)
- **Full documentation**: See [README.md](README.md)

---

## Troubleshooting

**Port 80 already in use:**
```powershell
# Edit deployment/docker-compose.yml
# Change ports section:
ports:
  - "8080:80"  # Use 8080 instead
  - "443:443"

# Access at http://localhost:8080
```

**Permission denied (Linux):**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

**Database permission errors:**
```powershell
# Remove and recreate volume
docker-compose -f deployment\docker-compose.yml down -v
docker-compose -f deployment\docker-compose.yml up -d --build
```
