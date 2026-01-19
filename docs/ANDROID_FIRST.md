# 🎯 THE WHOLE POINT: Android Integration

## Why This Project Exists

**Problem:** Copying text from phone to PC is slow and annoying with Telegram/Signal.

**Solution:** Share text on phone → instantly on PC. No apps, no forms, no waiting.

---

## The User Experience (2 Seconds Total)

```
[Phone: Reading article in browser]
   ↓
1. Long-press to select text
2. Tap "Share"
3. Choose "Paste Server" from share menu
   ↓
[Notification: ✓ Pasted successfully]
   ↓
[PC: Open browser]
   ↓
Text is RIGHT THERE at the top
```

**That's it. No opening apps. No waiting. Just works.**

---

## How It Works (No Custom App Needed!)

### Use HTTP Shortcuts App
- **Free & open-source** Android app
- Appears in system share menu
- Sends HTTP POST directly to your server
- Shows success/failure notification

### One-Time Setup (5 Minutes)

1. **Install HTTP Shortcuts** (Play Store or F-Droid)

2. **Get session cookie**:
   - Open paste server in Chrome on phone
   - Login with password
   - Chrome menu → Settings → Site settings → Cookies → Find your domain
   - Copy session cookie value

3. **Create shortcut** in HTTP Shortcuts app:
   ```
   Name: Paste to Server
   URL: https://your-domain.duckdns.org/api/paste
   Method: POST
   Body Type: JSON
   Body: {"content": "{share_text}"}
   Header: Cookie: session=YOUR_SESSION_COOKIE
   Trigger: Share (text)
   Success message: ✓ Pasted successfully
   ```

4. **Test it**:
   - Select text anywhere
   - Share → "Paste to Server"
   - Should see success notification
   - Check PC browser → text is there

---

## Session Cookie Management

### Problem: Cookie expires after 24 hours

### Solution 1: Long-lived sessions (Easiest)
Backend config:
```python
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
```
Set once, forget for a year.

### Solution 2: API tokens (Better)
- Generate permanent token
- Use `Authorization: Bearer TOKEN` header instead
- Never expires
- Can add later if sessions are annoying

---

## Offline Handling

HTTP Shortcuts has **built-in retry**:
- Share while offline → queues request
- Retries every 30 seconds
- Sends when connection restored
- Shows notification on success

Enable in shortcut settings:
```
Retry on failure: ✓
Retry delay: 30 seconds
Max retries: 10
```

---

## Troubleshooting

### "Failed to paste" notification

**Check 1: Session expired?**
- Login again on phone
- Get new session cookie
- Update in HTTP Shortcuts

**Check 2: Server reachable?**
- Test URL in phone browser
- Should see paste server login/home page
- If not, check DuckDNS + port forwarding

**Check 3: URL correct?**
- Must be `https://` (not `http://`)
- Must end with `/api/paste`

### Share menu doesn't show shortcut

- Open HTTP Shortcuts app
- Check shortcut has "Share" trigger enabled
- Restart phone (Android caches share menu)

---

## Alternative: PWA (Future)

Make paste server a **Progressive Web App**:
- Add `manifest.json`
- Add service worker
- User: "Add to Home Screen"
- Now appears in share menu natively

**Pros:** No separate app, no cookie management
**Cons:** Requires service worker code

**Recommendation:** HTTP Shortcuts for MVP, PWA later if wanted.

---

## The Backend Support (Already Planned)

Backend endpoint (already in plan):
```python
@app.route('/api/paste', methods=['POST'])
@require_auth  # Validates session cookie
@limiter.limit("30 per minute")
def create_paste():
    data = request.get_json()
    content = data['content']
    paste_id = db.create_paste(content)
    return jsonify({'id': paste_id})
```

**This is already designed. Just needs to be built.**

---

## Critical Success Criteria

The project is ONLY successful if:

✅ You can share text from phone in 2 seconds
✅ Text appears on PC immediately when you open browser
✅ No need to open Telegram/Signal/any app
✅ Works reliably (doesn't fail randomly)
✅ Fast enough that it's your default workflow

If any of these fail, the project failed. Everything else is just infrastructure.

---

## Summary: Don't Forget This Part

Everything else (ChatGPT UI, dark mode, etc.) is nice-to-have.

**THIS is the core value:**
- Phone share menu → server → PC browser
- 2 seconds
- No friction
- Just works

**Remember this when building. This is the goal.**

---

_See ANDROID_INTEGRATION.md for detailed setup instructions._
