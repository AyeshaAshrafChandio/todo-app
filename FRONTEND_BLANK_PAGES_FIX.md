# URGENT: Frontend Blank Pages - Troubleshooting Guide

## Issue
All frontend pages are showing blank in the browser.

## Immediate Diagnostic Steps

### Step 1: Check Browser Console
1. Open your browser to `http://localhost:3000`
2. Press **F12** to open DevTools
3. Go to **Console** tab
4. Look for any red error messages
5. **Take a screenshot** or copy the error messages

### Step 2: Check Network Tab
1. In DevTools, go to **Network** tab
2. Refresh the page (Ctrl+R)
3. Look for:
   - Failed requests (red status codes)
   - 404 errors
   - JavaScript files not loading
   - CSS files not loading

### Step 3: Check if JavaScript is Loading
1. In Network tab, filter by **JS**
2. Verify these files are loading:
   - `main-app.js`
   - `webpack.js`
   - `app/layout.js`
   - `app/page.js`

### Step 4: Check for Hydration Errors
Look in the console for messages like:
- "Hydration failed"
- "Text content does not match"
- "Expected server HTML to contain"

## Common Causes & Solutions

### Cause 1: API Call Failing on Mount
**Symptom**: AuthContext tries to call `/api/auth/me` and fails

**Solution**: Temporarily disable the API call
1. Open browser console
2. Clear localStorage: `localStorage.clear()`
3. Refresh the page

### Cause 2: JavaScript Not Loading
**Symptom**: No JavaScript files in Network tab

**Solution**: Restart the dev server
```bash
cd frontend
npm run dev
```

### Cause 3: Build Cache Issues
**Symptom**: Old cached files causing conflicts

**Solution**: Clear Next.js cache
```bash
cd frontend
rm -rf .next
npm run dev
```

### Cause 4: CSS Not Loading
**Symptom**: Page has content but no styling

**Solution**: Check if Tailwind CSS is configured correctly

## Quick Fix to Test

Create a simple test page to verify Next.js is working:

1. Create `frontend/src/app/test/page.tsx`:
```tsx
export default function TestPage() {
  return (
    <div style={{ padding: '20px', backgroundColor: 'lightblue' }}>
      <h1>Test Page</h1>
      <p>If you can see this, Next.js is working!</p>
    </div>
  );
}
```

2. Navigate to `http://localhost:3000/test`
3. If this page shows, the issue is in the main pages

## What to Report Back

Please provide:
1. **Browser console errors** (screenshot or text)
2. **Network tab status** (any failed requests?)
3. **Test page result** (does /test work?)
4. **Browser and version** (Chrome 120, Firefox 121, etc.)

## Temporary Workaround

If the issue is with AuthContext, temporarily bypass it:

1. Edit `frontend/src/components/Providers.tsx`
2. Comment out AuthProvider:
```tsx
export function Providers({ children }: ProvidersProps) {
  return (
    // <AuthProvider>
      {children}
    // </AuthProvider>
  );
}
```

3. Refresh browser
4. If pages show now, the issue is in AuthContext

## Next Steps

Once you provide the console errors, I can:
1. Identify the exact cause
2. Provide a targeted fix
3. Ensure all pages render correctly

**Please check your browser console and report back what errors you see!**
