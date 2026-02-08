# Frontend Quick Start Guide

## Prerequisites
- Node.js 18+ installed
- Backend API running on `http://localhost:8000`
- npm, yarn, or pnpm package manager

## Installation Steps

### 1. Navigate to Frontend Directory
```bash
cd C:\Users\Ali Haider\hakathon2\phase2\frontend
```

### 2. Install Dependencies
```bash
npm install
```

This will install:
- Next.js 15.0.0
- React 19.0.0
- TypeScript 5.0.0
- Tailwind CSS 3.4.0
- Better Auth 1.0.0
- All development dependencies

### 3. Configure Environment Variables
```bash
# Copy the example file
cp .env.local.example .env.local

# Edit .env.local with your settings
```

Required environment variables:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-here-change-in-production
BETTER_AUTH_URL=http://localhost:3000
NODE_ENV=development
```

### 4. Start Development Server
```bash
npm run dev
```

The application will be available at: `http://localhost:3000`

### 5. Verify Installation

Open your browser and navigate to `http://localhost:3000`. You should see:
- Landing page with "Manage Your Tasks Efficiently" heading
- Login and Sign Up buttons in the header
- Three feature cards (Task Management, Team Collaboration, Secure & Private)

## Available Scripts

```bash
# Development server with hot reload
npm run dev

# Production build
npm run build

# Start production server
npm start

# Run ESLint
npm run lint
```

## Testing the Application

### 1. Register a New User
1. Click "Sign Up" or navigate to `/register`
2. Fill in the registration form:
   - Name (optional)
   - Email (required)
   - Password (minimum 8 characters)
   - Confirm Password
3. Click "Create Account"
4. You'll be automatically logged in and redirected to `/dashboard`

### 2. Login
1. Click "Login" or navigate to `/login`
2. Enter your email and password
3. Click "Sign In"
4. You'll be redirected to `/dashboard`

### 3. Dashboard
After login, you'll see:
- Statistics cards (Total Tasks, Pending, In Progress, Completed)
- Recent tasks list
- Your teams overview
- Navigation menu (Dashboard, Tasks, Teams)

### 4. Create a Task
1. Navigate to "Tasks" from the menu
2. Click "Create Task" button
3. Fill in the form:
   - Title (required)
   - Description (optional)
   - Priority (low, medium, high)
   - Status (pending, in_progress, completed)
4. Click "Create Task"
5. Task appears in the list

### 5. Manage Tasks
- Filter tasks by status using tabs (All, Pending, In Progress, Completed)
- Change task status using the dropdown
- Delete tasks using the "Delete" button

### 6. Create a Team
1. Navigate to "Teams" from the menu
2. Click "Create Team" button
3. Fill in the form:
   - Team Name (required)
   - Description (optional)
4. Click "Create Team"
5. Team appears in the grid

### 7. Logout
Click "Logout" button in the header to sign out

## Troubleshooting

### Issue: npm install fails
**Solution**:
- Ensure Node.js 18+ is installed: `node --version`
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`, then reinstall

### Issue: Port 3000 already in use
**Solution**:
```bash
# Use a different port
PORT=3001 npm run dev
```

### Issue: API calls fail with CORS errors
**Solution**:
- Ensure backend is running on `http://localhost:8000`
- Check backend CORS configuration allows `http://localhost:3000`
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

### Issue: "Cannot find module" errors
**Solution**:
- Ensure all dependencies are installed: `npm install`
- Check TypeScript path aliases in `tsconfig.json`
- Restart the development server

### Issue: Authentication not working
**Solution**:
- Check backend API is running and accessible
- Verify JWT token is being stored in localStorage (check browser DevTools)
- Check network tab for API request/response
- Ensure `NEXT_PUBLIC_API_URL` is correct

### Issue: Styles not loading
**Solution**:
- Ensure Tailwind CSS is configured correctly
- Check `tailwind.config.js` content paths
- Restart development server
- Clear `.next` cache: `rm -rf .next`

## Project Structure Overview

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # React components
│   ├── lib/             # Utilities and API clients
│   └── hooks/           # Custom React hooks
├── public/              # Static assets
└── Configuration files
```

## Key Features

### Authentication
- JWT-based authentication
- Automatic token management
- Protected routes
- Session persistence

### Task Management
- CRUD operations
- Status tracking
- Priority levels
- Filtering

### Team Collaboration
- Team creation
- Team management
- Member roles (API ready)

### UI/UX
- Responsive design
- Accessible components
- Loading states
- Error handling

## Next Steps

1. **Verify Backend Connection**: Ensure backend API is running and accessible
2. **Test User Registration**: Create a test user account
3. **Test Task Creation**: Create and manage tasks
4. **Test Team Creation**: Create and manage teams
5. **Explore UI Components**: Check all pages and components

## Development Tips

### Hot Reload
The development server supports hot reload. Changes to files will automatically refresh the browser.

### TypeScript
All files use TypeScript. The compiler will catch type errors during development.

### Tailwind CSS
Use Tailwind utility classes for styling. Custom classes are defined in `globals.css`.

### API Client
All API calls use the centralized client in `src/lib/api/client.ts` with automatic JWT token injection.

### Custom Hooks
Use the provided hooks for state management:
- `useAuth()` - Authentication state
- `useTasks()` - Task management
- `useTeams()` - Team management

## Support

For issues or questions:
1. Check the main README.md for detailed documentation
2. Review the implementation summary in FRONTEND_SETUP_COMPLETE.md
3. Check browser console for errors
4. Check network tab for API issues

## Production Deployment

### Build for Production
```bash
npm run build
```

### Start Production Server
```bash
npm start
```

### Environment Variables for Production
Update `.env.local` with production values:
- `NEXT_PUBLIC_API_URL`: Your production API URL
- `BETTER_AUTH_SECRET`: Strong secret key
- `BETTER_AUTH_URL`: Your production frontend URL

### Deployment Platforms
The application can be deployed to:
- Vercel (recommended for Next.js)
- Netlify
- AWS Amplify
- Docker container
- Any Node.js hosting platform

## Success Checklist

- [ ] Dependencies installed successfully
- [ ] Environment variables configured
- [ ] Development server running
- [ ] Landing page loads correctly
- [ ] User registration works
- [ ] User login works
- [ ] Dashboard displays correctly
- [ ] Tasks can be created and managed
- [ ] Teams can be created and managed
- [ ] Logout works correctly

If all items are checked, your frontend is ready for Phase 8 implementation!
