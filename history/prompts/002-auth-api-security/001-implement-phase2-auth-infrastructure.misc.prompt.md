---
id: 001
title: Implement Phase 2 Authentication Infrastructure
stage: misc
date: 2026-02-04
surface: agent
model: claude-sonnet-4-5
feature: 002-auth-api-security
branch: 002-auth-api-security
user: Ali Haider
command: direct-implementation
labels: ["authentication", "jwt", "bcrypt", "schemas", "middleware", "services", "security"]
links:
  spec: specs/002-auth-api-security/data-model.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/schemas/user.py
  - backend/app/schemas/auth.py
  - backend/app/middleware/__init__.py
  - backend/app/middleware/auth.py
  - backend/app/services/auth_service.py
  - backend/app/services/user_service.py
  - backend/requirements.txt
tests:
  - Comprehensive integration test (all components)
  - Schema validation tests (email, password strength)
  - Password hashing and verification tests
  - JWT token generation and verification tests
  - Middleware authentication tests
  - User access control tests
---

## Prompt

Implement Phase 2 authentication infrastructure for Authentication & API Security feature:

**Context**: This is Spec 2 which extends Spec 1. The database schema (User model, Task extension) is already complete. Now implement the authentication infrastructure.

**Tasks to Complete**:

1. **Create backend/app/schemas/user.py**:
   - UserResponse schema with fields: id (str), email (str), created_at (datetime)
   - No password_hash in response (security)

2. **Create backend/app/schemas/auth.py**:
   - SignupRequest: email (str, email format), password (str, min 8 chars)
   - SigninRequest: email (str), password (str)
   - AuthResponse: user (UserResponse), token (str), expires_at (datetime)

3. **Create backend/app/middleware/auth.py**:
   - Import PyJWT, HTTPBearer from fastapi.security
   - Implement get_current_user dependency function:
     - Extract token from Authorization header (Bearer format)
     - Verify JWT signature using settings.BETTER_AUTH_SECRET
     - Decode token to get userId and email claims
     - Return dict with user_id and email
     - Raise HTTPException 401 for invalid/expired tokens
   - Handle errors: ExpiredSignatureError, InvalidTokenError

4. **Create backend/app/services/auth_service.py**:
   - hash_password(password: str) -> str: Use bcrypt with cost factor 12
   - verify_password(password: str, password_hash: str) -> bool: Use bcrypt.checkpw
   - create_jwt_token(user_id: str, email: str) -> dict:
     - Create JWT with claims: userId, email, iat, exp (24 hours)
     - Sign with settings.BETTER_AUTH_SECRET using HS256
     - Return dict with token and expires_at

5. **Create backend/app/services/user_service.py**:
   - create_user(db: Session, email: str, password: str) -> User
   - get_user_by_email(db: Session, email: str) -> Optional[User]
   - get_user_by_id(db: Session, user_id: str) -> Optional[User]

**Reference Files**:
- Data model: specs/002-auth-api-security/data-model.md
- Research decisions: specs/002-auth-api-security/research.md
- Config: backend/app/config.py (has BETTER_AUTH_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_SECONDS)
- User model: backend/app/models/user.py (already created)

**Acceptance Criteria**:
- All schemas created with proper validation
- JWT middleware verifies tokens correctly
- Password hashing uses bcrypt with cost 12
- JWT tokens include userId and email claims
- Token expiration set to 24 hours
- Error handling for invalid/expired tokens
- Services handle database operations correctly

**Important**:
- Use settings.BETTER_AUTH_SECRET from config
- JWT algorithm: HS256
- Token expiration: settings.JWT_EXPIRATION_SECONDS (86400 = 24 hours)
- Password validation: min 8 chars, must have uppercase, lowercase, digit

## Response snapshot

Successfully implemented Phase 2 authentication infrastructure with all required components:

**1. Schemas Created:**
- `backend/app/schemas/user.py`: UserResponse schema (excludes password_hash for security)
- `backend/app/schemas/auth.py`: SignupRequest, SigninRequest, AuthResponse with comprehensive validation

**2. Middleware Created:**
- `backend/app/middleware/auth.py`: JWT token verification with get_current_user dependency and verify_user_access helper

**3. Services Created:**
- `backend/app/services/auth_service.py`: Password hashing (bcrypt cost 12), verification, and JWT token generation
- `backend/app/services/user_service.py`: User CRUD operations (create, get by email, get by ID)

**4. Dependencies Updated:**
- Added `email-validator==2.1.0` to requirements.txt for Pydantic EmailStr validation

**Security Features Implemented:**
- Bcrypt password hashing with cost factor 12
- JWT tokens with HS256 algorithm
- Token expiration: 24 hours (86400 seconds)
- Password validation: min 8 chars, uppercase, lowercase, digit required
- Email format validation (RFC 5322)
- Timing-safe password comparison
- HTTP Bearer token authentication
- User access control verification

**All Tests Passed:**
- Schema validation (email format, password strength)
- Password hashing and verification
- JWT token generation with correct claims (userId, email, iat, exp)
- JWT token verification in middleware
- Invalid token rejection
- User access control enforcement

## Outcome

- ✅ Impact: Complete authentication infrastructure implemented with industry-standard security practices (bcrypt, JWT, proper validation)
- 🧪 Tests: All integration tests passed (schema validation, password hashing, JWT generation/verification, middleware authentication, access control)
- 📁 Files: 7 files created/modified (4 new modules, 2 new schemas, 1 dependency update)
- 🔁 Next prompts: Implement authentication API endpoints (/auth/signup, /auth/signin) using these components
- 🧠 Reflection: Implementation follows security best practices with proper separation of concerns (schemas, middleware, services). All acceptance criteria met.

## Evaluation notes (flywheel)

- Failure modes observed: Initial missing email-validator dependency (resolved by adding to requirements.txt)
- Graders run and results (PASS/FAIL): PASS - All 6 test categories passed (schema validation, password hashing, JWT generation, JWT verification, user services, access control)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Implement authentication API endpoints to expose these services via REST API
