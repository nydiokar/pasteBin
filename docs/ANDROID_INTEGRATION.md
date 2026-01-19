# Android Integration - The Whole Point

## The Problem We're Solving

**You select text on your phone → Share → Choose "Paste Server" → DONE.**

Text is now on your server. Open browser on PC → latest paste is RIGHT THERE.

**No opening apps, no pasting into forms, no waiting for apps to load.**

---

## Solution: HTTP Shortcuts App (NO Custom App Needed!)

### Why HTTP Shortcuts?
- ✅ **Free & open-source**
- ✅ **Appears in Android share menu automatically**
- ✅ **No coding needed**
- ✅ **Sends HTTP POST directly to your server**
- ✅ **Shows success/failure notification**
- ✅ **Works offline (queues request when back online)**

### How It Works

```
1. Select text anywhere (browser, email, whatever)
2. Tap "Share"
3. Choose "Paste to Server" (HTTP Shortcuts)
4. [App sends POST in background]
5. Notification: "✓ Pasted successfully"
6. Open browser on PC → text is there
```

**Total time: 2 seconds. No form filling. No app loading.**

---

## Setup Instructions (One-Time, 5 Minutes)

### Step 1: Install HTTP Shortcuts
- Play Store: https://play.google.com/store/apps/details?id=ch.rmy.android.http_shortcuts
- Or F-Droid (open-source store)

### Step 2: Get Your Session Cookie

