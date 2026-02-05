"""
Team Member API routes for team membership management.

This module implements the team membership endpoints:
- POST /api/teams/{team_id}/members: Invite a user to join the team
- DELETE /api/teams/{team_id}/members/{user_id}: Remove a member from the team
- POST /api/teams/{team_id}/leave: Leave a team (self-removal)

All endpoints require JWT authentication and enforce role-based permissions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from app.database.connection import get_db
from app.schemas.team_member import InviteMemberRequest, TeamMemberResponse, ChangeRoleRequest
from app.services import team_member_service, team_service, user_service
from app.middleware.auth import get_current_user
from app.middleware.permissions import (
    require_team_member,
    require_team_admin,
    validate_role_change
)


# Create router with /api/teams prefix
router = APIRouter(
    prefix="/api/teams",
    tags=["Team Members"],
    responses={
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "Not Found - Team or user does not exist"},
        422: {"description": "Validation Error - Invalid input data"},
        500: {"description": "Internal Server Error"}
    }
)


@router.post(
    "/{team_id}/members",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite a user to join the team",
    description="""
    Invite a user to join the team with a specific role.

    **Permission:** Owner or Admin

    **Note:** Cannot assign 'owner' role via this endpoint. Use role change endpoint for ownership transfer.

    **Returns:**
    - Team membership information

    **Error Responses:**
    - 400: Invalid request data or invalid role
    - 401: Not authenticated
    - 403: Not owner or admin
    - 404: Team or user does not exist
    - 409: User is already a team member
    - 500: Server error
    """
)
def invite_member(
    team_id: str,
    request: InviteMemberRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TeamMemberResponse:
    """
    Invite a user to join the team with a specific role.

    This endpoint allows team owners and admins to add new members to the team.
    The 'owner' role cannot be assigned via this endpoint (use role change for
    ownership transfer).

    Args:
        team_id: Team identifier (UUID)
        request: InviteMemberRequest containing user_id and role
        current_user: Authenticated user info from JWT token
        db: Database session dependency

    Returns:
        TeamMemberResponse with membership information

    Raises:
        HTTPException 403: If user is not owner or admin
        HTTPException 404: If team or user does not exist
        HTTPException 409: If user is already a team member
        HTTPException 500: If server error occurs

    Example Request:
        ```json
        {
            "user_id": "987fcdeb-51a2-43f7-b123-456789abcdef",
            "role": "member"
        }
        ```

    Example Response:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "team_id": "660e8400-e29b-41d4-a716-446655440001",
            "user_id": "987fcdeb-51a2-43f7-b123-456789abcdef",
            "role": "member",
            "joined_at": "2026-02-04T10:30:00Z"
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

        # Check if target user exists
        target_user = user_service.get_user_by_id(db, request.user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {request.user_id} not found"
            )

        # Check if user is already a member
        existing_membership = team_member_service.get_team_member(db, team_id, request.user_id)
        if existing_membership:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {request.user_id} is already a member of team {team_id}"
            )

        # Invite member
        membership = team_member_service.invite_member(
            db=db,
            team_id=team_id,
            user_id=request.user_id,
            role=request.role
        )

        # Return membership response
        return TeamMemberResponse(
            id=membership.id,
            team_id=membership.team_id,
            user_id=membership.user_id,
            role=membership.role.value,
            joined_at=membership.joined_at
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except ValueError as e:
        # Validation error (e.g., trying to assign owner role)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except IntegrityError:
        # Database constraint violation (duplicate membership)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {request.user_id} is already a member of team {team_id}"
        )

    except Exception as e:
        # Log error for debugging
        print(f"Invite member error: {str(e)}")

        # Return generic error to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while inviting the member. Please try again."
        )


