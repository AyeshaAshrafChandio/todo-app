# Frontend Quickstart Guide

**Feature**: Frontend Full-Stack UI (004-frontend-fullstack-ui)
**Date**: 2026-02-05

## Overview

This guide provides step-by-step instructions for setting up and running the frontend application locally.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js**: Version 18.x or higher
- **npm**: Version 9.x or higher (comes with Node.js)
- **Git**: For version control
- **Backend API**: The backend must be running and accessible

**Check versions**:
```bash
node --version  # Should be v18.x or higher
npm --version   # Should be v9.x or higher
```

## Project Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Navigate to Frontend Directory

```bash
cd frontend
```

### 3. Install Dependencies

```bash
npm install
```

This will install all required packages including:
- Next.js 16+
- React 19+
- TypeScript 5.x
- Tailwind CSS 3.x
- Better Auth client SDK

**Expected output**: Dependencies installed successfully (may take 2-3 minutes)

## Environment Configuration

### 1. Create Environment File

Copy the example environment file:

```bash
cp .env.local.example .env.local
```

### 2. Configure Environment Variables

Edit `.env.local` and set the following variables:

```env
# Backend API URL (required)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth URL (required)
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000/api/auth

# Better Auth Secret (server-side only, required for JWT verification)
BETTER_AUTH_SECRET=your-secret-key-here

# Optional: Enable debug mode
NEXT_PUBLIC_DEBUG=false
```

**Important**:
- `NEXT_PUBLIC_*` variables are exposed to the browser
- `BETTER_AUTH_SECRET` is server-side only (not exposed to browser)
- Replace `your-secret-key-here` with the same secret used in the backend
- Ensure backend API is running at the specified URL

### 3. Verify Backend Connection

Before starting the frontend, ensure the backend is running:

```bash
curl http://localhost:8000/api/health
```

**Expected response**: `{"status": "ok"}`

If the backend is not running, start it first (see backend README).

## Development

### Start Development Server

```bash
npm run dev
```

**Expected output**:
```
> frontend@0.1.0 dev
> next dev

  ▲ Next.js 16.0.0
  - Local:        http://localhost:3000
  - Network:      http://192.168.1.x:3000

 ✓ Ready in 2.5s
```

### Access Application

Open your browser and navigate to:
```
http://localhost:3000
```

**Expected behavior**:
- Landing page redirects to `/login` (if not authenticated)
- Login page displays signup/signin forms
- After authentication, redirects to `/dashboard`

### Development Features

**Hot Reload**: Changes to code automatically refresh the browser

**Fast Refresh**: React components update without losing state

**TypeScript Checking**: Type errors shown in terminal and browser

**Tailwind CSS**: Styles update instantly

## Available Scripts

### Development

```bash
npm run dev
```
Starts development server on http://localhost:3000

### Build

```bash
npm run build
```
Creates optimized production build in `.next/` directory

**Expected output**:
```
Route (app)                              Size     First Load JS
┌ ○ /                                    1.2 kB         85.3 kB
├ ○ /login                               2.5 kB         87.6 kB
├ ○ /register                            2.5 kB         87.6 kB
└ ● /dashboard                           3.8 kB         89.9 kB
```

### Start Production Server

```bash
npm run start
```
Starts production server (requires `npm run build` first)

### Lint

```bash
npm run lint
```
Runs ESLint to check code quality

### Type Check

```bash
npm run type-check
```
Runs TypeScript compiler to check types (no output)

### Format

```bash
npm run format
```
Formats code using Prettier (if configured)

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── (auth)/         # Public routes (login, register)
│   │   ├── (protected)/    # Protected routes (dashboard, tasks, teams)
│   │   ├── layout.tsx      # Root layout
│   │   └── page.tsx        # Landing page
│   ├── components/         # React components
│   │   ├── auth/           # Authentication components
│   │   ├── tasks/          # Task components
│   │   ├── teams/          # Team components
│   │   ├── shared/         # Shared task components
│   │   ├── ui/             # UI primitives
│   │   └── layout/         # Layout components
│   ├── lib/                # Utilities and helpers
│   │   ├── api/            # API client
│   │   ├── auth/           # Auth utilities
│   │   ├── utils/          # General utilities
│   │   └── types/          # TypeScript types
│   └── hooks/              # Custom React hooks
├── public/                 # Static assets
├── .env.local              # Environment variables (not in git)
├── .env.local.example      # Environment variables template
├── next.config.js          # Next.js configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── tsconfig.json           # TypeScript configuration
└── package.json            # Dependencies and scripts
```

## Testing

### Run Unit Tests

```bash
npm test
```

Runs Jest tests for components and utilities

### Run E2E Tests

```bash
npm run test:e2e
```

Runs Playwright end-to-end tests

### Run Tests in Watch Mode

```bash
npm run test:watch
```

Runs tests and re-runs on file changes

## Common Issues & Solutions

### Issue: Port 3000 already in use

**Error**: `Port 3000 is already in use`

**Solution**: Kill the process using port 3000 or use a different port

```bash
# Kill process on port 3000 (macOS/Linux)
lsof -ti:3000 | xargs kill -9

