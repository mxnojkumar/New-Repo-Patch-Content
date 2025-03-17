"""
Defines the TimeTracker model.

This module represents a time tracker model with id, task_id, category, task,
status, start_time, pause_time, resume_time, stop_time, and total_time.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TimeTracker(BaseModel):
    """Represent a time tracker model for tracking task timings."""

    id: Optional[int] = None
    task_id: int
    category: str
    start_time: Optional[datetime] = None
    stop_time: Optional[datetime] = None
    status: str
    total_time: float = 0.0

    @classmethod
    def create(cls, task_id: int, status: str, category: str) -> "TimeTracker":
        """Create a new TimeTracker instance.

        Args:
            task_id (int): Task ID.
            status (str): Status of the task.
            category (str): Category of the task.

        Returns:
            TimeTracker: A new TimeTracker instance.
        """
        return cls(task_id=task_id, status=status, category=category)
