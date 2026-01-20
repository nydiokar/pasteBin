# Paste Server - Complete Setup Guide

Production-ready deployment with Docker, HTTPS, and DuckDNS.

---

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for setup scripts)
- Home server or VPS
- (Optional) Domain via DuckDNS (free)

---

## Quick Start (Local Development)

```powershell
# 1. Clone/copy project
cd paste-server

# 2. Install Python dependencies for scripts
python -m pip install bcrypt

# 3. Generate session secret
python scripts/generate_secret.py

# 4. Generate password hash
python scripts/init_password.py

# 5. Create .env file
# Copy output from steps 3 & 4 into deployment/.env
```

**Example `deployment/.env`:**
```env
SESSION_SECRET=<output_from_step_3>
PASSWORD_HASH=<output_from_step_4>
DOMAIN=localhost
```

```powershell
# 6. Start services
docker-compose -f deployment/docker-compose.yml up -d --build

# 7. Access
# Open http://localhost in browser
# Login with the password you set in step 4
```

---

## Production Deployment (HTTPS + DuckDNS)

### Step 1: DuckDNS Setup (Free Dynamic DNS)

1. Go to https://www.duckdns.org
2. Login (GitHub/Google/etc.)
3. Create subdomain: `your-name.duckdns.org`
4. Copy your token

**Update IP address:**
```powershell
# Windows: Add to Task Scheduler (run every 5 minutes)
Invoke-WebRequest -Uri "https://www.duckdns.org/update?domains=your-name&token=YOUR_TOKEN&ip="
```

Or use their Windows client (easier).

### Step 2: Router Configuration

1. Login to router admin panel
2. Find "Port Forwarding" settings
3. Forward ports to your server:
   - Port 80 → Server IP:80 (HTTP)
   - Port 443 → Server IP:443 (HTTPS)

### Step 3: SSL Certificate (Let's Encrypt)

**Option A: Using Certbot (Recommended)**

```powershell
# On server
docker run -it --rm \
  -v ${PWD}/deployment/ssl:/etc/letsencrypt \
  certbot/certbot certonly --standalone \
  -d your-name.duckdns.org \
  --email your-email@example.com \
  --agree-tos

# Certificates will be in deployment/ssl/live/your-name.duckdns.org/
```

**Option B: Using acme.sh (Alternative)**

```powershell
# Install acme.sh
curl https://get.acme.sh | sh

# Get certificate
~/.acme.sh/acme.sh --issue -d your-name.duckdns.org --standalone

# Copy to deployment folder
~/.acme.sh/acme.sh --install-cert -d your-name.duckdns.org \
  --cert-file deployment/ssl/cert.pem \
  --key-file deployment/ssl/privkey.pem \
  --fullchain-file deployment/ssl/fullchain.pem
```

### Step 4: Configure Nginx for HTTPS

Edit `deployment/nginx.conf`:

1. Uncomment HTTPS server block (bottom of file)
2. Update `server_name` to your DuckDNS domain
3. Uncomment HTTP redirect (line near "# return 301")

### Step 5: Update .env

```env
SESSION_SECRET=<your_session_secret>
PASSWORD_HASH=<your_password_hash>
DOMAIN=your-name.duckdns.org
```

### Step 6: Deploy

```powershell
# Build and start
docker-compose -f deployment/docker-compose.yml up -d --build

# Check logs
docker-compose -f deployment/docker-compose.yml logs -f

# Check health
curl https://your-name.duckdns.org/health
```

### Step 7: Auto-Renew SSL

Certificates expire after 90 days. Setup auto-renewal:

**Windows Task Scheduler:**
```powershell
# Run every month
docker run --rm \
  -v ${PWD}/deployment/ssl:/etc/letsencrypt \
  certbot/certbot renew

# Reload nginx
docker-compose -f deployment/docker-compose.yml restart nginx
```

---

## Verification Checklist

After deployment, verify:

- [ ] Can access `https://your-domain.duckdns.org`
- [ ] Login works with password
- [ ] Can create new paste
- [ ] Can copy paste content
- [ ] Can delete paste
- [ ] Dark mode toggle works
- [ ] Mobile responsive (sidebar overlay)
- [ ] `/health` endpoint returns 200

---

## Maintenance