@router.delete(
    "/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a member from the team",
    description="""
    Remove a member from the team.

    **Permission:** Owner or Admin

    **Restrictions:** Cannot remove the team owner

    **Returns:**
    - 204 No Content (empty body)

    **Error Responses:**
    - 401: Not authenticated
    - 403: Not owner/admin, or attempting to remove owner
    - 404: Team or user does not exist
    - 500: Server error
    """
)
def remove_member(
    team_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Remove a member from the team.

    This endpoint allows team owners and admins to remove members from the team.
    The team owner cannot be removed (ownership must be transferred first).

    Args:
        team_id: Team identifier (UUID)
        user_id: User identifier to remove (UUID)
        current_user: Authenticated user info from JWT token
        db: Database session dependency

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 403: If user is not owner/admin, or attempting to remove owner
        HTTPException 404: If team or user does not exist
        HTTPException 500: If server error occurs

    Example:
        ```
        DELETE /api/teams/550e8400-e29b-41d4-a716-446655440000/members/987fcdeb-51a2-43f7-b123-456789abcdef
        Authorization: Bearer <token>
        ```
    """
    try:
        # Extract user ID from token
        requesting_user_id = current_user["user_id"]

        # Check if team exists
        team = team_service.get_team_by_id(db, team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team {team_id} not found"
            )

        # Verify requesting user is owner or admin
        require_team_admin(db, team_id, requesting_user_id)

        # Check if target user is a member
        target_membership = team_member_service.get_team_member(db, team_id, user_id)
        if not target_membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} is not a member of team {team_id}"
            )

        # Remove member
        success = team_member_service.remove_member(
            db=db,
            team_id=team_id,
            user_id=user_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} is not a member of team {team_id}"
            )

        # Return 204 No Content (no response body)
        return None

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except ValueError as e:
        # Validation error (e.g., trying to remove owner)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

    except Exception as e:
        # Log error for debugging
        print(f"Remove member error: {str(e)}")

        # Return generic error to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while removing the member. Please try again."
        )


@router.patch(
    "/{team_id}/members/{user_id}",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Change a team member's role",
    description="""
    Change a team member's role.

    **Permission:** Owner (can assign any role) or Admin (can assign member/viewer only)

    **Ownership Transfer:** When promoting a member to owner, the current owner is automatically demoted to admin (atomic operation)

    **Restrictions:**
    - Cannot change your own role
    - Admins cannot change owner or admin roles
    - Only owners can promote to owner or change admin roles

    **Returns:**
    - Updated team membership information

    **Error Responses:**
    - 400: Invalid request data
    - 401: Not authenticated
    - 403: Insufficient permissions or attempting to change own role
    - 404: Team or user does not exist
    - 500: Server error
    """
)
def change_member_role(
    team_id: str,
    user_id: str,
    request: ChangeRoleRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TeamMemberResponse:
    """
    Change a team member's role.

    This endpoint allows team owners and admins to change member roles.
    Owners can assign any role (including owner for ownership transfer).
    Admins can only assign member/viewer roles.

    When promoting to owner, the current owner is automatically demoted to admin
    in a single atomic transaction.

    Args:
        team_id: Team identifier (UUID)
        user_id: User identifier whose role to change (UUID)
        request: ChangeRoleRequest containing new role
        current_user: Authenticated user info from JWT token
        db: Database session dependency

    Returns:
        TeamMemberResponse with updated membership information

    Raises:
        HTTPException 403: If insufficient permissions or attempting to change own role
        HTTPException 404: If team or user does not exist
        HTTPException 500: If server error occurs

    Example Request:
        ```json
        {
            "role": "admin"
        }
        ```

    Example Response:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "team_id": "660e8400-e29b-41d4-a716-446655440001",
            "user_id": "987fcdeb-51a2-43f7-b123-456789abcdef",
            "role": "admin",
            "joined_at": "2026-02-04T10:30:00Z"
        }
        ```
    """
    try:
        # Extract requesting user ID from token
        requesting_user_id = current_user["user_id"]

        # Check if team exists
        team = team_service.get_team_by_id(db, team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team {team_id} not found"
            )

        # Check if target user is a member
        target_membership = team_member_service.get_team_member(db, team_id, user_id)
        if not target_membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} is not a member of team {team_id}"
            )

        # Validate role change permissions
        validate_role_change(
            session=db,
            team_id=team_id,
            target_user_id=user_id,
            new_role=request.role,
            requesting_user_id=requesting_user_id
        )

        # Update member role (handles ownership transfer atomically)
        updated_membership = team_member_service.update_member_role(
            db=db,
            team_id=team_id,
            user_id=user_id,
            new_role=request.role
        )

        if not updated_membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} is not a member of team {team_id}"
            )

        # Return updated membership response
        return TeamMemberResponse(
            id=updated_membership.id,
            team_id=updated_membership.team_id,
            user_id=updated_membership.user_id,
            role=updated_membership.role.value,
            joined_at=updated_membership.joined_at
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except ValueError as e:
        # Validation error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # Log error for debugging
        print(f"Change member role error: {str(e)}")

        # Return generic error to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while changing the member role. Please try again."
        )


@router.post(
    "/{team_id}/leave",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Leave a team (self-removal)",
    description="""
    Leave a team (self-removal).

    **Permission:** Any team member except owner

    **Restrictions:** Team owner cannot leave (must transfer ownership first)

    **Returns:**
    - 204 No Content (empty body)

    **Error Responses:**
    - 401: Not authenticated
    - 403: User is the team owner
    - 404: Team does not exist or user is not a member
    - 500: Server error
    """
)
def leave_team(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Leave a team (self-removal).

    This endpoint allows team members to remove themselves from a team.
    The team owner cannot leave (they must transfer ownership first or delete the team).

    Args:
        team_id: Team identifier (UUID)
        current_user: Authenticated user info from JWT token
        db: Database session dependency

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 403: If user is the team owner
        HTTPException 404: If team does not exist or user is not a member
        HTTPException 500: If server error occurs

    Example:
        ```
        POST /api/teams/550e8400-e29b-41d4-a716-446655440000/leave
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

        # Check if user is a member
        membership = team_member_service.get_team_member(db, team_id, user_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User is not a member of team {team_id}"
            )

        # Leave team
        success = team_member_service.leave_team(
            db=db,
            team_id=team_id,
            user_id=user_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User is not a member of team {team_id}"
            )

        # Return 204 No Content (no response body)
        return None

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except ValueError as e:
        # Validation error (e.g., owner trying to leave)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

    except Exception as e:
        # Log error for debugging
        print(f"Leave team error: {str(e)}")

        # Return generic error to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while leaving the team. Please try again."
        )
