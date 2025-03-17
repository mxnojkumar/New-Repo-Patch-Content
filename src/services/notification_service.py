"""Handle Notification Service.

This module handles notifying the user when the estimated duration is reached.
"""

from datetime import datetime
import time
from typing import Optional
from rich.console import Console

from src.data_loader.task_database import TaskDatabase
from src.data_loader.time_tracker_database import TimeTrackerDatabase
from src.services.task_service import TaskService
from src.services.time_tracker_service import TimeTrackerService


class NotificationService:
    """Service class for handling notifications."""

    def __init__(
        self,
        task_service: Optional[TaskService] = None,
        time_tracker_service: Optional[TimeTrackerService] = None,
    ) -> None:
        """Initialize the notification service with task and time tracker services.

        Args:
            task_service (Optional[TaskService], optional): Task service instance. Defaults to None.
            time_tracker_service (Optional[TimeTrackerService], optional): Time tracker service instance. Defaults to None.
        """
        self.task_service = task_service if task_service is not None else TaskService()
        self.time_tracker_service = time_tracker_service if time_tracker_service is not None else TimeTrackerService()
        self.console = Console()

    def notify_user(self, task_id: int, user_id: int) -> None:
        """Notify the user when the estimated duration is reached.

        Args:
            task_id (int): The task ID.
            user_id (int): The user ID.
        """
        # Create a new database connection for this thread
        task_db = TaskDatabase()
        time_tracker_db = TimeTrackerDatabase()

        # Create new service instances with the new database connections
        task_service = TaskService(task_db=task_db)
        time_tracker_service = TimeTrackerService(db=time_tracker_db)

        task = task_service.get_task_by_id(user_id, task_id)
        if not task or not task.duration:
            return

        estimated_duration = task.duration
        elapsed_time = 0.0

        while True:
            time_tracker = time_tracker_service.get_active_time_tracker(task_id)
            if not time_tracker or time_tracker.status != "In Progress":
                break

            # Calculate elapsed time
            if time_tracker.start_time:
                elapsed_time = (datetime.now() - time_tracker.start_time).total_seconds()
                elapsed_time += time_tracker.total_time or 0.0

            # Check if elapsed time exceeds estimated duration
            if elapsed_time >= estimated_duration:
                self.console.print(
                    f"[bold yellow]Notification: Task {task.task_name} has reached its estimated duration of {estimated_duration} seconds![/bold yellow]"
                )
                # Display the notification for 5 seconds
                time.sleep(5)
                break

            time.sleep(1)  # Check every second
