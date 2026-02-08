# 🔧 SIGNIN ERROR FIX GUIDE

## Issue: "API Error: 404 Not Found" when signing in

### Quick Diagnosis Steps

1. **Check if backend is running:**
   ```bash
   # Windows
   netstat -ano | findstr :8000

   # Should show: TCP 127.0.0.1:8000 ... LISTENING
   ```

2. **Verify you have an account:**
   - You need to **signup first** before you can signin
   - Go to http://localhost:3000/register
   - Create an account with email and password

3. **Check browser console:**
   - Open browser DevTools (F12)
   - Go to Console tab
   - Look for the actual error message
   - Check Network tab for the failed request

### Common Causes & Solutions

#### Cause 1: No Account Created Yet ⚠️
**Symptom:** Getting 401 or 404 when trying to signin

**Solution:**
1. Go to http://localhost:3000/register
2. Create a new account:
   - Email: your-email@example.com
   - Password: SecurePass123 (must have uppercase, lowercase, digit)
   - Confirm Password: SecurePass123
3. Click "Create Account"
4. You'll be automatically logged in and redirected to dashboard

#### Cause 2: Backend Not Running ⚠️
**Symptom:** "Network error" or "Failed to fetch"

**Solution:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

#### Cause 3: Wrong Credentials ⚠️
**Symptom:** "Invalid email or password"

**Solution:**
- Make sure you're using the correct email and password
- Password is case-sensitive
- Try resetting by creating a new account

#### Cause 4: Database Not Initialized ⚠️
**Symptom:** "500 Internal Server Error"

**Solution:**
```bash
cd backend
python -c "from app.database.connection import init_db; init_db()"
```

#### Cause 5: CORS Issue ⚠️
**Symptom:** CORS error in browser console

**Solution:**
- Check backend/.env has: `CORS_ORIGINS=http://localhost:3000`
- Restart backend after changing .env

### Step-by-Step Fix

1. **Start Backend:**
   ```bash
   cd backend
   python -c "from app.database.connection import init_db; init_db()"
   uvicorn app.main:app --reload --port 8000
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Create Account:**
   - Navigate to: http://localhost:3000/register
   - Fill in:
     - Email: test@example.com
     - Password: TestPass123
     - Confirm Password: TestPass123
   - Click "Create Account"

4. **Test Signin:**
   - Navigate to: http://localhost:3000/login
   - Enter same credentials
   - Click "Sign In"
   - Should redirect to dashboard

### Verify Backend is Working

Test the signin endpoint directly:
```bash
# First, signup a user
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'

# Then, signin
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```

Expected response:
```json
{
  "user": {
    "id": "...",
    "email": "test@example.com",
    "created_at": "..."
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "..."
}
```

### Check Frontend Configuration

Verify frontend/.env:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=j-cgloynfj_XyhfeROGyecnUbArVlx4RtpoafbXfkz8
BETTER_AUTH_URL=http://localhost:3003
```

### Still Not Working?

1. **Clear browser cache:**
   - Press Ctrl+Shift+Delete
   - Clear cached images and files
   - Hard reload: Ctrl+Shift+R

2. **Check browser console:**
   - Open DevTools (F12)
   - Look for actual error message
   - Check Network tab for failed requests

3. **Restart both servers:**
   - Stop backend (Ctrl+C)
   - Stop frontend (Ctrl+C)
   - Start backend again
   - Start frontend again

4. **Delete database and start fresh:**
   ```bash
   cd backend
   rm todo_dev.db  # Delete SQLite database
   python -c "from app.database.connection import init_db; init_db()"
   uvicorn app.main:app --reload --port 8000
   ```

### Error Messages Explained

- **"API Error: 404 Not Found"** → Backend not running or wrong URL
- **"Invalid email or password"** → Wrong credentials or user doesn't exist
- **"Email already registered"** → User already exists, try signin instead
- **"Network error"** → Backend not running or CORS issue
- **"Failed to fetch"** → Backend not accessible

### Quick Test

Run this to verify everything is working:
```bash
cd backend
python -c "
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test signup
print('Testing signup...')
response = client.post('/api/auth/signup', json={
    'email': 'quicktest@example.com',
    'password': 'TestPass123'
})
print(f'Signup: {response.status_code}')

# Test signin
print('Testing signin...')
response = client.post('/api/auth/signin', json={
    'email': 'quicktest@example.com',
    'password': 'TestPass123'
})
print(f'Signin: {response.status_code}')

if response.status_code == 200:
    print('✅ Everything is working!')
else:
    print(f'❌ Error: {response.text}')
"
```

---

**Most Common Solution:** You need to **signup first** before you can signin!
