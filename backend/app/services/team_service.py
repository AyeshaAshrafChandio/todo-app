"""
Team service for database operations on Team model.

This module provides service functions for creating, retrieving, updating,
and deleting teams. It handles team-related business logic and database
interactions including transaction management for multi-record operations.
"""

from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.models.team import Team
from app.models.team_member import TeamMember, TeamRole
from app.models.task import Task
from app.models.user import User


def create_team(
    db: Session,
    name: str,
    owner_id: str,
    description: Optional[str] = None
) -> Team:
    """
    Create a new team and add the owner as a member in a single transaction.

    This function creates a team and automatically adds the creator as the
    team owner in the team_members table. Both operations are performed
    atomically in a single transaction.

    Args:
        db: Database session
        name: Team name (must be unique)
        owner_id: User ID of the team owner
        description: Optional team description

    Returns:
        Created Team object with generated ID and timestamps

    Raises:
        IntegrityError: If team name already exists or owner_id is invalid

    Example:
        ```python
        team = create_team(
            db=db,
            name="Engineering Team",
            owner_id="550e8400-e29b-41d4-a716-446655440000",
            description="Core engineering team"
        )
        ```

    Database Operations:
        1. Create Team object
        2. Add team to database
        3. Flush to get team ID
        4. Create TeamMember record with owner role
        5. Add membership to database
        6. Commit transaction (both team and membership)
        7. Refresh to get generated fields
    """
    try:
        # Create team object
        team = Team(
            name=name.strip(),
            owner_id=owner_id,
            description=description.strip() if description else None
        )

        # Add team to database
        db.add(team)
        db.flush()  # Flush to get team ID without committing

        # Create owner membership
        owner_membership = TeamMember(
            team_id=team.id,
            user_id=owner_id,
            role=TeamRole.OWNER
        )

        # Add membership to database
        db.add(owner_membership)

        # Commit both team and membership in single transaction
        db.commit()
        db.refresh(team)

        return team

    except IntegrityError:
        db.rollback()
        raise


def get_user_teams(db: Session, user_id: str) -> List[dict]:
    """
    Get all teams that a user is a member of with role and member count.

    Returns a list of teams with the user's role in each team and the
    total number of members in each team.

    Args:
        db: Database session
        user_id: User ID to get teams for

    Returns:
        List of dictionaries containing team info, user's role, and member count:
        [
            {
                "id": "team-uuid",
                "name": "Team Name",
                "description": "Team description",
                "role": "owner",
                "member_count": 5,
                "created_at": datetime
            }
        ]

    Example:
        ```python
        teams = get_user_teams(db, "550e8400-e29b-41d4-a716-446655440000")
        for team in teams:
            print(f"{team['name']}: {team['role']} ({team['member_count']} members)")
        ```

    Database Query:
        Joins teams with team_members to get user's teams and roles,
        then counts members for each team.
    """
    # Query teams where user is a member
    statement = (
        select(Team, TeamMember.role)
        .join(TeamMember, Team.id == TeamMember.team_id)
        .where(TeamMember.user_id == user_id)
        .order_by(Team.created_at.desc())
    )

    results = db.exec(statement).all()

    # Build response with member counts
    teams_with_info = []
    for team, role in results:
        # Count members for this team
        member_count_statement = select(TeamMember).where(TeamMember.team_id == team.id)
        member_count = len(db.exec(member_count_statement).all())

        teams_with_info.append({
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "role": role.value,
            "member_count": member_count,
            "created_at": team.created_at
        })

    return teams_with_info