**Option A: From Browser (Easiest)**
1. Open your paste server in Chrome on phone
2. Login with password
3. Open Chrome menu → Settings → Site settings → Cookies
4. Find your domain → Copy session cookie value
5. Save it somewhere (we'll use it in Step 3)

**Option B: From DevTools**
1. Open paste server on PC
2. Login
3. F12 → Application tab → Cookies
4. Copy `session` cookie value

### Step 3: Create Shortcut in HTTP Shortcuts App

Open HTTP Shortcuts app → Create new shortcut:

**Basic Settings:**
- Name: `Paste to Server`
- Icon: Pick something recognizable (clipboard icon)

**Request Settings:**
- **URL**: `https://your-domain.duckdns.org/api/paste`
- **Method**: `POST`
- **Request Body Type**: `JSON`
- **Request Body**:
  ```json
  {
    "content": "{share_text}"
  }
  ```
  *(Note: `{share_text}` is a variable - HTTP Shortcuts fills it with shared text)*

**Headers:**
- Add header:
  - **Key**: `Cookie`
  - **Value**: `session=YOUR_SESSION_COOKIE_HERE`
    *(Paste the cookie you got from Step 2)*

**Response Handling:**
- **Success Message**: `✓ Pasted successfully`
- **Failure Message**: `✗ Failed to paste`
- **Show notification**: ✓ Enabled

**Trigger:**
- **Trigger type**: Share (text)
- This makes it appear in share menu

### Step 4: Test It
1. Open any app (browser, notes, email)
2. Select some text
3. Tap "Share"
4. Choose "Paste to Server"
5. Should see notification: "✓ Pasted successfully"
6. Open paste server on PC → text should be there

---

## Troubleshooting

### "Failed to paste" notification

**Cause 1: Session expired**
- Sessions last 24 hours
- Solution: Login again on phone, get new session cookie, update HTTP Shortcuts

**Cause 2: Wrong URL**
- Check URL is `https://` (not `http://`)
- Check domain is correct
- Test URL in browser first

**Cause 3: Server down**
- Check server is running: `docker ps`
- Check nginx is running
- Check DuckDNS domain resolves: `ping your-domain.duckdns.org`

### Session cookie keeps expiring

**Solution 1: Extend session duration**
- Edit backend `app.py`
- Change `PERMANENT_SESSION_LIFETIME` from 24h to 30 days:
  ```python
  app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
  ```

**Solution 2: Use API token instead** (better long-term)
- Backend generates a permanent token
- Use token in header instead of session cookie
- Add to backend later if session approach is annoying

### Share menu doesn't show "Paste to Server"

- Open HTTP Shortcuts app
- Check shortcut has "Share" trigger enabled
- Try creating shortcut again
- Restart phone (sometimes Android caches share menu)

---

## Alternative: Tasker (More Complex, More Powerful)

If you already use Tasker:

**Profile:**
- Event: Share Text Received

**Task:**
1. HTTP POST to `https://your-domain.duckdns.org/api/paste`
2. Headers: `Cookie: session=...`
3. Body: `{"content": "%STEXT"}`
4. Show notification on success/failure

**Pros:**
- More customizable
- Can add retry logic
- Can queue when offline

**Cons:**
- Costs money ($3)
- More complex setup
- Overkill for this use case

**Recommendation: Stick with HTTP Shortcuts unless you already use Tasker.**

---

## What If Server Is Unreachable?

### Scenario: Phone on cellular, server at home behind router

**Problem:** Can't reach server from outside network

**Solutions (Pick One):**

**Option 1: DuckDNS + Port Forwarding (Recommended)**
- Setup DuckDNS dynamic DNS (free)
- Forward port 443 on router to server
- Now accessible from anywhere: `https://yourdomain.duckdns.org`
- **This is the whole point - it's covered in SETUP.md**

**Option 2: Tailscale VPN**
- Install Tailscale on server + phone
- Always connected via VPN (encrypted tunnel)
- Server accessible even without port forwarding
- Slightly slower but very secure

**Option 3: Cloudflare Tunnel**
- No port forwarding needed
- Cloudflare proxies traffic
- Free tier available
- More complex setup

**Most people should use Option 1 (DuckDNS + port forward).**

---

## Session Management Strategy

### Problem: Don't want to update cookie every 24 hours

### Solution 1: Long-lived sessions (Quick fix)
```python
# In backend app.py
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
```

**Pros:** Set once, forget for a year
**Cons:** Less secure (if phone lost, session valid for year)

### Solution 2: API tokens (Better long-term)

**Backend changes:**
- Add `/api/token` endpoint (generate permanent token)
- Check token in auth middleware (instead of session)

**HTTP Shortcuts changes:**
- Header: `Authorization: Bearer YOUR_TOKEN_HERE`
- Never expires

**When to do this:**
- If session expiry becomes annoying
- Can add in 30 minutes later

**For MVP: Use Solution 1 (long sessions), add tokens later if needed.**

---

## Advanced: Offline Queueing

### Problem: Share text when offline, want it to send when back online

### Solution: HTTP Shortcuts has built-in retry

In HTTP Shortcuts settings:
- **Retry on failure**: ✓ Enabled
- **Retry delay**: 30 seconds
- **Max retries**: 10

Now if you share while offline:
- Shortcut fails silently
- Retries every 30 seconds
- Sends when connection restored
- Shows notification on success

---

## Alternative Approach: PWA (Future Enhancement)

### Progressive Web App

**What it is:**
- "Install" website as app (no app store)
- Appears in share menu natively
- Can work offline with service worker

**How to enable:**
1. Add `manifest.json` to frontend
2. Add service worker for offline support
3. User visits site → Browser prompts "Add to Home Screen"
4. Now appears in share menu automatically

**Benefits:**
- No separate app needed
- No session cookie management
- Just works

**Downside:**
- Requires service worker (100 lines JS)
- Not needed for MVP

**Recommendation: HTTP Shortcuts for now, PWA later if you want.**

---

## The Point (Summary)

### Without This Integration:
1. Copy text on phone
2. Open Telegram/Signal
3. Wait for app to load
4. Paste text
5. Send message to self
6. Open Telegram on PC
7. Wait for app to load
8. Copy text from Telegram

**Total: ~30 seconds, 8 steps, annoying**

### With HTTP Shortcuts:
1. Share text → "Paste to Server"
2. Open browser on PC

**Total: ~3 seconds, 2 steps, instant**

---

## Critical Files Reference

### Backend Endpoint (Already Planned)
```python
@app.route('/api/paste', methods=['POST'])
@require_auth  # Checks session cookie
@limiter.limit("30 per minute")
def create_paste():
    data = request.get_json()
    content = data.get('content')
    paste_id = db.create_paste(content)
    return jsonify({'id': paste_id, 'created_at': datetime.utcnow().isoformat()})
```

**This is already in the plan - just needs to be built.**

### HTTP Shortcuts Config (Export/Import)

After you create the shortcut, you can export it as JSON and share:

```json
{
  "name": "Paste to Server",
  "url": "https://your-domain.duckdns.org/api/paste",
  "method": "POST",
  "bodyType": "json",
  "body": "{\"content\": \"{share_text}\"}",
  "headers": [
    {
      "key": "Cookie",
      "value": "session=YOUR_SESSION_HERE"
    }
  ],
  "feedback": {
    "success": "✓ Pasted successfully",
    "failure": "✗ Failed to paste"
  }
}
```

**Save this config in `/deployment/http-shortcuts-config.json` so you don't forget.**

---

## Don't Forget Checklist

When deploying, ensure:
- [ ] DuckDNS domain set up
- [ ] Port 443 forwarded to server
- [ ] HTTPS/SSL working (Let's Encrypt)
- [ ] `/api/paste` endpoint working (test with curl)
- [ ] Rate limiting allows 30 requests/min
- [ ] Session lasts at least 24 hours (or use long-lived)
- [ ] HTTP Shortcuts app installed on phone
- [ ] Shortcut created and tested
- [ ] Session cookie updated in shortcut
- [ ] Test: Share text → See it on PC

**If all checked, you're done. Android integration complete.**

---

_This is the whole point. Everything else is just infrastructure to support this workflow._