# Kill process on port 3000 (Windows)
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use a different port
PORT=3001 npm run dev
```

### Issue: Backend connection refused

**Error**: `Failed to fetch` or `ECONNREFUSED`

**Solution**: Ensure backend is running and URL is correct

```bash
# Check backend is running
curl http://localhost:8000/api/health

# Verify NEXT_PUBLIC_API_URL in .env.local
cat .env.local | grep NEXT_PUBLIC_API_URL
```

### Issue: Authentication not working

**Error**: `401 Unauthorized` or `Invalid token`

**Solution**: Verify Better Auth configuration

1. Check `BETTER_AUTH_SECRET` matches backend
2. Clear browser cookies and localStorage
3. Restart both frontend and backend
4. Check browser console for errors

```bash
# Clear Next.js cache
rm -rf .next

# Restart development server
npm run dev
```

### Issue: TypeScript errors

**Error**: Type errors in terminal or browser

**Solution**: Ensure types are up to date

```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Run type check
npm run type-check
```

### Issue: Styles not loading

**Error**: Tailwind CSS styles not applied

**Solution**: Restart development server

```bash
# Stop server (Ctrl+C)
# Clear Next.js cache
rm -rf .next

# Restart
npm run dev
```

## Development Workflow

### 1. Create New Feature

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# Test locally
npm run dev

# Run tests
npm test

# Build to verify
npm run build
```

### 2. Code Quality Checks

```bash
# Lint code
npm run lint

# Type check
npm run type-check

# Format code
npm run format
```

### 3. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

## Deployment

### Build for Production

```bash
npm run build
```

### Environment Variables for Production

Ensure the following environment variables are set in your deployment platform:

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_BETTER_AUTH_URL=https://api.yourdomain.com/api/auth
BETTER_AUTH_SECRET=<production-secret>
```

### Deploy to Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Deploy to production
vercel --prod
```

### Deploy to Other Platforms

The application can be deployed to any platform that supports Next.js:
- Netlify
- AWS Amplify
- Google Cloud Run
- Docker container

See Next.js deployment documentation for platform-specific instructions.

## Browser Support

The application supports the latest 2 versions of:
- Chrome
- Firefox
- Safari
- Edge

**Minimum requirements**:
- JavaScript enabled
- Cookies enabled (for authentication)
- Modern CSS support (flexbox, grid)

## Performance Optimization

### Development

- Use Server Components by default
- Only use Client Components when needed
- Lazy load non-critical components
- Optimize images with Next.js Image component

### Production

- Enable compression (gzip/brotli)
- Use CDN for static assets
- Enable caching headers
- Monitor Core Web Vitals

## Security Considerations

### Development

- Never commit `.env.local` to git
- Use HTTPS in production
- Keep dependencies up to date
- Review security advisories

### Production

- Enable HTTPS only
- Set secure headers (CSP, HSTS)
- Implement rate limiting
- Monitor for vulnerabilities

## Getting Help

### Documentation

- Next.js: https://nextjs.org/docs
- React: https://react.dev
- Tailwind CSS: https://tailwindcss.com/docs
- TypeScript: https://www.typescriptlang.org/docs

### Project-Specific

- See `specs/004-frontend-fullstack-ui/` for detailed specifications
- Check `plan.md` for architecture decisions
- Review `data-model.md` for type definitions
- Consult `contracts/` for API documentation

### Troubleshooting

1. Check browser console for errors
2. Check terminal for build errors
3. Verify environment variables
4. Ensure backend is running
5. Clear cache and restart

## Next Steps

After setup is complete:

1. **Explore the application**: Navigate through all pages
2. **Review the code**: Understand component structure
3. **Run tests**: Ensure everything works
4. **Read specifications**: Understand requirements
5. **Start development**: Implement features

## Quick Reference

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm test` | Run unit tests |
| `npm run lint` | Lint code |
| `npm run type-check` | Check TypeScript types |

| URL | Description |
|-----|-------------|
| http://localhost:3000 | Frontend application |
| http://localhost:3000/login | Login page |
| http://localhost:3000/register | Signup page |
| http://localhost:3000/dashboard | Dashboard (requires auth) |
| http://localhost:8000 | Backend API |

| Environment Variable | Required | Description |
|---------------------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API base URL |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | Yes | Better Auth endpoint |
| `BETTER_AUTH_SECRET` | Yes | JWT secret (server-side) |
| `NEXT_PUBLIC_DEBUG` | No | Enable debug mode |

---

**Last Updated**: 2026-02-05
**Version**: 1.0.0
