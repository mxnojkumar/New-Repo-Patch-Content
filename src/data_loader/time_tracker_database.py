"""
time_tracker_database.py module.

This module handles database operations for the TimeTracker model.
"""

import sqlite3
from datetime import date, datetime
from sqlite3 import Connection, Error
from typing import List, Optional

from src.models.time_tracker import TimeTracker


class TimeTrackerDatabase:
    """Database class for managing time tracking data."""

    def __init__(
        self,
        db_path: str = "src/database/timings.db",
        tasks_db_path: str = "src/database/tasks.db",
    ) -> None:
        """Initialize the database connection and ensure the time trackers \
table exists.

        Args:
            db_path (str, optional): Path to the SQLite database file. Defaults
            to "src/database/timings.db".
            tasks_db_path (str, optional): Path to the tasks database file.
            Defaults to "src/database/tasks.db".
        """
        self.db_path = db_path
        self.tasks_db_path = tasks_db_path
        self.conn: Optional[Connection] = None
        self.connect()
        self.create_time_trackers_table()

    def connect(self) -> None:
        """Establish a connection to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            # Attach the tasks database
            self.conn.execute(
                f"ATTACH DATABASE '{self.tasks_db_path}' AS tasks_db"
            )
        except Error as e:
            raise Exception(f"Error connecting to database: {e}")

    def create_time_trackers_table(self) -> None:
        """Create the time trackers table if it doesn't exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS time_trackers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            start_time TEXT,
            stop_time TEXT,
            status TEXT NOT NULL,
            total_time REAL DEFAULT 0
        );
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(create_table_sql)
                self.conn.commit()
        except Error as e:
            raise Exception(f"Error creating time trackers table: {e}")

    def save_time_tracker(self, time_tracker: TimeTracker) -> None:
        """
        Save a new time tracker to the database.

        Args:
            time_tracker (TimeTracker): The time tracker instance to save.
        """
        insert_sql = """
        INSERT INTO time_trackers (task_id, category, start_time, stop_time,
        status, total_time)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    insert_sql,
                    (
                        time_tracker.task_id,
                        time_tracker.category,  # Added category
                        time_tracker.start_time.isoformat()
                        if time_tracker.start_time
                        else None,
                        time_tracker.stop_time.isoformat()
                        if time_tracker.stop_time
                        else None,
                        time_tracker.status,
                        time_tracker.total_time,
                    ),
                )
                self.conn.commit()
        except Error as e:
            raise Exception(f"Error saving time tracker: {e}")

    def update_time_tracker(self, time_tracker: TimeTracker) -> None:
        """
        Update an existing time tracker in the database.

        Args:
            time_tracker (TimeTracker): The time tracker instance to update.
        """
        update_sql = """
        UPDATE time_trackers
        SET start_time = ?, stop_time = ?, status = ?, total_time = ?
        WHERE id = ?
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    update_sql,
                    (
                        time_tracker.start_time.isoformat()
                        if time_tracker.start_time
                        else None,
                        time_tracker.stop_time.isoformat()
                        if time_tracker.stop_time
                        else None,
                        time_tracker.status,
                        time_tracker.total_time,
                        time_tracker.id,
                    ),
                )
                self.conn.commit()
        except Error as e:
            raise Exception(f"Error updating time tracker: {e}")

    def get_active_time_tracker(self, task_id: int) -> Optional[TimeTracker]:
        """
        Retrieve the active time tracker for a task.

        Args:
            task_id (int): The task ID.
        """
        select_sql = """
        SELECT * FROM time_trackers
        WHERE task_id = ? AND status != 'Completed'
        ORDER BY id DESC
        LIMIT 1
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(select_sql, (task_id,))
                row = cursor.fetchone()
                if row:
                    return TimeTracker(
                        id=row["id"],
                        task_id=row["task_id"],
                        category=row["category"],  # Added category
                        start_time=datetime.fromisoformat(row["start_time"])
                        if row["start_time"]
                        else None,
                        stop_time=datetime.fromisoformat(row["stop_time"])
                        if row["stop_time"]
                        else None,
                        status=row["status"],
                        total_time=row["total_time"],
                    )
        except Error as e:
            raise Exception(f"Error retrieving active time tracker: {e}")
        return None

    def get_last_paused_time_tracker(
        self, task_id: int
    ) -> Optional[TimeTracker]:
        """Retrieve the last paused time tracker for a task."""
        select_sql = """
        SELECT * FROM time_trackers
        WHERE task_id = ? AND status = 'Paused'
        ORDER BY id DESC
        LIMIT 1
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(select_sql, (task_id,))
                row = cursor.fetchone()
                if row:
                    return TimeTracker(
                        id=row["id"],
                        task_id=row["task_id"],
                        category=row["category"],  # Added category
                        start_time=datetime.fromisoformat(row["start_time"])
                        if row["start_time"]
                        else None,
                        stop_time=datetime.fromisoformat(row["stop_time"])
                        if row["stop_time"]
                        else None,
                        status=row["status"],
                        total_time=row["total_time"],
                    )
        except Error as e:
            raise Exception(f"Error retrieving last paused time tracker: {e}")
        return None

    def get_time_trackers_by_user(self, user_id: int) -> List[TimeTracker]:
        """Retrieve all time trackers for a given user."""
        select_sql = """
        SELECT * FROM time_trackers
        WHERE task_id IN (SELECT id FROM tasks_db.tasks WHERE user_id = ?)
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(select_sql, (user_id,))
                rows = cursor.fetchall()
                return [
                    TimeTracker(
                        id=row["id"],
                        task_id=row["task_id"],
                        category=row["category"],
                        start_time=datetime.fromisoformat(row["start_time"])
                        if row["start_time"]
                        else None,
                        stop_time=datetime.fromisoformat(row["stop_time"])
                        if row["stop_time"]
                        else None,
                        status=row["status"],
                        total_time=row["total_time"],
                    )
                    for row in rows
                ]
        except Error as e:
            raise Exception(f"Error retrieving time trackers by user: {e}")
        return []

    def get_time_trackers_by_user_and_date(
        self, user_id: int, date: date
    ) -> List[TimeTracker]:
        """Retrieve time trackers for a given user and date."""
        select_sql = """
        SELECT * FROM time_trackers
        WHERE task_id IN (SELECT id FROM tasks WHERE user_id = ?)
        AND DATE(start_time) = ?
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(select_sql, (user_id, date.isoformat()))
                rows = cursor.fetchall()
                return [
                    TimeTracker(
                        id=row["id"],
                        task_id=row["task_id"],
                        category=row["category"],  # Added category
                        start_time=datetime.fromisoformat(row["start_time"])
                        if row["start_time"]
                        else None,
                        stop_time=datetime.fromisoformat(row["stop_time"])
                        if row["stop_time"]
                        else None,
                        status=row["status"],
                        total_time=row["total_time"],
                    )
                    for row in rows
                ]
        except Error as e:
            raise Exception(
                f"Error retrieving time trackers by user and date: {e}"
            )
        return []

    def get_time_trackers_by_user_and_date_range(
        self, user_id: int, start_date: date, end_date: date
    ) -> List[TimeTracker]:
        """Retrieve time trackers for a given user and date range."""
        select_sql = """
        SELECT * FROM time_trackers
        WHERE task_id IN (SELECT id FROM tasks WHERE user_id = ?)
        AND DATE(start_time) BETWEEN ? AND ?
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    select_sql,
                    (user_id, start_date.isoformat(), end_date.isoformat()),
                )
                rows = cursor.fetchall()
                return [
                    TimeTracker(
                        id=row["id"],
                        task_id=row["task_id"],
                        category=row["category"],  # Added category
                        start_time=datetime.fromisoformat(row["start_time"])
                        if row["start_time"]
                        else None,
                        stop_time=datetime.fromisoformat(row["stop_time"])
                        if row["stop_time"]
                        else None,
                        status=row["status"],
                        total_time=row["total_time"],
                    )
                    for row in rows
                ]
        except Error as e:
            raise Exception(
                f"Error retrieving time trackers by user and date range: {e}"
            )
        return []

    def get_time_trackers_by_task(self, task_id: int) -> List[TimeTracker]:
        """Retrieve all time trackers for a specific task.

        Args:
            task_id (int): The task ID.

        Returns:
            List[TimeTracker]: A list of time trackers for the task.
        """
        select_sql = """
        SELECT * FROM time_trackers
        WHERE task_id = ?
        ORDER BY id DESC
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(select_sql, (task_id,))
                rows = cursor.fetchall()
                return [
                    TimeTracker(
                        id=row["id"],
                        task_id=row["task_id"],
                        category=row["category"],
                        start_time=datetime.fromisoformat(row["start_time"])
                        if row["start_time"]
                        else None,
                        stop_time=datetime.fromisoformat(row["stop_time"])
                        if row["stop_time"]
                        else None,
                        status=row["status"],
                        total_time=row["total_time"],
                    )
                    for row in rows
                ]
        except Error as e:
            raise Exception(f"Error retrieving time trackers by task: {e}")
        return []