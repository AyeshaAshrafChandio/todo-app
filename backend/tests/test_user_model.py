"""
Unit tests for User SQLModel.

Tests cover:
- User creation with valid data
- Email uniqueness constraint
- Password hash validation
- Timestamp auto-generation
- UUID primary key generation
"""

import pytest
from datetime import datetime
from sqlmodel import Session, select
from app.models.user import User


class TestUserModel:
    """Test suite for User model."""

    def test_create_user_with_valid_data(self, session):
        """Test creating a user with valid email and password hash."""
        # Arrange
        user = User(
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
        )

        # Act
        session.add(user)
        session.commit()
        session.refresh(user)

        # Assert
        assert user.id is not None
        assert len(user.id) == 36  # UUID length
        assert user.email == "test@example.com"
        assert user.password_hash.startswith("$2b$12$")
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_id_auto_generated(self, session):
        """Test that user ID is automatically generated as UUID."""
        # Arrange
        user = User(
            email="auto@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
        )

        # Act
        session.add(user)
        session.commit()
        session.refresh(user)

        # Assert
        assert user.id is not None
        # UUID format: 8-4-4-4-12 characters
        parts = user.id.split('-')
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

    def test_email_uniqueness_constraint(self, session):
        """Test that duplicate emails are rejected."""
        # Arrange
        user1 = User(
            email="duplicate@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
        )
        user2 = User(
            email="duplicate@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
        )

        # Act & Assert
        session.add(user1)
        session.commit()

        session.add(user2)
        with pytest.raises(Exception):  # IntegrityError or similar
            session.commit()

    def test_password_hash_minimum_length(self, session):
        """Test that password hash must be at least 60 characters."""
        # Arrange - bcrypt hash is exactly 60 characters
        valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
        user = User(
            email="hash@example.com",
            password_hash=valid_hash
        )

        # Act
        session.add(user)
        session.commit()
        session.refresh(user)

        # Assert
        assert len(user.password_hash) >= 60
        assert user.password_hash == valid_hash

    def test_timestamps_auto_generated(self, session):
        """Test that created_at and updated_at are automatically set."""
        # Arrange
        before_creation = datetime.utcnow()
        user = User(
            email="timestamp@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
        )

        # Act
        session.add(user)
        session.commit()
        session.refresh(user)
        after_creation = datetime.utcnow()

        # Assert
        assert user.created_at is not None
        assert user.updated_at is not None
        assert before_creation <= user.created_at <= after_creation
        assert before_creation <= user.updated_at <= after_creation

    def test_user_repr(self, session):
        """Test string representation of User."""
        # Arrange
        user = User(
            email="repr@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        # Act
        repr_str = repr(user)

        # Assert
        assert "User(" in repr_str
        assert user.id in repr_str
        assert user.email in repr_str

    def test_query_user_by_email(self, session):
        """Test querying user by email."""
        # Arrange
        user = User(
            email="query@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
        )
        session.add(user)
        session.commit()

        # Act
        found_user = session.exec(
            select(User).where(User.email == "query@example.com")
        ).first()

        # Assert
        assert found_user is not None
        assert found_user.email == "query@example.com"
        assert found_user.id == user.id

    def test_query_user_by_id(self, session):
        """Test querying user by ID."""
        # Arrange
        user = User(
            email="queryid@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        # Act
        found_user = session.exec(
            select(User).where(User.id == user.id)
        ).first()

        # Assert
        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == "queryid@example.com"

    def test_multiple_users_creation(self, session):
        """Test creating multiple users with unique emails."""
        # Arrange
        users = [
            User(
                email=f"user{i}@example.com",
                password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
            )
            for i in range(5)
        ]

        # Act
        for user in users:
            session.add(user)
        session.commit()

        # Assert
        all_users = session.exec(select(User)).all()
        assert len(all_users) == 5

        # Verify all have unique IDs
        user_ids = [u.id for u in all_users]
        assert len(user_ids) == len(set(user_ids))

        # Verify all have unique emails
        emails = [u.email for u in all_users]
        assert len(emails) == len(set(emails))