### View Logs
```powershell
# All services
docker-compose -f deployment/docker-compose.yml logs -f

# Backend only
docker logs paste-server-backend -f

# Nginx only
docker logs paste-server-nginx -f
```

### Restart Services
```powershell
# Restart all
docker-compose -f deployment/docker-compose.yml restart

# Restart backend only
docker-compose -f deployment/docker-compose.yml restart backend
```

### Backup Database
```powershell
# Database is in Docker volume: paste-data
# Backup:
docker cp paste-server-backend:/app/data/pastes.db ./backup-$(date +%Y%m%d).db

# Restore:
docker cp ./backup-20260119.db paste-server-backend:/app/data/pastes.db
docker-compose -f deployment/docker-compose.yml restart backend
```

### Update Application
```powershell
# Pull latest code
git pull

# Rebuild and restart
docker-compose -f deployment/docker-compose.yml up -d --build
```

---

## Troubleshooting

### "Connection refused" when accessing domain

**Check 1: Is server running?**
```powershell
docker ps
# Should see paste-server-backend and paste-server-nginx
```

**Check 2: Are ports forwarded?**
```powershell
# From external network (phone on cellular), test:
curl -I http://your-domain.duckdns.org
```

**Check 3: Is DuckDNS IP correct?**
```powershell
# Check current IP
nslookup your-domain.duckdns.org

# Should match your public IP
# Find your IP at: https://ifconfig.me
```

### "Invalid password" on login

**Regenerate password hash:**
```powershell
python scripts/init_password.py
# Copy new hash to deployment/.env
docker-compose -f deployment/docker-compose.yml restart backend
```

### SSL certificate errors

**Re-generate certificate:**
```powershell
# Remove old certs
rm -rf deployment/ssl

# Generate new
docker run -it --rm \
  -v ${PWD}/deployment/ssl:/etc/letsencrypt \
  certbot/certbot certonly --standalone \
  -d your-name.duckdns.org \
  --email your@email.com \
  --agree-tos --force-renewal

# Restart nginx
docker-compose -f deployment/docker-compose.yml restart nginx
```

### Database corruption

**Reset database (deletes all pastes):**
```powershell
# Stop backend
docker-compose -f deployment/docker-compose.yml stop backend

# Remove database file
docker volume rm paste-data

# Restart (creates new empty database)
docker-compose -f deployment/docker-compose.yml up -d backend
```

---

## Security Best Practices

✅ **Strong password**: Use 16+ character random password
✅ **HTTPS only**: Always use HTTPS in production
✅ **Rate limiting**: Built-in (5 login attempts, 30 pastes/min)
✅ **Session timeout**: 30 days (configurable in backend/app.py)
✅ **HTTP-only cookies**: Prevents XSS attacks
✅ **Firewall**: Only ports 80 and 443 should be open
✅ **Updates**: Keep Docker images updated

---

## Performance Tuning

### Increase paste limit per request
Edit `backend/app.py`:
```python
limit: int = min(int(request.args.get('limit', 50)), 200)  # Increase from 100 to 200
```

### Increase gunicorn workers
Edit `backend/Dockerfile`:
```dockerfile
CMD ["gunicorn", "--workers", "4", ...]  # Increase from 2 to 4
```

### Enable nginx caching
Edit `deployment/nginx.conf`:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m;

location /api/pastes {
    proxy_cache api_cache;
    proxy_cache_valid 200 60s;
    # ... rest of config
}
```

---

## Android Integration

See [ANDROID_INTEGRATION.md](ANDROID_INTEGRATION.md) for complete setup.

**Quick version:**
1. Install "HTTP Shortcuts" app
2. Login to paste server on phone, copy session cookie
3. Create shortcut:
   - URL: `https://your-domain.duckdns.org/api/paste`
   - Method: POST
   - Body: `{"content": "{share_text}"}`
   - Header: `Cookie: session=YOUR_SESSION_COOKIE`
   - Trigger: Share (text)
4. Share text anywhere → "Paste to Server" → Done

---

## Next Steps

After deployment:
1. Test from multiple devices (phone, tablet, laptop)
2. Setup automatic backups (cron job to backup database)
3. Setup monitoring (optional: Uptime Kuma, Healthchecks.io)
4. Configure Android share integration
5. Share access with family/friends (same password, or extend with multi-user support later)

---

**For issues or questions, see the GitHub repository.**
