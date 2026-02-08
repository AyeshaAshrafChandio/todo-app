# Todo App Frontend

Modern Next.js 16+ frontend application for task management with team collaboration.

## Technology Stack

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth with JWT
- **State Management**: React Hooks
- **API Client**: Fetch API with custom wrapper

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (auth)/            # Authentication pages (login, register)
│   │   ├── (protected)/       # Protected pages (dashboard, tasks, teams)
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── auth/             # Authentication components
│   │   ├── tasks/            # Task components
│   │   ├── teams/            # Team components
│   │   ├── shared/           # Shared components
│   │   └── ui/               # UI components (Button, Input, Card)
│   ├── lib/                   # Utilities and API clients
│   │   ├── api/              # API client functions
│   │   │   ├── client.ts     # Base API client with JWT handling
│   │   │   ├── auth.ts       # Authentication API
│   │   │   ├── tasks.ts      # Tasks API
│   │   │   └── teams.ts      # Teams API
│   │   ├── types/            # TypeScript type definitions
│   │   │   ├── auth.ts       # Auth types
│   │   │   ├── task.ts       # Task types
│   │   │   └── team.ts       # Team types
│   │   └── utils.ts          # Utility functions
│   └── hooks/                 # Custom React hooks
│       ├── useAuth.ts        # Authentication hook
│       ├── useTasks.ts       # Tasks management hook
│       └── useTeams.ts       # Teams management hook
├── public/                    # Static assets
├── .env.local.example        # Environment variables template
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript configuration
├── tailwind.config.js        # Tailwind CSS configuration
└── next.config.js            # Next.js configuration
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend API running on `http://localhost:8000` (or configured URL)

### Installation

1. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

2. Create environment file:
```bash
cp .env.local.example .env.local
```

3. Configure environment variables in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

### Development

Run the development server:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

Build for production:
```bash
npm run build
npm start
```

## Features

### Authentication
- User registration with email and password
- User login with JWT token authentication
- Automatic token refresh and session management
- Protected routes with authentication middleware

### Task Management
- Create, read, update, and delete tasks
- Task status tracking (pending, in progress, completed)
- Task priority levels (low, medium, high)
- Task filtering by status
- Due date management

### Team Collaboration
- Create and manage teams
- Team member management with role-based access control
- Team task assignment
- Shared task views

### UI/UX
- Responsive design (mobile-first)
- Accessible components (WCAG 2.1 AA compliant)
- Loading states and error handling
- Toast notifications for user feedback

## Architecture

### Server vs Client Components

**Server Components** (default):
- Root layout
- Static pages
- SEO-critical content

**Client Components** ('use client'):
- Authentication pages (login, register)
- Protected pages (dashboard, tasks, teams)
- Interactive UI components
- Components using React hooks

### API Client

The API client (`src/lib/api/client.ts`) provides:
- Automatic JWT token injection in headers
- Token storage in localStorage
- Automatic redirect to login on 401 errors
- Error handling and type safety

### Custom Hooks

- `useAuth`: Authentication state and operations
- `useTasks`: Task management with CRUD operations
- `useTeams`: Team management with CRUD operations

## Component Library

### UI Components

- **Button**: Reusable button with variants (primary, secondary, outline, danger)
- **Input**: Form input with label, error handling, and validation
- **Card**: Container component with header, body, and footer sections

### Usage Example

```tsx
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';

function MyComponent() {
  return (
    <Card>
      <CardHeader>
        <h2>Form Title</h2>
      </CardHeader>
      <CardBody>
        <Input label="Email" type="email" required />
        <Button variant="primary">Submit</Button>
      </CardBody>
    </Card>
  );
}
```

## API Integration

### Authentication Flow

1. User logs in → JWT token received
2. Token stored in localStorage
3. Token included in all API requests via Authorization header
4. Backend verifies token and returns user-specific data

### API Endpoints

All API calls go through the base client with automatic token handling:

```typescript
import { apiClient } from '@/lib/api/client';

// Example: Get tasks
const tasks = await apiClient<Task[]>('/api/tasks');

// Example: Create task
const newTask = await apiClient<Task>('/api/tasks', {
  method: 'POST',
  body: JSON.stringify({ title: 'New Task' }),
});
```

## Styling

### Tailwind CSS

The project uses Tailwind CSS for styling with a custom configuration:

- Custom color palette (primary colors)
- Responsive breakpoints (sm, md, lg, xl, 2xl)
- Utility classes for common patterns

### CSS Classes

Common utility classes:
- Layout: `flex`, `grid`, `container`, `mx-auto`
- Spacing: `p-4`, `m-2`, `space-x-4`, `gap-6`
- Typography: `text-lg`, `font-bold`, `text-gray-900`
- Colors: `bg-primary-600`, `text-white`, `border-gray-200`

## Best Practices

### TypeScript

- All components and functions are fully typed
- Type definitions in `src/lib/types/`
- No `any` types (use proper interfaces)

### Performance

- Server Components by default for better performance
- Client Components only when needed (interactivity, hooks)
- Image optimization with Next.js Image component
- Code splitting and lazy loading

### Accessibility

