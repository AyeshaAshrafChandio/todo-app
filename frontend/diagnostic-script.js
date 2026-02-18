// DIAGNOSTIC SCRIPT - Run this in browser console (F12)
// Copy and paste this entire script into the console and press Enter

console.clear();
console.log('═══════════════════════════════════════════════════════════');
console.log('🔍 AUTHENTICATION DIAGNOSTIC REPORT');
console.log('═══════════════════════════════════════════════════════════');
console.log('');

// 1. Check localStorage
console.log('1️⃣ LOCALSTORAGE CHECK:');
const localToken = localStorage.getItem('auth_token');
const localUser = localStorage.getItem('auth_user');
console.log('   auth_token:', localToken ? `EXISTS (${localToken.substring(0, 30)}...)` : '❌ NOT FOUND');
console.log('   auth_user:', localUser ? `EXISTS (${localUser.substring(0, 50)}...)` : '❌ NOT FOUND');
console.log('');

// 2. Check cookies
console.log('2️⃣ COOKIES CHECK:');
console.log('   All cookies:', document.cookie || '❌ NO COOKIES');
const cookieToken = document.cookie.split('; ').find(row => row.startsWith('auth_token='));
console.log('   auth_token cookie:', cookieToken ? `EXISTS (${cookieToken.substring(0, 50)}...)` : '❌ NOT FOUND');
console.log('');

// 3. Check API URL
console.log('3️⃣ API CONFIGURATION:');
console.log('   NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL || 'NOT SET (using default)');
console.log('');

// 4. Test backend connectivity
console.log('4️⃣ BACKEND CONNECTIVITY TEST:');
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
console.log('   Testing:', apiUrl);

fetch(apiUrl + '/')
  .then(res => res.json())
  .then(data => {
    console.log('   ✅ Backend is reachable');
    console.log('   Response:', data);
  })
  .catch(err => {
    console.log('   ❌ Backend is NOT reachable');
    console.log('   Error:', err.message);
  });

// 5. Test auth endpoint
console.log('');
console.log('5️⃣ AUTH ENDPOINT TEST:');
const token = localToken || (cookieToken ? cookieToken.split('=')[1] : null);
if (token) {
  console.log('   Token found, testing /api/auth/me...');
  fetch(apiUrl + '/api/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
    .then(res => {
      console.log('   Status:', res.status, res.statusText);
      return res.json();
    })
    .then(data => {
      if (data.detail) {
        console.log('   ❌ Auth failed:', data.detail);
      } else {
        console.log('   ✅ Auth successful');
        console.log('   User:', data);
      }
    })
    .catch(err => {
      console.log('   ❌ Request failed:', err.message);
    });
} else {
  console.log('   ❌ No token found - cannot test auth endpoint');
}

console.log('');
console.log('═══════════════════════════════════════════════════════════');
console.log('📋 COPY THE OUTPUT ABOVE AND SHARE IT');
console.log('═══════════════════════════════════════════════════════════');
