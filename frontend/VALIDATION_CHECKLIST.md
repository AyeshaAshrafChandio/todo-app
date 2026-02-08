# Frontend Validation Checklist

This document provides a comprehensive testing checklist for the Todo App frontend before production deployment.

## Table of Contents

1. [Performance Testing](#performance-testing)
2. [Security Testing](#security-testing)
3. [Authentication Testing](#authentication-testing)
4. [Functional Testing](#functional-testing)
5. [UI/UX Testing](#ui-ux-testing)
6. [Accessibility Testing](#accessibility-testing)
7. [Browser Compatibility](#browser-compatibility)
8. [Error Handling](#error-handling)

---

## Performance Testing

### Page Load Performance

**Target**: All pages should load in < 2 seconds on 3G connection

- [ ] **Home Page (/)**: Load time < 2 seconds
- [ ] **Sign In Page (/signin)**: Load time < 2 seconds
- [ ] **Sign Up Page (/signup)**: Load time < 2 seconds
- [ ] **Dashboard (/dashboard)**: Load time < 2 seconds
- [ ] **Tasks Page (/dashboard/tasks)**: Load time < 2 seconds
- [ ] **Teams Page (/dashboard/teams)**: Load time < 2 seconds
- [ ] **Shared Tasks (/dashboard/shared)**: Load time < 2 seconds

### Core Web Vitals

**Targets**:
- First Contentful Paint (FCP): < 1.5 seconds
- Largest Contentful Paint (LCP): < 2.5 seconds
- Time to Interactive (TTI): < 3 seconds
- Cumulative Layout Shift (CLS): < 0.1
- First Input Delay (FID): < 100ms

**Test Each Page**:
- [ ] Home page meets all Core Web Vitals targets
- [ ] Dashboard meets all Core Web Vitals targets
- [ ] Tasks page meets all Core Web Vitals targets
- [ ] Teams page meets all Core Web Vitals targets

**Tools**:
- Chrome DevTools Lighthouse
- WebPageTest.org
- Google PageSpeed Insights

### Network Performance

- [ ] API requests complete in < 1 second (local network)
- [ ] API requests complete in < 3 seconds (3G network)
- [ ] Images are optimized and lazy-loaded
- [ ] No unnecessary API calls on page load
- [ ] API calls are properly cached where appropriate

---

## Security Testing

### JWT Token Handling

**Critical**: All authenticated API requests must include JWT token

- [ ] **Task API Calls**: Token included in Authorization header
  - GET /api/tasks
  - POST /api/tasks
  - PUT /api/tasks/{id}
  - DELETE /api/tasks/{id}

- [ ] **Team API Calls**: Token included in Authorization header
  - GET /api/teams
  - POST /api/teams
  - PUT /api/teams/{id}
  - DELETE /api/teams/{id}

- [ ] **Team Member API Calls**: Token included in Authorization header
  - GET /api/teams/{id}/members
  - POST /api/teams/{id}/members
  - DELETE /api/teams/{id}/members/{memberId}

- [ ] **Task Share API Calls**: Token included in Authorization header
  - GET /api/task-shares
  - POST /api/task-shares
  - DELETE /api/task-shares/{id}

**Verification Method**:
1. Open Chrome DevTools → Network tab
2. Perform action that triggers API call
3. Click on the request
4. Check Headers tab for: `Authorization: Bearer <token>`

### Input Sanitization

- [ ] Task titles are sanitized before display
- [ ] Task descriptions are sanitized before display
- [ ] Team names are sanitized before display
- [ ] User names are sanitized before display
- [ ] XSS attempts are blocked (test with `<script>alert('XSS')</script>`)
- [ ] HTML injection is prevented (test with `<img src=x onerror=alert(1)>`)

### Authentication Security

- [ ] Passwords are not visible in network requests
- [ ] JWT tokens are not logged to console in production
- [ ] Tokens are stored securely (HTTP-only cookies or secure storage)
- [ ] Sensitive data is not exposed in URLs
- [ ] CSRF protection is enabled

---

## Authentication Testing

### 401 Unauthorized Error Handling

**Expected Behavior**: User is logged out and redirected to sign-in page

**Test Scenarios**:

1. **Expired Token**:
   - [ ] Manually expire token in backend
   - [ ] Make any API request
   - [ ] Verify user is logged out
   - [ ] Verify redirect to /signin
   - [ ] Verify error message displayed

2. **Invalid Token**:
   - [ ] Manually modify token in storage
   - [ ] Make any API request
   - [ ] Verify user is logged out
   - [ ] Verify redirect to /signin

3. **Missing Token**:
   - [ ] Clear token from storage
   - [ ] Try to access protected route
   - [ ] Verify redirect to /signin

**Verification Steps**:
1. Sign in successfully
2. Trigger 401 error (use one of the scenarios above)
3. Confirm automatic logout
4. Confirm redirect to /signin with message
5. Confirm user can sign in again

### 403 Forbidden Error Handling

**Expected Behavior**: Access denied message displayed, user stays on current page

**Test Scenarios**:

1. **Insufficient Permissions - Team Actions**:
   - [ ] As Member, try to delete team
   - [ ] Verify 403 error caught
   - [ ] Verify "Access Denied" message displayed
   - [ ] Verify user stays on teams page

2. **Insufficient Permissions - Task Actions**:
   - [ ] Try to edit task shared with view-only permission
   - [ ] Verify 403 error caught
   - [ ] Verify "Access Denied" message displayed
   - [ ] Verify user stays on task page

3. **Insufficient Permissions - Member Management**:
   - [ ] As Member, try to add team members
   - [ ] Verify 403 error caught
   - [ ] Verify "Access Denied" message displayed

**Verification Steps**:
1. Create scenario with insufficient permissions
2. Attempt restricted action
3. Confirm 403 error is caught
4. Confirm clear error message displayed
5. Confirm user is NOT logged out
6. Confirm user can continue using app

---

## Functional Testing

### User Authentication Flow

**Sign Up**:
- [ ] User can sign up with valid email and password
- [ ] Email validation works (rejects invalid emails)
- [ ] Password validation works (minimum 8 chars, uppercase, lowercase, number)
- [ ] Password confirmation validation works
- [ ] Error messages are clear and helpful
- [ ] Success message displayed after signup
- [ ] User is redirected to dashboard after signup
- [ ] Duplicate email shows appropriate error

**Sign In**:
- [ ] User can sign in with correct credentials
- [ ] Invalid credentials show error message
- [ ] User is redirected to dashboard after signin
- [ ] JWT token is stored correctly
- [ ] User session persists on page refresh

**Sign Out**:
- [ ] User can sign out from dashboard
- [ ] Token is cleared from storage
- [ ] User is redirected to home page
- [ ] Protected routes are no longer accessible

### Personal Task Management

**Create Task**:
- [ ] User can create task with title only
- [ ] User can create task with title and description
- [ ] User can set priority (low, medium, high)
- [ ] User can set due date
- [ ] User can set status (pending, in_progress, completed)
- [ ] Form validation works (title required, min 3 chars)
- [ ] Success toast displayed after creation
- [ ] New task appears in task list immediately
- [ ] Task is persisted (survives page refresh)

**View Tasks**:
- [ ] User can view all personal tasks
- [ ] Tasks display correct information (title, description, priority, due date, status)
- [ ] Tasks are sorted correctly (by creation date, newest first)
- [ ] Empty state shown when no tasks exist
- [ ] Loading skeleton shown while fetching tasks

**Update Task**:
- [ ] User can edit task title
- [ ] User can edit task description
- [ ] User can change task priority
- [ ] User can change task status
- [ ] User can change task due date
- [ ] Changes are saved immediately
- [ ] Success toast displayed after update
- [ ] Updated task reflects changes in list

**Delete Task**:
- [ ] User can delete task
- [ ] Confirmation dialog shown before deletion
- [ ] Task is removed from list after deletion
- [ ] Success toast displayed after deletion
- [ ] Deletion is persisted (survives page refresh)

**Filter Tasks**:
- [ ] User can filter by status (all, pending, in_progress, completed)
- [ ] User can filter by priority (all, low, medium, high)
- [ ] Filters work correctly and show expected results
- [ ] Filter state persists during session

### Team Management

**Create Team**:
- [ ] User can create team with name and description
- [ ] Form validation works (name required, min 3 chars)
- [ ] Success toast displayed after creation
- [ ] New team appears in team list
- [ ] Creator is automatically set as Owner
- [ ] Team is persisted (survives page refresh)

**View Teams**:
- [ ] User can view all teams they belong to
- [ ] Teams display correct information (name, description, member count, role)
- [ ] Empty state shown when no teams exist
- [ ] Loading skeleton shown while fetching teams

**Update Team**:
- [ ] Owner can edit team name
- [ ] Owner can edit team description
- [ ] Admin can edit team details
- [ ] Member cannot edit team details (403 error)
- [ ] Changes are saved immediately
- [ ] Success toast displayed after update

**Delete Team**:
- [ ] Owner can delete team
- [ ] Admin cannot delete team (403 error)
- [ ] Member cannot delete team (403 error)
- [ ] Confirmation dialog shown before deletion
- [ ] Team is removed from list after deletion
- [ ] Success toast displayed after deletion

### Team Member Management

**Add Member**:
- [ ] Owner can add members by email
- [ ] Admin can add members by email
- [ ] Member cannot add members (403 error)
- [ ] Can assign role (admin or member) when adding
- [ ] Email validation works
- [ ] Error shown if user not found
- [ ] Error shown if user already a member
- [ ] Success toast displayed after adding
- [ ] New member appears in member list

**Update Member Role**:
- [ ] Owner can change member roles
- [ ] Admin can change member roles (except owner)
- [ ] Member cannot change roles (403 error)
- [ ] Owner role cannot be changed
- [ ] Changes are saved immediately
- [ ] Success toast displayed after update

**Remove Member**:
- [ ] Owner can remove members
- [ ] Admin can remove members (except owner)
- [ ] Member cannot remove members (403 error)
- [ ] Owner cannot be removed
- [ ] Confirmation dialog shown before removal
- [ ] Member is removed from list
- [ ] Success toast displayed after removal

### Team Task Management

**Create Team Task**:
- [ ] User can create task for team
- [ ] Task is associated with correct team
- [ ] All team members can see the task
- [ ] Task appears in team task list

**View Team Tasks**:
- [ ] User can view all tasks for a team
- [ ] Only team members can view team tasks
- [ ] Non-members get 403 error when trying to view

**Update Team Task**:
- [ ] Team members can update team tasks
- [ ] Non-members cannot update team tasks (403 error)
- [ ] Changes are visible to all team members

**Delete Team Task**:
- [ ] Task creator can delete team task
- [ ] Team owner can delete any team task
- [ ] Team admin can delete any team task
- [ ] Team member can only delete own tasks

### Task Sharing

**Share Task**:
- [ ] User can share personal task with another user
- [ ] Can specify permission level (view or edit)
- [ ] Email validation works
- [ ] Error shown if user not found
- [ ] Error shown if task already shared with user
- [ ] Success toast displayed after sharing
- [ ] Shared user receives access immediately

**View Shared Tasks**:
- [ ] User can view tasks shared with them
- [ ] Shared tasks show correct permission level
- [ ] Shared tasks show owner information
- [ ] Empty state shown when no shared tasks

**Edit Shared Task**:
- [ ] User with edit permission can modify task
- [ ] User with view permission cannot modify task (403 error)
- [ ] Changes are visible to task owner

**Unshare Task**:
- [ ] Task owner can revoke share access
- [ ] Confirmation dialog shown before unsharing
- [ ] User loses access immediately after unsharing
- [ ] Success toast displayed after unsharing

---

## UI/UX Testing

### Responsive Design

**Mobile (320px - 640px)**:
- [ ] All pages render correctly
- [ ] Navigation menu works (hamburger menu)
- [ ] Forms are usable (inputs not too small)
- [ ] Buttons are tappable (min 44x44px)
- [ ] Text is readable without zooming
- [ ] No horizontal scrolling
- [ ] Cards stack vertically
- [ ] Modals fit on screen

**Tablet (641px - 1024px)**:
- [ ] All pages render correctly
- [ ] Navigation adapts appropriately
- [ ] Forms are well-spaced
- [ ] Content uses available space efficiently
- [ ] No layout breaks

**Desktop (1025px+)**:
- [ ] All pages render correctly
- [ ] Sidebar navigation visible
- [ ] Content is centered and not too wide
- [ ] Multi-column layouts work correctly
- [ ] Hover states work on interactive elements

### Loading States

- [ ] Loading skeletons shown while fetching data
- [ ] Loading spinners shown during form submissions
- [ ] Disabled state shown on buttons during async operations
- [ ] Loading states don't cause layout shift
- [ ] Loading states have appropriate timeout (show error if > 30s)

### Toast Notifications

- [ ] Success toasts shown for successful actions (green)
- [ ] Error toasts shown for failed actions (red)
- [ ] Info toasts shown for informational messages (blue)
- [ ] Toasts auto-dismiss after 5 seconds
- [ ] Toasts can be manually dismissed
- [ ] Multiple toasts stack correctly
- [ ] Toast messages are clear and actionable

### Confirmation Dialogs

- [ ] Confirmation shown before deleting tasks
- [ ] Confirmation shown before deleting teams
- [ ] Confirmation shown before removing team members
- [ ] Confirmation shown before unsharing tasks
- [ ] Dialogs have clear "Confirm" and "Cancel" buttons
- [ ] Dialogs can be closed with Escape key
- [ ] Dialogs can be closed by clicking outside (optional)

### Form Validation

- [ ] Required fields show error when empty
- [ ] Email fields validate email format
- [ ] Password fields validate strength requirements
- [ ] Number fields validate numeric input
- [ ] Date fields validate date format
- [ ] Error messages appear below fields
- [ ] Error messages are clear and helpful
- [ ] Form cannot be submitted with validation errors
- [ ] Validation happens on blur and on submit

### Empty States

- [ ] Empty state shown when no tasks exist
- [ ] Empty state shown when no teams exist
- [ ] Empty state shown when no shared tasks exist
- [ ] Empty state shown when no team members exist
- [ ] Empty states have helpful message and call-to-action
- [ ] Empty states have appropriate icon/illustration

---

## Accessibility Testing

### Keyboard Navigation

- [ ] All interactive elements are keyboard accessible
- [ ] Tab order is logical and follows visual flow
- [ ] Focus indicators are visible on all elements
- [ ] Enter key activates buttons and links
- [ ] Escape key closes modals and dialogs
- [ ] Arrow keys navigate within lists and menus
- [ ] No keyboard traps (can always tab out)

### Screen Reader Compatibility

- [ ] All images have alt text
- [ ] All form inputs have labels
- [ ] All buttons have descriptive text or aria-label
- [ ] Page structure uses semantic HTML (header, nav, main, footer)
- [ ] Headings are in logical order (h1, h2, h3)
- [ ] ARIA labels used where appropriate
- [ ] Error messages are announced
- [ ] Loading states are announced

### Color Contrast

- [ ] Text meets WCAG AA contrast ratio (4.5:1 for normal text)
- [ ] Large text meets WCAG AA contrast ratio (3:1)
- [ ] Interactive elements have sufficient contrast
- [ ] Focus indicators have sufficient contrast
- [ ] Error messages have sufficient contrast

**Tools**:
- Chrome DevTools Lighthouse (Accessibility audit)
- WAVE Browser Extension
- axe DevTools Extension

### Focus Management

- [ ] Focus moves to modal when opened
- [ ] Focus returns to trigger element when modal closed
- [ ] Focus moves to error message when validation fails
- [ ] Focus moves to success message after form submission
- [ ] Skip to main content link available

---

## Browser Compatibility

### Desktop Browsers

- [ ] Chrome (latest version)
- [ ] Firefox (latest version)
- [ ] Safari (latest version)
- [ ] Edge (latest version)

### Mobile Browsers

- [ ] Chrome Mobile (Android)
- [ ] Safari Mobile (iOS)
- [ ] Firefox Mobile (Android)
- [ ] Samsung Internet (Android)

### Test Each Browser

- [ ] All pages render correctly
- [ ] All features work as expected
- [ ] No console errors
- [ ] Performance is acceptable
- [ ] Responsive design works

---

## Error Handling

### Network Errors

- [ ] **No Internet Connection**: Clear error message displayed
- [ ] **Timeout**: Error message with retry option
- [ ] **Server Unavailable (500)**: Generic error message displayed
- [ ] **Bad Request (400)**: Specific error message from API displayed
- [ ] **Not Found (404)**: Resource not found message displayed

### Application Errors

- [ ] **React Component Error**: Error boundary catches and displays fallback UI
- [ ] **JavaScript Error**: Error boundary catches and displays fallback UI
- [ ] **API Error**: Error message displayed in toast
- [ ] **Validation Error**: Error message displayed below field

### Error Recovery

- [ ] User can retry failed actions
- [ ] User can reload page to recover from errors
- [ ] User is not logged out due to non-auth errors
- [ ] Error state is cleared after successful retry
- [ ] User can navigate away from error state

---

## Production Readiness Checklist

### Environment Configuration

- [ ] `.env.local` is not committed to version control
- [ ] `.env.local.example` is up to date
- [ ] Production environment variables are set correctly
- [ ] API URL points to production backend
- [ ] Better Auth secret is strong and unique
- [ ] NODE_ENV is set to "production"

### Build and Deployment

- [ ] `npm run build` completes without errors
- [ ] Build output is optimized (check bundle size)
- [ ] No console warnings in production build
- [ ] Source maps are generated for debugging
- [ ] Static assets are properly cached

### Security

- [ ] All user input is sanitized
- [ ] JWT tokens are verified on backend
- [ ] HTTPS is enforced in production
- [ ] CORS is properly configured
- [ ] Rate limiting is enabled on backend
- [ ] Security headers are set (CSP, X-Frame-Options, etc.)

### Monitoring and Logging

- [ ] Error tracking is set up (Sentry, LogRocket, etc.)
- [ ] Analytics is set up (Google Analytics, Plausible, etc.)
- [ ] Performance monitoring is enabled
- [ ] API errors are logged
- [ ] User actions are tracked (optional)

### Documentation

- [ ] README.md is complete and accurate
- [ ] API documentation is available
- [ ] Environment variables are documented
- [ ] Deployment guide is available
- [ ] Troubleshooting guide is available

---

## Testing Tools

### Recommended Tools

1. **Chrome DevTools**
   - Network tab for API inspection
   - Lighthouse for performance and accessibility
   - Console for error checking

2. **Browser Extensions**
   - WAVE (Accessibility)
   - axe DevTools (Accessibility)
   - React Developer Tools

3. **Online Tools**
   - WebPageTest.org (Performance)
   - Google PageSpeed Insights (Performance)
   - BrowserStack (Cross-browser testing)

4. **Manual Testing**
   - Test on real devices when possible
   - Test with slow network (Chrome DevTools → Network → Throttling)
   - Test with screen reader (NVDA, JAWS, VoiceOver)

---

## Sign-Off

### Testing Completed By

- **Tester Name**: ___________________________
- **Date**: ___________________________
- **Environment**: [ ] Development [ ] Staging [ ] Production

### Results Summary

- **Total Tests**: ___________________________
- **Passed**: ___________________________
- **Failed**: ___________________________
- **Blocked**: ___________________________

### Critical Issues Found

1. ___________________________
2. ___________________________
3. ___________________________

### Approval

- [ ] All critical tests passed
- [ ] All security tests passed
- [ ] Performance meets targets
- [ ] Accessibility meets WCAG 2.1 AA
- [ ] Ready for production deployment

**Approved By**: ___________________________
**Date**: ___________________________

---

**Version**: 1.0.0
**Last Updated**: 2026-02-05