- Semantic HTML elements
- ARIA labels and roles
- Keyboard navigation support
- Focus management
- Color contrast compliance

### Security

- JWT tokens stored securely
- No sensitive data in client-side code
- CSRF protection
- Input validation and sanitization

## Troubleshooting

### Common Issues

**Issue**: API calls fail with CORS errors
**Solution**: Ensure backend has CORS configured for `http://localhost:3000`

**Issue**: Authentication not working
**Solution**: Check that `NEXT_PUBLIC_API_URL` is set correctly and backend is running

**Issue**: Token expired errors
**Solution**: Implement token refresh logic or re-login

## Testing

### Manual Testing Checklist

See `VALIDATION_CHECKLIST.md` for comprehensive testing procedures.

**Core Functionality**:
- [ ] User can sign up with valid email/password
- [ ] User can sign in with correct credentials
- [ ] User cannot access protected routes without authentication
- [ ] User can create, edit, and delete personal tasks
- [ ] User can create teams and invite members
- [ ] User can share tasks with specific permissions
- [ ] All forms validate input correctly
- [ ] Error messages are clear and helpful
- [ ] Loading states display during async operations
- [ ] Toast notifications appear for user actions

**Responsive Design**:
- [ ] Works on mobile (320px - 640px)
- [ ] Works on tablet (641px - 1024px)
- [ ] Works on desktop (1025px+)
- [ ] Touch targets minimum 44x44px
- [ ] No horizontal scrolling

**Accessibility**:
- [ ] Keyboard navigation works for all interactive elements
- [ ] Screen reader compatible
- [ ] Focus indicators visible
- [ ] Color contrast meets WCAG 2.1 AA standards

### Performance Testing

- [ ] Page load time < 2 seconds
- [ ] Time to Interactive (TTI) < 3 seconds
- [ ] First Contentful Paint (FCP) < 1.5 seconds
- [ ] Largest Contentful Paint (LCP) < 2.5 seconds
- [ ] Cumulative Layout Shift (CLS) < 0.1

## Deployment

### Build for Production

```bash
npm run build
```

This creates an optimized production build in the `.next` directory.

### Start Production Server

```bash
npm run start
```

### Environment Variables for Production

Ensure the following environment variables are set in your production environment:

```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
BETTER_AUTH_SECRET=your-production-secret-key
BETTER_AUTH_URL=https://your-frontend-domain.com
NODE_ENV=production
```

**Security Notes**:
- Never commit `.env.local` to version control
- Use strong, randomly generated secrets in production
- Rotate secrets regularly
- Use HTTPS in production

### Deployment Platforms

The application can be deployed to:

- **Vercel** (recommended for Next.js)
- **Netlify**
- **AWS Amplify**
- **Docker** (containerized deployment)

### Vercel Deployment

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Follow the prompts
4. Set environment variables in Vercel dashboard

## Security

### Best Practices Implemented

- JWT token verification on all API requests
- Input sanitization to prevent XSS attacks
- CSRF protection via Better Auth
- HTTP-only cookies for token storage
- Secure password hashing (backend)
- Rate limiting (backend)
- Content Security Policy headers

### Input Sanitization

All user input is sanitized using the `sanitize.ts` utility:

```typescript
import { sanitizeInput, sanitizeHtml } from '@/lib/utils/sanitize';

const cleanInput = sanitizeInput(userInput);
const cleanHtml = sanitizeHtml(htmlContent);
```

## Error Handling

### Global Error Boundary

The application includes a global error boundary that catches unhandled React errors:

- Displays user-friendly error message
- Provides "Reload Page" button
- Shows error details in development mode
- Logs errors to console for debugging

### API Error Handling

- **401 Unauthorized**: Automatic logout and redirect to signin
- **403 Forbidden**: Access denied message with explanation
- **404 Not Found**: Resource not found message
- **500 Server Error**: Generic error message with retry option

## Next Steps

1. ✅ Implement task detail page (`/tasks/[id]`)
2. ✅ Add team member management UI
3. ✅ Implement task sharing functionality
4. Add real-time updates with WebSockets
5. Implement notifications system
6. Add search and advanced filtering
7. Implement dark mode
8. Add unit and integration tests
9. Add end-to-end tests with Playwright
10. Implement analytics and monitoring

## Contributing

### Code Style

Follow the project's coding standards:
- Use TypeScript for all files
- Follow Next.js 15+ App Router conventions
- Use Tailwind CSS for styling (no inline styles)
- Write accessible, semantic HTML
- Add proper error handling
- Document complex logic with JSDoc comments
- Keep components small and focused (< 200 lines)

### Git Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit: `git commit -m "feat: add feature"`
3. Push to remote: `git push origin feature/your-feature`
4. Create pull request

### Commit Message Format

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

## Support

For issues and questions:
- Create an issue on GitHub
- Email: support@example.com
- Documentation: See `/docs` directory

## Acknowledgments

Built with:
- [Next.js](https://nextjs.org/)
- [React](https://react.dev/)
- [TypeScript](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Better Auth](https://better-auth.com/)

## License

Copyright 2026 Todo App. All rights reserved.
