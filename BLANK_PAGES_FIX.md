# Quick Fix Guide - Blank Pages Issue

## Problem
All pages showing blank in the browser.

## Quick Fix Steps

### 1. Clear Cache and Rebuild
```bash
cd frontend
rm -rf .next
npm run build
npm run dev
```

### 2. Check Browser Console
Open browser DevTools (F12) and check for JavaScript errors in the Console tab.

### 3. Verify Backend is Running
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 4. Check These Common Issues

#### Issue A: Authentication Loop
If protected pages are blank, the auth check might be failing.

**Solution**: Open browser in incognito mode or clear cookies:
- Chrome: Settings → Privacy → Clear browsing data → Cookies
- Or just use incognito: Ctrl+Shift+N

#### Issue B: API Connection
Frontend can't reach backend.

**Check**:
- Backend running on http://localhost:8000
- Frontend .env has: `NEXT_PUBLIC_API_URL=http://localhost:8000`

#### Issue C: JavaScript Error
A component is throwing an error.

**Check**: Browser console (F12) for red error messages

### 5. Test Each Page

**Home Page** (should work without auth):
- http://localhost:3000

**Login Page** (should work without auth):
- http://localhost:3000/login

**Dashboard** (requires auth):
- http://localhost:3000/dashboard
- Should redirect to login if not authenticated

## Expected Behavior

### Home Page (/)
- Should show landing page with "Manage Your Tasks Efficiently"
- Login and Sign Up buttons visible
- No authentication required

### Login Page (/login)
- Should show login form
- No authentication required

### Protected Pages (/dashboard, /tasks, /chat)
- Should redirect to /login if not authenticated
- Should show content if authenticated

## Debugging Commands

```bash
# Check if frontend is running
curl http://localhost:3000

# Check if backend is running
curl http://localhost:8000/health

# View frontend logs
cd frontend
npm run dev

# View backend logs
cd backend
uvicorn app.main:app --reload --port 8000
```

## If Still Blank

1. **Check browser console** - Look for errors
2. **Try different browser** - Rule out browser-specific issues
3. **Check network tab** - See if API calls are failing
4. **Disable browser extensions** - They might interfere
5. **Clear all cache** - Browser cache might be stale

## Most Likely Causes

1. ✅ **Build cache issue** - Fixed by clearing .next folder
2. ✅ **Auth loop** - Fixed by clearing cookies or using incognito
3. ✅ **Backend not running** - Start backend server
4. ⚠️ **JavaScript error** - Check browser console

## Quick Test

Open browser console (F12) and run:
```javascript
console.log('Test:', document.body.innerHTML.length);
```

If it shows a large number (>1000), HTML is there but hidden.
If it shows small number (<100), HTML is not rendering.
