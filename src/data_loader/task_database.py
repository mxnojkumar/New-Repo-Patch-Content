"""
task_database.py module.

This module contains the TaskDatabase class, which is responsible for managing
tasks in the database.
The class provides methods for saving, retrieving, updating, and deleting tasks
from the database.
"""

import sqlite3
from sqlite3 import Connection, Error
from typing import List, Optional

from src.models.task import Task


class TaskDatabase:
    """Database class for managing tasks."""

    def __init__(self, db_path: str = "src/database/tasks.db") -> None:
        """Initialize the TaskDatabase class.

        Args:
            db_path (str, optional): The path to the SQLite database file.
            Defaults to "src/database/tasks.db".
        """
        self.db_path = db_path
        self.conn: Optional[Connection] = None
        self.connect()
        self.create_tasks_table()

    def connect(self) -> None:
        """Establish a connection to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        except Error as e:
            raise Exception(f"Error connecting to database: {e}")

    def create_tasks_table(self) -> None:
        """Create the tasks table if it doesn't exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_name TEXT NOT NULL,
            task_name TEXT NOT NULL,
            duration REAL DEFAULT 0,
            task_status TEXT NOT NULL,
            FOREIGN KEY (category_name) REFERENCES categories(name)
        );
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(create_table_sql)
                self.conn.commit()
        except Error as e:
            raise Exception(f"Error creating tasks table: {e}")

    def save_task(self, task: Task) -> Optional[Task]:
        """Save a new task into the database.

        Args:
            task (Task): The task to be saved.

        Raises:
            Exception: When an error occurs while saving the task.

        Returns:
            Optional[Task]: The saved task with the generated ID.
        """
        insert_sql = """
        INSERT INTO tasks (user_id, category_name, task_name, duration,
        task_status) VALUES (?, ?, ?, ?, ?)
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    insert_sql,
                    (
                        task.user_id,
                        task.category_name,
                        task.task_name,
                        task.duration,
                        task.task_status,
                    ),
                )
                self.conn.commit()
                task.id = cursor.lastrowid  # Set the generated ID for the task
                return task
            return None
        except Error as e:
            raise Exception(f"Error saving task: {e}")

    def get_tasks_by_user(self, user_id: int) -> List[Task]:
        """Retrieve all tasks for a given user.

        Args:
            user_id (int): The ID of the user.

        Raises:
            Exception: When an error occurs while retrieving tasks.

        Returns:
            List[Task]: A list of tasks for the given user.
        """
        select_sql = "SELECT * FROM tasks WHERE user_id = ?"
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(select_sql, (user_id,))
                rows = cursor.fetchall()
                return [
                    Task(
                        id=row["id"],
                        user_id=row["user_id"],
                        category_name=row["category_name"],
                        task_name=row["task_name"],
                        duration=row["duration"],
                        task_status=row["task_status"],
                    )
                    for row in rows
                ]
        except Error as e:
            raise Exception(f"Error retrieving tasks: {e}")
        return []

    def update_task(
        self,
        user_id: int,
        task_id: int,
        category_name: str,
        task_name: str,
        duration: float,
    ) -> None:
        """Update a task by task ID for the given user.

        Args:
            user_id (int): The ID of the user.
            task_id (int): The ID of the task to update.
            category_name (str): The name of the category.
            task_name (str): The name of the task.
            duration (float): The duration of the task.

        Raises:
            Exception: When an error occurs while updating the task.
            Exception: When the task ID is invalid or non-existing.
        """
        check_sql = "SELECT COUNT() FROM tasks WHERE id = ? AND user_id = ?"
        update_sql = """
        UPDATE tasks
        SET category_name = ?, task_name = ?, duration = ?
        WHERE id = ? AND user_id = ?
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                # Check if task exists
                cursor.execute(check_sql, (task_id, user_id))
                count = cursor.fetchone()[0]
                if count == 0:
                    raise Exception(
                        f"No task found with ID {task_id} for user {user_id}."
                    )
                # Proceed with the update
                cursor.execute(
                    update_sql,
                    (category_name, task_name, duration, task_id, user_id),
                )
                self.conn.commit()
        except Error as e:
            raise Exception(f"Error updating task: {e}")

    def update_task_status(self, task_id: int, status: str) -> None:
        """Update the status of a task.

        Args:
            task_id (int): The ID of the task to update.
            status (str): The new status of the task.

        Raises:
            Exception: When an error occurs while updating the task status.
        """
        update_sql = "UPDATE tasks SET task_status = ? WHERE id = ?"
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(update_sql, (status, task_id))
                self.conn.commit()
        except Error as e:
            raise Exception(f"Error updating task status: {e}")

    def delete_task(self, user_id: int, task_id: int) -> None:
        """Delete a task by task ID for the given user.

        Args:
            user_id (int): The ID of the user.
            task_id (int): The ID of the task to delete.

        Raises:
            Exception: When an error occurs while deleting the task.
            Exception: When the task ID is invalid or non-existing.
        """
        check_sql = "SELECT COUNT() FROM tasks WHERE id = ? AND user_id = ?"
        delete_sql = "DELETE FROM tasks WHERE id = ? AND user_id = ?"
        try:
            if self.conn:
                cursor = self.conn.cursor()
                # Check if task exists
                cursor.execute(check_sql, (task_id, user_id))
                count = cursor.fetchone()[0]
                if count == 0:
                    raise Exception(
                        f"No task found with ID {task_id} for user {user_id}."
                    )
                # Proceed with deletion
                cursor.execute(delete_sql, (task_id, user_id))
                self.conn.commit()
        except Error as e:
            raise Exception(f"Error deleting task: {e}")
