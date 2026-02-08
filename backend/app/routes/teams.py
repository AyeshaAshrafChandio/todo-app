"""
Team API routes for team creation and management.

This module implements the team endpoints:
- POST /api/teams: Create a new team
- GET /api/teams: List user's teams
- GET /api/teams/{team_id}: Get team details
- PATCH /api/teams/{team_id}: Update team settings
- DELETE /api/teams/{team_id}: Delete team

All endpoints require JWT authentication and enforce role-based permissions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from app.database.connection import get_db
from app.schemas.team import (
    TeamCreate,
    TeamResponse,
    TeamUpdate,
    TeamListResponse,
    TeamDetailResponse
)
from app.services import team_service
from app.middleware.auth import get_current_user
from app.middleware.permissions import (
    require_team_member,
    require_team_admin,
    require_team_owner
)


# Create router with /api/teams prefix
router = APIRouter(
    prefix="/api/teams",
    tags=["Teams"],
    responses={
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "Not Found - Team does not exist"},
        422: {"description": "Validation Error - Invalid input data"},
        500: {"description": "Internal Server Error"}
    }
)


@router.post(
    "",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new team",
    description="""
    Create a new team. The authenticated user automatically becomes the team owner.

    **Returns:**
    - Team information (id, name, description, owner_id, timestamps)

    **Error Responses:**
    - 400: Invalid request data (missing name, name too long, etc.)
    - 401: Not authenticated
    - 409: Team name already exists
    - 500: Server error during team creation
    """
)
def create_team(
    request: TeamCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TeamResponse:
    """
    Create a new team.

    This endpoint creates a new team with the authenticated user as the owner.
    The owner is automatically added to the team_members table with the 'owner' role.

    Args:
        request: TeamCreate containing name and optional description
        current_user: Authenticated user info from JWT token
        db: Database session dependency

    Returns:
        TeamResponse with team information

    Raises:
        HTTPException 409: If team name already exists
        HTTPException 500: If server error occurs during creation

    Example Request:
        ```json
        {
            "name": "Engineering Team",
            "description": "Core engineering team for product development"
        }
        ```

    Example Response:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Engineering Team",
            "description": "Core engineering team for product development",
            "owner_id": "660e8400-e29b-41d4-a716-446655440001",
            "created_at": "2026-02-04T10:30:00Z",
            "updated_at": "2026-02-04T10:30:00Z"
        }
        ```
    """
    try:
        # Extract user ID from token
        user_id = current_user["user_id"]

        # Check if team name already exists
        existing_team = team_service.get_team_by_name(db, request.name)
        if existing_team:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Team name '{request.name}' already exists"
            )

        # Create team (also creates owner membership in transaction)
        team = team_service.create_team(
            db=db,
            name=request.name,
            owner_id=user_id,
            description=request.description
        )

        # Return team response
        return TeamResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            owner_id=team.owner_id,
            created_at=team.created_at,
            updated_at=team.updated_at
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except IntegrityError:
        # Database constraint violation (duplicate name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Team name '{request.name}' already exists"
        )

    except Exception as e:
        # Log error for debugging
        print(f"Create team error: {str(e)}")

        # Return generic error to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the team. Please try again."
        )


@router.get(
    "",
    response_model=list[TeamListResponse],
    status_code=status.HTTP_200_OK,
    summary="List user's teams",
    description="""
    List all teams the authenticated user is a member of.

    **Returns:**
    - List of teams with user's role and member count

    **Error Responses:**
    - 401: Not authenticated
    - 500: Server error
    """
)
def list_teams(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[TeamListResponse]:
    """
    List all teams the authenticated user is a member of.

    This endpoint returns all teams where the user has a membership record,
    along with their role in each team and the total member count.

    Args:
        current_user: Authenticated user info from JWT token
        db: Database session dependency

    Returns:
        List of TeamListResponse objects

    Raises:
        HTTPException 500: If server error occurs

    Example Response:
        ```json
        [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Engineering Team",
                "description": "Core engineering team",
                "role": "owner",
                "member_count": 5,
                "created_at": "2026-02-04T10:30:00Z"
            }
        ]
        ```
    """
    try:
        # Extract user ID from token
        user_id = current_user["user_id"]

        # Get user's teams with role and member count
        teams = team_service.get_user_teams(db, user_id)

        # Convert to response models
        return [
            TeamListResponse(
                id=team["id"],
                name=team["name"],
                description=team["description"],
                role=team["role"],
                member_count=team["member_count"],
                created_at=team["created_at"]
            )
            for team in teams
        ]

    except Exception as e:
        # Log error for debugging
        print(f"List teams error: {str(e)}")

        # Return generic error to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving teams. Please try again."
        )


@router.get(
    "/{team_id}",
    response_model=TeamDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get team details",
    description="""
    Get detailed information about a specific team, including all members.

    **Permission:** Must be a team member

    **Returns:**
    - Team information with complete members list

    **Error Responses:**
    - 401: Not authenticated
    - 403: Not a team member
    - 404: Team does not exist
    - 500: Server error
    """
)
def get_team(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TeamDetailResponse:
    """
    Get detailed team information including all members.

    This endpoint returns complete team information with a list of all members,
    their roles, and email addresses. Only team members can access this endpoint.

    Args:
        team_id: Team identifier (UUID)
        current_user: Authenticated user info from JWT token
        db: Database session dependency

    Returns:
        TeamDetailResponse with team info and members list

    Raises:
        HTTPException 403: If user is not a team member
        HTTPException 404: If team does not exist
        HTTPException 500: If server error occurs

    Example Response:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Engineering Team",
            "description": "Core engineering team",
            "owner_id": "660e8400-e29b-41d4-a716-446655440001",
            "created_at": "2026-02-04T10:30:00Z",
            "updated_at": "2026-02-04T10:30:00Z",
            "members": [
                {
                    "user_id": "660e8400-e29b-41d4-a716-446655440001",
                    "email": "owner@example.com",
                    "role": "owner",
                    "joined_at": "2026-02-04T10:30:00Z"
                }
            ]
        }
        ```
    """
    try:
        # Extract user ID from token
        user_id = current_user["user_id"]

        # Check if team exists
        team_details = team_service.get_team_details(db, team_id)
        if not team_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team {team_id} not found"
            )

        # Verify user is a team member
        require_team_member(db, team_id, user_id)

        # Return team details
        return TeamDetailResponse(**team_details)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Log error for debugging
        print(f"Get team error: {str(e)}")

        # Return generic error to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving team details. Please try again."
        )


@router.patch(
    "/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
    summary="Update team settings",
    description="""
    Update team name and/or description.

    **Permission:** Owner or Admin

    **Returns:**
    - Updated team information

    **Error Responses:**
    - 400: Invalid request data
    - 401: Not authenticated
    - 403: Not owner or admin
    - 404: Team does not exist
    - 409: New name already exists
    - 500: Server error
    """
)
def update_team(
    team_id: str,
    request: TeamUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TeamResponse:
    """
    Update team settings (name and/or description).

    This endpoint allows team owners and admins to update the team name
    and/or description. Only provided fields will be updated.

    Args:
        team_id: Team identifier (UUID)
        request: TeamUpdate containing optional name and description
        current_user: Authenticated user info from JWT token
        db: Database session dependency

    Returns:
        TeamResponse with updated team information

    Raises:
        HTTPException 403: If user is not owner or admin
        HTTPException 404: If team does not exist
        HTTPException 409: If new name already exists
        HTTPException 500: If server error occurs

    Example Request:
        ```json
        {
            "description": "Updated team description"
        }
        ```

    Example Response:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Engineering Team",
            "description": "Updated team description",
            "owner_id": "660e8400-e29b-41d4-a716-446655440001",
            "created_at": "2026-02-04T10:30:00Z",
            "updated_at": "2026-02-04T11:00:00Z"
        }
        ```
    """
    try:
        # Extract user ID from token
        user_id = current_user["user_id"]

        # Check if team exists
        team = team_service.get_team_by_id(db, team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team {team_id} not found"
            )

        # Verify user is owner or admin
        require_team_admin(db, team_id, user_id)

        # Check if new name already exists (if name is being changed)
        if request.name and request.name != team.name:
            existing_team = team_service.get_team_by_name(db, request.name)
            if existing_team:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Team name '{request.name}' already exists"
                )

        # Update team
        updated_team = team_service.update_team(
            db=db,
            team_id=team_id,
            name=request.name,
            description=request.description
        )

        # Return updated team
        return TeamResponse(
            id=updated_team.id,
            name=updated_team.name,
            description=updated_team.description,
            owner_id=updated_team.owner_id,
            created_at=updated_team.created_at,
            updated_at=updated_team.updated_at
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except IntegrityError:
        # Database constraint violation (duplicate name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Team name '{request.name}' already exists"
        )

    except Exception as e:
        # Log error for debugging
        print(f"Update team error: {str(e)}")

        # Return generic error to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the team. Please try again."
        )


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete team",
    description="""
    Delete a team. All team members are removed, and team tasks are converted to personal tasks.

    **Permission:** Owner only

    **Returns:**
    - 204 No Content (empty body)

    **Error Responses:**
    - 401: Not authenticated
    - 403: Not the team owner
    - 404: Team does not exist
    - 500: Server error
    """
)
def delete_team(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a team.

    This endpoint deletes the team and all team memberships (CASCADE),
    and converts all team tasks to personal tasks (sets team_id to NULL).
    Only the team owner can delete the team.

    Args:
        team_id: Team identifier (UUID)
        current_user: Authenticated user info from JWT token
        db: Database session dependency

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 403: If user is not the team owner
        HTTPException 404: If team does not exist
        HTTPException 500: If server error occurs

    Example:
        ```
        DELETE /api/teams/550e8400-e29b-41d4-a716-446655440000
        Authorization: Bearer <token>
        ```
    """
    try:
        # Extract user ID from token
        user_id = current_user["user_id"]

        # Check if team exists
        team = team_service.get_team_by_id(db, team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team {team_id} not found"
            )

        # Verify user is the team owner
        require_team_owner(db, team_id, user_id)

        # Delete team (converts tasks to personal, deletes memberships)
        success = team_service.delete_team(db, team_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team {team_id} not found"
            )

        # Return 204 No Content (no response body)
        return None

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Log error for debugging
        print(f"Delete team error: {str(e)}")

        # Return generic error to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the team. Please try again."
        )
