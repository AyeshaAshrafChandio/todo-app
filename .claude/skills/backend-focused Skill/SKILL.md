---
name: backend-core
description: Design and implement backend systems including API routes, request/response handling, and database connectivity.
---

# Backend Core Development

## Instructions

1. **Project Setup**
   - Initialize backend framework (Node.js / Express / FastAPI / Django)
   - Environment configuration (.env)
   - Folder structure (routes, controllers, services, models)

2. **Routing**
   - Define RESTful API routes
   - Use proper HTTP methods (GET, POST, PUT, DELETE)
   - Version APIs if required (`/api/v1`)

3. **Request & Response Handling**
   - Parse request body, params, and query
   - Validate incoming data
   - Send structured JSON responses
   - Proper HTTP status codes

4. **Database Integration**
   - Connect to database (MongoDB / PostgreSQL / MySQL)
   - Use ORM/ODM if applicable
   - Perform CRUD operations
   - Handle connection errors gracefully

5. **Error Handling**
   - Centralized error middleware
   - Consistent error response format
   - Logging for debugging

## Best Practices
- Follow REST conventions
- Keep controllers thin, move logic to services
- Validate input before DB operations
- Never expose sensitive data
- Use async/await for clean async code
- Secure routes with authentication when needed

## Example Structure

```js
// routes/user.routes.js
router.post("/users", createUser);
router.get("/users/:id", getUser);
