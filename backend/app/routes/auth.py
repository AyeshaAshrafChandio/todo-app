"""
Authentication API routes for user signup, signin, and profile retrieval.

This module implements the authentication endpoints:
- POST /api/auth/signup: Register new user account
- POST /api/auth/signin: Authenticate existing user
- GET /api/auth/me: Get current authenticated user profile

All endpoints follow security best practices including:
- Password hashing with bcrypt
- JWT token generation and verification
- Generic error messages to prevent information leakage
- Input validation and sanitization
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from app.database.connection import get_db
from app.schemas.auth import SignupRequest, SigninRequest, AuthResponse
from app.schemas.user import UserResponse
from app.services import auth_service, user_service
from app.middleware.auth import get_current_user


# Create router with /api/auth prefix
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized - Invalid or expired token"},
        422: {"description": "Validation Error - Invalid input data"},
        500: {"description": "Internal Server Error"}
    }
)


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user account",
    description="""
    Register a new user account with email and password.

    **Password Requirements:**
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit

    **Returns:**
    - User information (id, email, created_at)
    - JWT access token (valid for 24 hours)
    - Token expiration timestamp

    **Error Responses:**
    - 422: Email already registered or validation failed
    - 500: Server error during registration
    """
)
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
) -> AuthResponse:
    """
    Register a new user account.

    This endpoint creates a new user account with the provided email and password.
    The password is hashed using bcrypt before storage. A JWT token is generated
    and returned for immediate authentication.

    Security:
        - Password is hashed with bcrypt (cost factor 12)
        - Email uniqueness is enforced by database constraint
        - Password strength is validated by Pydantic schema
        - JWT token is signed with BETTER_AUTH_SECRET

    Args:
        request: SignupRequest containing email and password
        db: Database session dependency

    Returns:
        AuthResponse with user info, JWT token, and expiration

    Raises:
        HTTPException 422: If email already exists or validation fails
        HTTPException 500: If server error occurs during registration

    Example Request:
        ```json
        {
            "email": "user@example.com",
            "password": "SecurePass123"
        }
        ```

    Example Response:
        ```json
        {
            "user": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2026-02-04T10:30:00Z"
            },
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "expires_at": "2026-02-05T10:30:00Z"
        }
        ```
    """
    try:
        # Check if email already exists
        existing_user = user_service.get_user_by_email(db, request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email already registered"
            )

        # Create new user (password is hashed inside create_user)
        user = user_service.create_user(
            db=db,
            email=request.email,
            password=request.password
        )

        # Generate JWT token
        token_data = auth_service.create_jwt_token(
            user_id=str(user.id),
            email=user.email
        )

        # Return authentication response
        return AuthResponse(
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                created_at=user.created_at
            ),
            token=token_data["token"],
            expires_at=token_data["expires_at"]
        )

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise

    except IntegrityError:
        # Database constraint violation (duplicate email)
        # This is a backup check in case the email check above fails due to race condition
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already registered"
        )

    except Exception as e:
        # Log error for debugging (in production, use proper logging)
        print(f"Signup error: {str(e)}")

        # Return generic error to client (don't leak internal details)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration. Please try again."
        )


@router.post(
    "/signin",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate existing user",
    description="""
    Authenticate an existing user with email and password.

    **Returns:**
    - User information (id, email, created_at)
    - JWT access token (valid for 24 hours)
    - Token expiration timestamp

    **Error Responses:**
    - 401: Invalid email or password (generic message for security)
    - 500: Server error during authentication

    **Security Note:**
    Error messages are intentionally generic to prevent user enumeration attacks.
    """
)
def signin(
    request: SigninRequest,
    db: Session = Depends(get_db)
) -> AuthResponse:
    """
    Authenticate an existing user.

    This endpoint verifies user credentials and returns a JWT token for
    authenticated API access. Error messages are intentionally generic
    to prevent user enumeration attacks.

    Security:
        - Generic error messages (don't reveal if email exists)
        - Timing-safe password comparison
        - JWT token signed with BETTER_AUTH_SECRET
        - 24-hour token expiration

    Args:
        request: SigninRequest containing email and password
        db: Database session dependency

    Returns:
        AuthResponse with user info, JWT token, and expiration

    Raises:
        HTTPException 401: If email not found or password incorrect
        HTTPException 500: If server error occurs during authentication

    Example Request:
        ```json
        {
            "email": "user@example.com",
            "password": "SecurePass123"
        }
        ```

    Example Response:
        ```json
        {
            "user": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2026-02-04T10:30:00Z"
            },
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "expires_at": "2026-02-05T10:30:00Z"
        }
        ```
    """
    try:
        # Find user by email
        user = user_service.get_user_by_email(db, request.email)

        # Return generic error if user not found (don't reveal email existence)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password using timing-safe comparison
        is_valid = auth_service.verify_password(request.password, user.password_hash)

        # Return generic error if password incorrect
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Generate JWT token
        token_data = auth_service.create_jwt_token(
            user_id=str(user.id),
            email=user.email
        )

        # Return authentication response
        return AuthResponse(
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                created_at=user.created_at
            ),
            token=token_data["token"],
            expires_at=token_data["expires_at"]
        )

    except HTTPException:
        # Re-raise HTTP exceptions (authentication errors)
        raise

    except Exception as e:
        # Log error for debugging (in production, use proper logging)
        print(f"Signin error: {str(e)}")

        # Return generic error to client (don't leak internal details)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during authentication. Please try again."
        )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
    description="""
    Retrieve the profile information of the currently authenticated user.

    **Authentication Required:**
    This endpoint requires a valid JWT token in the Authorization header:
    ```
    Authorization: Bearer <token>
    ```

    **Returns:**
    - User information (id, email, created_at)

    **Error Responses:**
    - 401: Invalid or expired token
    - 404: User not found (token valid but user deleted)
    - 500: Server error
    """
)
def get_me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get current authenticated user profile.

    This endpoint returns the profile information of the user identified
    by the JWT token in the Authorization header. The token is verified
    by the get_current_user dependency.

    Security:
        - Requires valid JWT token in Authorization header
        - Token signature and expiration are verified
        - User ID is extracted from token claims

    Args:
        current_user: Authenticated user info from JWT token (dependency)
        db: Database session dependency

    Returns:
        UserResponse with user profile information

    Raises:
        HTTPException 401: If token is invalid or expired (handled by middleware)
        HTTPException 404: If user not found in database
        HTTPException 500: If server error occurs

    Example Request:
        ```
        GET /api/auth/me
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        ```

    Example Response:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "created_at": "2026-02-04T10:30:00Z"
        }
        ```
    """
    try:
        # Extract user ID from token claims
        user_id = current_user["user_id"]

        # Retrieve user from database
        user = user_service.get_user_by_id(db, user_id)

        # Return 404 if user not found (token valid but user deleted)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Return user profile
        return UserResponse(
            id=str(user.id),
            email=user.email,
            created_at=user.created_at
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Log error for debugging (in production, use proper logging)
        print(f"Get user profile error: {str(e)}")

        # Return generic error to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving user profile. Please try again."
        )
