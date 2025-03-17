"""
Handle Reporting Service.

This module handles report generation logic for the Time Tracker Console
Application. It includes functions for generating and viewing reports of time
entries, filtered by various criteria.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from src.data_loader.time_tracker_database import TimeTrackerDatabase
from src.models.time_tracker import TimeTracker
from src.services.task_service import TaskService


class ReportService:
    """Service class for generating time tracking reports."""

    def __init__(
        self,
        db: Optional[TimeTrackerDatabase] = None,
        task_service: Optional[TaskService] = None,
    ) -> None:
        """Initialize the report service with a database instance and \
task service.

        Args:
            db (Optional[TimeTrackerDatabase], optional): Time tracker database
            instance. Defaults to None.
            task_service (Optional[TaskService], optional): Task service
            instance. Defaults to None.
        """
        self.db = db if db is not None else TimeTrackerDatabase()
        self.task_service = (
            task_service if task_service is not None else TaskService()
        )

    def get_time_trackers_by_user(self, user_id: int) -> List[TimeTracker]:
        """Retrieve all time trackers for a given user.

        Args:
            user_id (int): The user ID.

        Returns:
            List[TimeTracker]: A list of time trackers for the user.
        """
        return self.db.get_time_trackers_by_user(user_id)

    def get_time_trackers_by_user_and_date(
        self, user_id: int, date: date
    ) -> List[TimeTracker]:
        """Retrieve time trackers for a given user and date.

        Args:
            user_id (int): The user ID.
            date (date): The date to filter by.

        Returns:
            List[TimeTracker]: A list of time trackers for the user and date.
        """
        return self.db.get_time_trackers_by_user_and_date(user_id, date)

    def get_time_trackers_by_user_and_date_range(
        self, user_id: int, start_date: date, end_date: date
    ) -> List[TimeTracker]:
        """Retrieve time trackers for a given user and date range.

        Args:
            user_id (int): The user ID.
            start_date (date): The start date of the range.
            end_date (date): The end date of the range.

        Returns:
            List[TimeTracker]: A list of time trackers for the user and date
            range.
        """
        return self.db.get_time_trackers_by_user_and_date_range(
            user_id, start_date, end_date
        )

    def get_category_insights(
        self, time_trackers: List[TimeTracker]
    ) -> Dict[str, float]:
        """Generate insights based on categories.

        Args:
            time_trackers (List[TimeTracker]): A list of time trackers.

        Returns:
            Dict[str, float]: A dictionary of category insights.
        """
        categories: Dict[str, float] = {}
        for tracker in time_trackers:
            if tracker.category not in categories:
                categories[tracker.category] = 0.0
            categories[tracker.category] += tracker.total_time

        # Filter out categories with zero total time
        frequent_categories = {k: v for k, v in categories.items() if v > 0}
        return frequent_categories

    def get_task_insights(
        self, time_trackers: List[TimeTracker], user_id: int
    ) -> List[Dict[str, Any]]:
        """Generate insights for each task.

        Args:
            time_trackers (List[TimeTracker]): A list of time trackers.
            user_id (int): The user ID.

        Returns:
            List[Dict[str, Any]]: A list of task insights.
        """
        task_insights = []
        for tracker in time_trackers:
            task = self.task_service.get_task_by_id(
                user_id, tracker.task_id
            )  # Pass user_id explicitly
            if task:
                task_insights.append(
                    {
                        "task_id": tracker.task_id,
                        "task_name": task.task_name,
                        "category": tracker.category,
                        "start_time": tracker.start_time,
                        "stop_time": tracker.stop_time,
                        "total_time": tracker.total_time,
                        "estimated_duration": task.duration,
                        "status": tracker.status,
                    }
                )
        return task_insights

    def get_task_duration_insights(self, task_id: int, user_id: int) -> str:
        """Generate insights about task duration.

        Args:
            task_id (int): The task ID.
            user_id (int): The user ID.

        Returns:
            str: A message with insights about the task duration.
        """
        task = self.task_service.get_task_by_id(user_id, task_id)
        if not task:
            return "Task not found."

        time_tracker = self.db.get_active_time_tracker(task_id)
        if not time_tracker or time_tracker.status != "Completed":
            return "Task not completed."

        elapsed_time = time_tracker.total_time
        estimated_duration = task.duration

        if elapsed_time < estimated_duration:
            return f"Task completed {estimated_duration - elapsed_time:.2f} \
                seconds early."
        elif elapsed_time > estimated_duration:
            return f"Task delayed by {elapsed_time - estimated_duration:.2f} \
                seconds."
        else:
            return "Task completed exactly on time."

    def get_total_time(self, time_trackers: List[TimeTracker]) -> float:
        """Calculate the total time spent on tasks.

        Args:
            time_trackers (List[TimeTracker]): A list of time trackers.

        Returns:
            float: The total time spent on tasks.
        """
        return sum(tracker.total_time for tracker in time_trackers)
