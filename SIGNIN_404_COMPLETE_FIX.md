# 🔴 SIGNIN 404 ERROR - COMPLETE FIX

## Issue
You're getting "API Error: 404 Not Found" when trying to sign in because the backend server is running but the auth routes aren't loaded.

## Root Cause
The backend server needs to be restarted to load the auth routes properly.

---

## ✅ COMPLETE FIX (Step-by-Step)

### Step 1: Stop Backend Server
1. Find the terminal window where backend is running
2. Press `Ctrl+C` to stop it
3. Wait for it to fully stop

### Step 2: Restart Backend Server
```bash
cd C:\Users\Ali Haider\hakathon2\phase2\backend
uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['C:\\Users\\Ali Haider\\hakathon2\\phase2\\backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
Starting up: Initializing database...
Database initialized successfully
INFO:     Application startup complete.
```

### Step 3: Verify Auth Routes are Loaded
Open a new terminal and run:
```bash
curl http://localhost:8000/api/auth/signin -X POST -H "Content-Type: application/json" -d "{\"email\":\"test\",\"password\":\"test\"}"
```

**Expected Response:**
```json
{"detail":"Invalid email or password"}
```

**NOT:** `{"detail":"Not Found"}`

If you get "Invalid email or password", the routes are working! ✅

### Step 4: Create an Account
1. Go to http://localhost:3000/register
2. Fill in:
   - **Email:** test@example.com
   - **Password:** TestPass123
   - **Confirm Password:** TestPass123
3. Click "Create Account"
4. You should be redirected to dashboard

### Step 5: Test Signin
1. Logout (if logged in)
2. Go to http://localhost:3000/login
3. Enter:
   - **Email:** test@example.com
   - **Password:** TestPass123
4. Click "Sign In"
5. Should redirect to dashboard ✅

---

## Alternative: Complete Fresh Start

If the above doesn't work, do a complete fresh start:

### 1. Stop Everything
- Stop backend (Ctrl+C)
- Stop frontend (Ctrl+C)

### 2. Clean Database
```bash
cd C:\Users\Ali Haider\hakathon2\phase2\backend
del todo_dev.db
```

### 3. Initialize Database
```bash
python -c "from app.database.connection import init_db; init_db()"
```

### 4. Start Backend
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Start Frontend (New Terminal)
```bash
cd C:\Users\Ali Haider\hakathon2\phase2\frontend
npm run dev
```

### 6. Test Complete Flow
1. Navigate to http://localhost:3000/register
2. Create account with:
   - Email: myemail@example.com
   - Password: MySecurePass123
3. Should auto-login and redirect to dashboard
4. Logout
5. Go to http://localhost:3000/login
6. Login with same credentials
7. Should work! ✅

---

## Verification Commands

### Check Backend is Running
```bash
netstat -ano | findstr :8000
```
Should show: `TCP 127.0.0.1:8000 ... LISTENING`

### Test Signup Endpoint
```bash
curl -X POST http://localhost:8000/api/auth/signup ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"verify@example.com\",\"password\":\"TestPass123\"}"
```

Should return 201 with user data and token.

### Test Signin Endpoint
```bash
curl -X POST http://localhost:8000/api/auth/signin ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"verify@example.com\",\"password\":\"TestPass123\"}"
```

Should return 200 with user data and token.

---

## Common Mistakes

### ❌ Wrong: Using old terminal session
The backend might be running in a terminal that hasn't picked up code changes.

### ✅ Right: Stop and restart backend
Always stop (Ctrl+C) and restart the backend server after code changes.

### ❌ Wrong: Trying to signin without account
You must signup first before you can signin.

### ✅ Right: Signup → Signin
1. Create account at /register
2. Then login at /login

### ❌ Wrong: Wrong password format
Password must have: uppercase, lowercase, and digit (min 8 chars)

### ✅ Right: TestPass123
- Has uppercase: T, P
- Has lowercase: est, ass
- Has digit: 123
- Length: 11 chars ✅

---

## Still Not Working?

### Check Browser Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for actual error message
4. Go to Network tab
5. Click on failed request
6. Check Response tab

### Check Backend Logs
Look at the terminal where backend is running. Any errors?

### Try Different Browser
Sometimes browser cache causes issues. Try:
- Chrome Incognito mode
- Different browser
- Clear browser cache (Ctrl+Shift+Delete)

---

## Quick Test Script

Run this to verify everything is working:

```bash
cd C:\Users\Ali Haider\hakathon2\phase2\backend
python -c "
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print('=== Testing Auth Endpoints ===')
print()

# Test signup
print('1. Testing signup...')
response = client.post('/api/auth/signup', json={
    'email': 'quicktest@example.com',
    'password': 'TestPass123'
})
print(f'   Status: {response.status_code}')
if response.status_code == 201:
    print('   ✅ Signup working!')
    token = response.json()['token']

    # Test signin
    print()
    print('2. Testing signin...')
    response = client.post('/api/auth/signin', json={
        'email': 'quicktest@example.com',
        'password': 'TestPass123'
    })
    print(f'   Status: {response.status_code}')
    if response.status_code == 200:
        print('   ✅ Signin working!')
        print()
        print('=== ALL TESTS PASSED ===')
    else:
        print(f'   ❌ Signin failed: {response.text}')
else:
    print(f'   ❌ Signup failed: {response.text}')
"
```

---

## Summary

**The fix is simple: Restart your backend server.**

1. Stop backend (Ctrl+C)
2. Start backend: `uvicorn app.main:app --reload --port 8000`
3. Create account at /register
4. Login at /login

**That's it!** ✅
