# Testing Guide for Foundational Components

## Quick Verification

### 1. Check All Files Exist

Run this command to verify all files were created:

```bash
cd C:\Users\Ali Haider\hakathon2\phase2\frontend

# Check utilities
ls src/lib/utils/validation.ts
ls src/lib/utils/errors.ts
ls src/lib/utils/format.ts
ls src/lib/utils/index.ts

# Check auth
ls src/lib/auth/token.ts
ls src/lib/auth/session.ts
ls src/lib/auth/index.ts

# Check middleware
ls src/middleware.ts

# Check UI components
ls src/components/ui/Modal.tsx
ls src/components/ui/EmptyState.tsx
ls src/components/ui/index.ts
```

### 2. Test Validation Utilities

Create a test file: `src/test-validation.ts`

```typescript
import {
  validateEmail,
  validatePassword,
  validateTaskTitle,
} from './lib/utils/validation';

// Test email validation
console.log('Valid email:', validateEmail('user@example.com'));
console.log('Invalid email:', validateEmail('invalid-email'));

// Test password validation
console.log('Valid password:', validatePassword('Password123'));
console.log('Weak password:', validatePassword('weak'));

// Test task title validation
console.log('Valid title:', validateTaskTitle('My Task'));
console.log('Short title:', validateTaskTitle('ab'));
```

Run: `npx ts-node src/test-validation.ts`

### 3. Test Token Management

Create a test file: `src/test-token.ts`

```typescript
import {
  setToken,
  getToken,
  hasValidToken,
  clearAuth,
} from './lib/auth/token';

// Test token storage
setToken('test-token-123');
console.log('Token stored:', getToken());

// Test token validation
console.log('Has valid token:', hasValidToken());

// Test clear auth
clearAuth();
console.log('Token after clear:', getToken());
```

### 4. Test Modal Component

Add to any page (e.g., `src/app/page.tsx`):

```typescript
'use client';

import { useState } from 'react';
import { Modal, ModalBody, ModalFooter } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';

export default function TestModal() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="p-8">
      <Button onClick={() => setIsOpen(true)}>Open Modal</Button>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Test Modal"
      >
        <ModalBody>
          <p>This is a test modal.</p>
        </ModalBody>
        <ModalFooter>
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            Close
          </Button>
        </ModalFooter>
      </Modal>
    </div>
  );
}
```

### 5. Test EmptyState Component

Add to any page:

```typescript
import { EmptyState, EmptyStateIcons } from '@/components/ui/EmptyState';

export default function TestEmptyState() {
  return (
    <div className="p-8">
      <EmptyState
        icon={<EmptyStateIcons.NoTasks />}
        title="No tasks yet"
        description="Create your first task to get started"
        action={{
          label: 'Create Task',
          onClick: () => alert('Create task clicked'),
        }}
      />
    </div>
  );
}
```

### 6. Test Middleware

1. Start the dev server: `npm run dev`
2. Navigate to `http://localhost:3000/dashboard` (should redirect to `/login` if not authenticated)
3. Navigate to `http://localhost:3000/login` after logging in (should redirect to `/dashboard`)

### 7. Test Error Handling

Create a test file: `src/test-errors.ts`

```typescript
import {
  getErrorMessage,
  isAuthError,
  formatValidationErrors,
} from './lib/utils/errors';
import { ApiError } from './lib/api/client';

// Test error message extraction
const error1 = new Error('Test error');
console.log('Error message:', getErrorMessage(error1));

// Test auth error detection
const authError = new ApiError(401, 'Unauthorized', {
  detail: 'Token expired',
});
console.log('Is auth error:', isAuthError(authError));

// Test validation error formatting
const validationError = new ApiError(422, 'Validation Error', {
  detail: [
    { loc: ['body', 'email'], msg: 'Invalid email' },
    { loc: ['body', 'password'], msg: 'Password too short' },
  ],
});
console.log('Validation errors:', formatValidationErrors(validationError));
```

