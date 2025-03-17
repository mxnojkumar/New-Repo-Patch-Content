"""
Defines Task model.

This module represents a task model with id, category, task, task_duration, and
owner_id.
"""

from typing import Optional

from pydantic import BaseModel, field_validator


class Task(BaseModel):
    """Represent a task model using Pydantic for validation."""

    id: Optional[int] = None
    user_id: int
    category_name: str
    task_name: str
    duration: float = 0.0
    task_status: str

    @field_validator("category_name", "task_name", "task_status")
    def not_empty(cls, value: str) -> str:
        """Validate that the task entities are not empty.

        Args:
            value (str): The value to validate.

        Raises:
            ValueError: If the value is empty.

        Returns:
            str: The value if it is not empty.
        """
        if not value or value.strip() == "":
            raise ValueError("Task entities must not be Empty!.")
        return value

    @classmethod
    def create(
        cls,
        user_id: int,
        category_name: str,
        task_name: str,
        duration: float,
        task_status: str,
    ) -> "Task":
        """
        Create new task.

        Factory method to create a new Task instance.

        Args:
            user_id (int): The user's unique identifier.
            category_id (int): The category's unique identifier.
            task_name (str): The task name.
            duration (float, optional): The task duration. Defaults to 0.0.

        Returns:
            Task: A new Task instance.
        """
        return cls(
            user_id=user_id,
            category_name=category_name,
            task_name=task_name,
            duration=duration,
            task_status=task_status,
        )
