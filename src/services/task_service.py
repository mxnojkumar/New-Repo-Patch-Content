"""
Handles Task CRUD operations.

This module contains the TaskService class, which is responsible for managing
tasks in the application.
It provides methods for creating, reading, updating, and deleting tasks, as
well as updating task status.
"""

from typing import List, Optional

from src.data_loader.category_database import CategoryDatabase
from src.data_loader.task_database import TaskDatabase
from src.models.task import Task


class TaskService:
    """Service class for managing tasks."""

    def __init__(
        self,
        task_db: Optional[TaskDatabase] = None,
        category_db: Optional[CategoryDatabase] = None,
    ) -> None:
        """Initialize the task service with database instances.

        Args:
            task_db (Optional[TaskDatabase], optional): The task database
            instance. Defaults to None.
            category_db (Optional[CategoryDatabase], optional): The category
            database instance. Defaults to None.
        """
        self.task_db = task_db if task_db is not None else TaskDatabase()
        self.category_db = (
            category_db if category_db is not None else CategoryDatabase()
        )

    def create_task(
        self,
        user_id: int,
        category_name: str,
        task_name: str,
        duration: float = 0.0,
    ) -> Task:
        """Create a new task, ensuring category exists.

        Args:
            user_id (int): The user ID.
            category_name (str): The category name.
            task_name (str): The task name.
            duration (float, optional): The task duration. Defaults to 0.0.

        Raises:
            ValueError: If the category could not be created or retrieved.

        Returns:
            Task: The created task.
        """
        category = self.category_db.get_or_create_category(category_name)
        if category is None or "":
            raise ValueError(
                f"Category '{category_name}' "
                "could not be created or retrieved."
            )
        new_task = Task.create(
            user_id=user_id,
            category_name=category_name,
            task_name=task_name,
            duration=duration,
            task_status="Not Started",
        )
        self.task_db.save_task(new_task)
        return new_task

    def get_tasks(self, user_id: int) -> List[Task]:
        """Retrieve all tasks for a given user.

        Args:
            user_id (int): The user ID.

        Returns:
            List[Task]: A list of tasks for the given user.
        """
        return self.task_db.get_tasks_by_user(user_id)

    def get_task_by_id(self, user_id: int, task_id: int) -> Optional[Task]:
        """Retrieve a task by its ID for the given user.

        Args:
            user_id (int): The user ID.
            task_id (int): The task ID.

        Returns:
            Optional[Task]: The task if found, otherwise None.
        """
        tasks = self.task_db.get_tasks_by_user(user_id)
        for task in tasks:
            if task.id == task_id:
                return task
        return None

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
            user_id (int): The user ID.
            task_id (int): The task ID.
            category_name (str): The category name.
            task_name (str): The task name.
            duration (float): The task duration.
        """
        try:
            if (
                category_name
                and category_name.strip()
                and task_name
                and task_name.strip()
            ):
                self.task_db.update_task(
                    user_id, task_id, category_name, task_name, duration
                )
        except ValueError as err:
            raise ValueError(err)

    def update_task_status(self, task_id: int, status: str) -> None:
        """Update the status of a task.

        Args:
            task_id (int): The task ID.
            status (str): The new status.
        """
        self.task_db.update_task_status(task_id, status)

    def delete_task(self, user_id: int, task_id: int) -> None:
        """Delete a task by task ID for the given user.

        Args:
            user_id (int): The user ID.
            task_id (int): The task ID.
        """
        self.task_db.delete_task(user_id, task_id)
