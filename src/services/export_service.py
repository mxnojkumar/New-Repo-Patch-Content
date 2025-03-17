"""Handle Data Export Service.

This module handles exporting time tracking data to a CSV file.
"""

import csv
from datetime import datetime, timedelta
from typing import Optional

from src.data_loader.time_tracker_database import TimeTrackerDatabase
from src.models.time_tracker import TimeTracker


class ExportService:
    """Service class for exporting time tracking data."""

    def __init__(self, db: Optional[TimeTrackerDatabase] = None) -> None:
        """Initialize the export service with a database instance.

        Args:
            db (Optional[TimeTrackerDatabase], optional): Time tracker database
            instance. Defaults to None.
        """
        self.db = db if db is not None else TimeTrackerDatabase()

    def export_to_csv(self, user_id: int, report_type: str, duration: Optional[int] = None) -> str:
        """Export time tracking data to a CSV file.

        Args:
            user_id (int): The user ID.
            report_type (str): The type of report (e.g., overall, daily, weekly, etc.).
            duration (Optional[int], optional): The duration for custom reports. Defaults to None.

        Returns:
            str: The path to the exported CSV file.
        """
        # Get time trackers based on the report type
        if report_type == "overall":
            time_trackers = self.db.get_time_trackers_by_user(user_id)
        elif report_type == "daily":
            time_trackers = self.db.get_time_trackers_by_user_and_date(user_id, datetime.now().date())
        elif report_type == "weekly":
            start_date = datetime.now().date() - timedelta(days=7)
            time_trackers = self.db.get_time_trackers_by_user_and_date_range(user_id, start_date, datetime.now().date())
        elif report_type == "monthly":
            start_date = datetime.now().date() - timedelta(days=30)
            time_trackers = self.db.get_time_trackers_by_user_and_date_range(user_id, start_date, datetime.now().date())
        elif report_type == "custom" and duration:
            start_date = datetime.now().date() - timedelta(days=duration)
            time_trackers = self.db.get_time_trackers_by_user_and_date_range(user_id, start_date, datetime.now().date())
        else:
            raise ValueError("Invalid report type or duration.")

        # Generate CSV file
        filename = f"time_tracker_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Task ID", "Category", "Start Time", "Stop Time", "Total Time (seconds)", "Status"])
            for tracker in time_trackers:
                writer.writerow([
                    tracker.task_id,
                    tracker.category,
                    tracker.start_time.isoformat() if tracker.start_time else "",
                    tracker.stop_time.isoformat() if tracker.stop_time else "",
                    tracker.total_time,
                    tracker.status,
                ])

        return filename