def get_team_details(db: Session, team_id: str) -> Optional[dict]:
    """
    Get detailed team information including all members.

    Returns complete team information with a list of all members,
    their roles, and email addresses.

    Args:
        db: Database session
        team_id: Team ID to get details for

    Returns:
        Dictionary containing team info and members list, or None if not found:
        {
            "id": "team-uuid",
            "name": "Team Name",
            "description": "Team description",
            "owner_id": "owner-uuid",
            "created_at": datetime,
            "updated_at": datetime,
            "members": [
                {
                    "user_id": "user-uuid",
                    "email": "user@example.com",
                    "role": "owner",
                    "joined_at": datetime
                }
            ]
        }

    Example:
        ```python
        team_details = get_team_details(db, "team-uuid")
        if team_details:
            print(f"Team: {team_details['name']}")
            print(f"Members: {len(team_details['members'])}")
        ```

    Database Query:
        Retrieves team and joins with team_members and users to get
        complete member information.
    """
    # Get team
    team = db.get(Team, team_id)
    if not team:
        return None

    # Get all members with user info
    statement = (
        select(TeamMember, User)
        .join(User, TeamMember.user_id == User.id)
        .where(TeamMember.team_id == team_id)
        .order_by(TeamMember.joined_at)
    )

    member_results = db.exec(statement).all()

    # Build members list
    members = []
    for membership, user in member_results:
        members.append({
            "user_id": membership.user_id,
            "email": user.email,
            "role": membership.role.value,
            "joined_at": membership.joined_at
        })

    return {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "owner_id": team.owner_id,
        "created_at": team.created_at,
        "updated_at": team.updated_at,
        "members": members
    }


def update_team(
    db: Session,
    team_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Optional[Team]:
    """
    Update team name and/or description.

    Updates only the provided fields. If a field is None, it is not updated.

    Args:
        db: Database session
        team_id: Team ID to update
        name: New team name (optional, must be unique)
        description: New team description (optional)

    Returns:
        Updated Team object, or None if team not found

    Raises:
        IntegrityError: If new name already exists

    Example:
        ```python
        team = update_team(
            db=db,
            team_id="team-uuid",
            description="Updated description"
        )
        ```

    Database Operations:
        1. Retrieve team by ID
        2. Update provided fields
        3. Commit transaction
        4. Refresh to get updated timestamp
    """
    # Get team
    team = db.get(Team, team_id)
    if not team:
        return None

    try:
        # Update provided fields
        if name is not None:
            team.name = name.strip()

        if description is not None:
            team.description = description.strip() if description else None

        # Update timestamp
        from datetime import datetime
        team.updated_at = datetime.utcnow()

        # Commit changes
        db.add(team)
        db.commit()
        db.refresh(team)

        return team

    except IntegrityError:
        db.rollback()
        raise


def delete_team(db: Session, team_id: str) -> bool:
    """
    Delete a team and convert all team tasks to personal tasks.

    This function deletes the team and all team memberships (CASCADE),
    and sets team_id to NULL for all tasks owned by the team (converting
    them to personal tasks). All operations are performed in a single
    transaction.

    Args:
        db: Database session
        team_id: Team ID to delete

    Returns:
        True if team was deleted, False if team not found

    Example:
        ```python
        success = delete_team(db, "team-uuid")
        if success:
            print("Team deleted successfully")
        ```

    Database Operations:
        1. Convert team tasks to personal tasks (set team_id = NULL)
        2. Delete team (CASCADE deletes team_members automatically)
        3. Commit transaction
    """
    # Get team
    team = db.get(Team, team_id)
    if not team:
        return False

    try:
        # Convert team tasks to personal tasks
        statement = select(Task).where(Task.team_id == team_id)
        team_tasks = db.exec(statement).all()

        for task in team_tasks:
            task.team_id = None
            db.add(task)

        # Delete team (CASCADE will delete team_members)
        db.delete(team)

        # Commit transaction
        db.commit()

        return True

    except Exception:
        db.rollback()
        raise


def get_team_by_id(db: Session, team_id: str) -> Optional[Team]:
    """
    Retrieve a team by its unique ID.

    Args:
        db: Database session
        team_id: Team's unique identifier (UUID string)

    Returns:
        Team object if found, None otherwise

    Example:
        ```python
        team = get_team_by_id(db, "550e8400-e29b-41d4-a716-446655440000")
        if team:
            print(f"Found team: {team.name}")
        ```
    """
    return db.get(Team, team_id)


def get_team_by_name(db: Session, name: str) -> Optional[Team]:
    """
    Retrieve a team by name (case-sensitive).

    Args:
        db: Database session
        name: Team name to search for

    Returns:
        Team object if found, None otherwise

    Example:
        ```python
        team = get_team_by_name(db, "Engineering Team")
        if team:
            print(f"Found team: {team.id}")
        ```
    """
    statement = select(Team).where(Team.name == name)
    return db.exec(statement).first()
