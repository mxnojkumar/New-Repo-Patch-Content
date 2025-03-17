"""
Defines User model.

This module represents a user model with id, email, password and created_at
attributes.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """Represent a user model using Pydantic for validation."""

    id: Optional[int] = None
    email: EmailStr
    hashed_password: str
    created_at: datetime

    @classmethod
    def create(cls, email: EmailStr, hashed_password: str) -> "User":
        """
        Create new user.

        Creates a new User instance with a unique UUID, email, hashed password
        and created_at timing.

        Args:
            email (EmailStr): The user's validated email.
            hashed_password (str): The hashed password.

        Returns:
            User: A new User instance.
        """
        return cls(
            email=email,
            hashed_password=hashed_password,
            created_at=datetime.now(timezone.utc),
        )
