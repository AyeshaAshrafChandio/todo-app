"""
Team Member service for database operations on TeamMember model.

This module provides service functions for managing team memberships including
inviting members, removing members, and handling self-removal (leaving teams).
"""

from typing import Optional
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.models.team_member import TeamMember, TeamRole
from app.models.user import User


def invite_member(
    db: Session,
    team_id: str,
    user_id: str,
    role: TeamRole
) -> TeamMember:
    """
    Add a user to a team with a specific role.

    Creates a new team membership record. The role cannot be 'owner'
    (ownership transfer uses a different mechanism).

    Args:
        db: Database session
        team_id: Team ID to add member to
        user_id: User ID to add as member
        role: Role to assign (admin/member/viewer, not owner)

    Returns:
        Created TeamMember object

    Raises:
        IntegrityError: If user is already a member of the team
        ValueError: If role is 'owner' or user/team doesn't exist

    Example:
        ```python
        membership = invite_member(
            db=db,
            team_id="team-uuid",
            user_id="user-uuid",
            role=TeamRole.MEMBER
        )
        ```

    Database Operations:
        1. Validate user exists
        2. Create TeamMember record
        3. Add to database
        4. Commit transaction
        5. Refresh to get generated fields
    """
    # Validate role is not owner
    if role == TeamRole.OWNER:
        raise ValueError("Cannot assign 'owner' role via invite. Use role change for ownership transfer.")

    # Validate user exists
    user = db.get(User, user_id)
    if not user:
        raise ValueError(f"User {user_id} does not exist")

    try:
        # Create membership
        membership = TeamMember(
            team_id=team_id,
            user_id=user_id,
            role=role
        )

        # Add to database
        db.add(membership)
        db.commit()
        db.refresh(membership)

        return membership

    except IntegrityError:
        db.rollback()
        raise


def remove_member(
    db: Session,
    team_id: str,
    user_id: str
) -> bool:
    """
    Remove a member from a team.

    Deletes the team membership record. Cannot remove the team owner
    (ownership must be transferred first).

    Args:
        db: Database session
        team_id: Team ID to remove member from
        user_id: User ID to remove

    Returns:
        True if member was removed, False if membership not found

    Raises:
        ValueError: If attempting to remove the team owner

    Example:
        ```python
        success = remove_member(
            db=db,
            team_id="team-uuid",
            user_id="user-uuid"
        )
        ```

    Database Operations:
        1. Find membership record
        2. Validate not removing owner
        3. Delete membership
        4. Commit transaction
    """
    # Find membership
    statement = select(TeamMember).where(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    )
    membership = db.exec(statement).first()

    if not membership:
        return False

    # Cannot remove owner
    if membership.role == TeamRole.OWNER:
        raise ValueError("Cannot remove team owner. Transfer ownership first.")

    try:
        # Delete membership
        db.delete(membership)
        db.commit()

        return True

    except Exception:
        db.rollback()
        raise


def leave_team(
    db: Session,
    team_id: str,
    user_id: str
) -> bool:
    """
    Allow a user to leave a team (self-removal).

    Removes the user's membership from the team. Team owners cannot leave
    (they must transfer ownership first or delete the team).

    Args:
        db: Database session
        team_id: Team ID to leave
        user_id: User ID who is leaving

    Returns:
        True if user left the team, False if not a member

    Raises:
        ValueError: If user is the team owner

    Example:
        ```python
        success = leave_team(
            db=db,
            team_id="team-uuid",
            user_id="user-uuid"
        )
        ```

    Database Operations:
        1. Find membership record
        2. Validate not the owner
        3. Delete membership
        4. Commit transaction
    """
    # Find membership
    statement = select(TeamMember).where(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    )
    membership = db.exec(statement).first()

    if not membership:
        return False

    # Owner cannot leave (must transfer ownership or delete team)
    if membership.role == TeamRole.OWNER:
        raise ValueError("Team owner cannot leave. Transfer ownership first or delete the team.")

    try:
        # Delete membership
        db.delete(membership)
        db.commit()

        return True

    except Exception:
        db.rollback()
        raise


def get_team_member(
    db: Session,
    team_id: str,
    user_id: str
) -> Optional[TeamMember]:
    """
    Get a specific team membership record.

    Args:
        db: Database session
        team_id: Team ID
        user_id: User ID

    Returns:
        TeamMember object if found, None otherwise

    Example:
        ```python
        membership = get_team_member(db, "team-uuid", "user-uuid")
        if membership:
            print(f"User role: {membership.role.value}")
        ```
    """
    statement = select(TeamMember).where(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    )
    return db.exec(statement).first()


def update_member_role(
    db: Session,
    team_id: str,
    user_id: str,
    new_role: TeamRole
) -> Optional[TeamMember]:
    """
    Update a team member's role.

    Changes a member's role in the team. If promoting to owner, the current
    owner is automatically demoted to admin (atomic operation).

    Args:
        db: Database session
        team_id: Team ID
        user_id: User ID whose role to change
        new_role: New role to assign

    Returns:
        Updated TeamMember object, or None if membership not found

    Example:
        ```python
        membership = update_member_role(
            db=db,
            team_id="team-uuid",
            user_id="user-uuid",
            new_role=TeamRole.ADMIN
        )
        ```

    Database Operations:
        1. Find membership record
        2. If promoting to owner, demote current owner to admin
        3. Update role
        4. Commit transaction (atomic)
        5. Refresh to get updated fields
    """
    # Find membership
    membership = get_team_member(db, team_id, user_id)
    if not membership:
        return None

    try:
        # If promoting to owner, demote current owner to admin
        if new_role == TeamRole.OWNER:
            # Find current owner
            current_owner_statement = select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.role == TeamRole.OWNER
            )
            current_owner = db.exec(current_owner_statement).first()

            if current_owner and current_owner.user_id != user_id:
                # Demote current owner to admin
                current_owner.role = TeamRole.ADMIN
                db.add(current_owner)

        # Update role
        membership.role = new_role
        db.add(membership)

        # Commit transaction (atomic)
        db.commit()
        db.refresh(membership)

        return membership

    except Exception:
        db.rollback()
        raise


def get_team_members(db: Session, team_id: str) -> list[TeamMember]:
    """
    Get all members of a team.

    Args:
        db: Database session
        team_id: Team ID

    Returns:
        List of TeamMember objects

    Example:
        ```python
        members = get_team_members(db, "team-uuid")
        for member in members:
            print(f"{member.user_id}: {member.role.value}")
        ```
    """
    statement = select(TeamMember).where(TeamMember.team_id == team_id)
    return db.exec(statement).all()