### 8. Integration Test

Create a complete form test: `src/app/test-form/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import {
  validateEmail,
  validatePassword,
  getErrorMessage,
} from '@/lib/utils';

export default function TestForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: Record<string, string> = {};

    const emailResult = validateEmail(email);
    if (!emailResult.isValid) {
      newErrors.email = emailResult.error || 'Invalid email';
    }

    const passwordResult = validatePassword(password);
    if (!passwordResult.isValid) {
      newErrors.password = passwordResult.error || 'Invalid password';
    }

    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0) {
      alert('Form is valid!');
    }
  };

  return (
    <div className="max-w-md mx-auto p-8">
      <h1 className="text-2xl font-bold mb-6">Test Form</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <Input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter email"
          />
          {errors.email && (
            <p className="text-red-600 text-sm mt-1">{errors.email}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Password</label>
          <Input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter password"
          />
          {errors.password && (
            <p className="text-red-600 text-sm mt-1">{errors.password}</p>
          )}
        </div>

        <Button type="submit">Submit</Button>
      </form>
    </div>
  );
}
```

## Expected Results

### Validation
- ✓ Email validation rejects invalid formats
- ✓ Password validation enforces strength requirements
- ✓ Task title validation enforces length constraints

### Token Management
- ✓ Tokens are stored in localStorage
- ✓ Token validation checks expiration
- ✓ Clear auth removes all auth data

### Session Management
- ✓ Sessions are created with token and user data
- ✓ Session validation checks token expiration
- ✓ Destroy session clears all data

### Middleware
- ✓ Unauthenticated users redirected to /login
- ✓ Authenticated users redirected away from /login
- ✓ Protected routes require authentication

### UI Components
- ✓ Modal opens/closes correctly
- ✓ Modal traps focus
- ✓ Modal closes on Escape key
- ✓ EmptyState displays icon, title, description, and action
- ✓ EmptyState action button triggers onClick

### Error Handling
- ✓ Error messages extracted correctly
- ✓ Auth errors detected (401/403)
- ✓ Validation errors formatted correctly
- ✓ Network errors detected

## Common Issues and Solutions

### Issue: Modal not closing on overlay click
**Solution**: Ensure `closeOnOverlayClick={true}` is set (default is true)

### Issue: Validation not working
**Solution**: Check that you're importing from `@/lib/utils` or `@/lib/utils/validation`

### Issue: Token not persisting
**Solution**: Ensure you're using `setToken()` from `@/lib/auth/token` and not directly accessing localStorage

### Issue: Middleware not redirecting
**Solution**: Check that the auth token is stored in cookies (middleware reads from cookies, not localStorage)

### Issue: TypeScript errors in node_modules
**Solution**: These are normal Next.js type definition issues and don't affect the foundational components

## Performance Checklist

- [ ] Validation functions are fast (< 1ms)
- [ ] Token operations are synchronous
- [ ] Modal animations are smooth (60fps)
- [ ] EmptyState renders without layout shift
- [ ] Error handling doesn't block UI

## Accessibility Checklist

- [ ] Modal has proper ARIA labels
- [ ] Modal traps focus correctly
- [ ] Modal closes on Escape key
- [ ] EmptyState has ARIA live region
- [ ] All interactive elements are keyboard accessible

## Security Checklist

- [ ] Tokens are validated before use
- [ ] Expired tokens are rejected
- [ ] Auth errors clear tokens
- [ ] Middleware protects routes
- [ ] No sensitive data in error messages

## Next Steps

1. **Replace existing implementations** - Use the new Modal and EmptyState components throughout the app
2. **Add validation to forms** - Use validation utilities in all form components
3. **Standardize error handling** - Use error utilities for consistent error messages
4. **Update middleware** - Consider using httpOnly cookies instead of localStorage for tokens
5. **Add tests** - Write unit tests for utilities and integration tests for components
