"""
Handles task controller.

This module contains the TaskController class which is responsible for handling
task management operations like creating, updating, and deleting tasks.
"""

from datetime import datetime
from typing import Optional

import inquirer  # type: ignore
from rich.console import Console
from rich.panel import Panel

from src.controllers.export_controller import ExportController
from src.controllers.report_controller import ReportController
from src.controllers.time_tracker_controller import TimeTrackerController
from src.services.category_service import CategoryService
from src.services.task_service import TaskService
from src.services.time_tracker_service import TimeTrackerService
from src.utils.helpers import clear_console


class TaskController:
    """Controller for handling task management operations."""

    def __init__(
        self,
        user_id: int,
        task_service: TaskService,
        category_service: CategoryService,
    ) -> None:
        """Initialize the TaskController with user ID, task service, and \
category service.

        Args:
            user_id (int): The ID of the user.
            task_service (TaskService): The task service instance.
            category_service (CategoryService): The category service instance.
        """
        self.user_id = user_id
        self.task_service = task_service
        self.category_service = category_service
        self.console = Console()

    def show_dashboard(self) -> Optional[str]:
        """Display the updated dashboard with current and recent tasks.

        Returns:
            Optional[str]: The action to take after displaying the dashboard.
        """
        tasks = self.task_service.get_tasks(self.user_id)
        current_tasks = [
            task
            for task in tasks
            if task.task_status in ["In Progress", "Paused"]
        ]
        recent_tasks = [
            task for task in tasks if task.task_status == "Completed"
        ]

        self.console.print(
            Panel.fit("[bold magenta]Current Tasks[/bold magenta]")
        )
        if current_tasks:
            for task in current_tasks:
                self.console.print(
                    f"[cyan]Status: {task.task_status}[/cyan] | "
                    f"Task: {task.task_name} | "
                    f"Category: {task.category_name} | "
                )
        else:
            self.console.print("[yellow]No current tasks.[/yellow]")

        self.console.print(
            Panel.fit("[bold magenta]Recent Tasks[/bold magenta]")
        )
        if recent_tasks:
            for task in recent_tasks:
                self.console.print(
                    f"[cyan]Status: {task.task_status}[/cyan] | "
                    f"Task: {task.task_name} | "
                    f"Category: {task.category_name}"
                )
        else:
            self.console.print("[yellow]No recent tasks.[/yellow]")

        return None

    def show_task_menu(self) -> Optional[str]:
        """Display the task management menu with dynamic options.

        Returns:
            Optional[str]: The action to take after displaying the task menu.
        """
        tasks = self.task_service.get_tasks(self.user_id)
        time_tracker_service = TimeTrackerService()

        task_choices = [
            ("Create New Task", "create"),
            *[
                (
                    f"Status: {task.task_status} | "
                    f"Task: {task.task_name} | "
                    f"Category: {task.category_name} | "
                    f"Estimated duration: {task.duration}s | "
                    f"Elapsed time: {self._get_elapsed_time(task.id if task.id else 0, time_tracker_service)}s",
                    task.id,
                )
                for task in tasks
            ],
            ("Generate Report", "report"),
            ("Export Data", "export"),
            ("Logout", "logout"),
        ]
        questions = [
            inquirer.List(
                "task",
                message="Select a task or create a new one:",
                choices=task_choices,
            )
        ]
        answers = inquirer.prompt(questions)
        if not answers:
            return None
        selected_task_id = answers["task"]
        if selected_task_id == "create":
            self.create_task()
        elif selected_task_id == "report":
            self.generate_report()
        elif selected_task_id == "export":  # Handle export option
            ExportController(self.user_id).export_data()
        elif selected_task_id == "logout":
            return "logout"
        else:
            self.handle_task_options(int(selected_task_id))
        return None

    def _get_elapsed_time(self, task_id: int, time_tracker_service: TimeTrackerService) -> float:
        """Get the elapsed time for a task based on its status.

        Args:
            task_id (int): The task ID.
            time_tracker_service (TimeTrackerService): The time tracker service instance.

        Returns:
            float: The elapsed time in seconds.
        """
        time_tracker = time_tracker_service.get_active_time_tracker(task_id)
        if not time_tracker:
            # If no active time tracker, check for completed or paused trackers
            time_tracker = time_tracker_service.get_last_paused_time_tracker(task_id)
            if not time_tracker:
                # If no paused tracker, check for completed trackers
                time_trackers = time_tracker_service.db.get_time_trackers_by_task(task_id)
                if time_trackers:
                    time_tracker = time_trackers[-1]  # Get the latest time tracker

        if time_tracker:
            if time_tracker.status == "In Progress":
                # Calculate elapsed time for an active task
                if time_tracker.start_time:
                    elapsed_time = (datetime.now() - time_tracker.start_time).total_seconds()
                    return elapsed_time + (time_tracker.total_time or 0.0)
            elif time_tracker.status in ["Paused", "Completed"]:
                # Return total_time for paused or completed tasks
                return time_tracker.total_time or 0.0

        # Default to 0.0 for not started tasks
        return 0.0

    def generate_report(self) -> None:
        """Generate a report based on user input."""
        questions = [
            inquirer.List(
                "report_type",
                message="Select a report type:",
                choices=[
                    ("Overall", "overall"),
                    ("Daily", "daily"),
                    ("Weekly", "weekly"),
                    ("Monthly", "monthly"),
                    (
                        "Category-wise",
                        "category",
                    ),  # Map "Category-wise" to "category"
                    ("Custom", "custom"),
                ],
            ),
        ]
        answers = inquirer.prompt(questions)
        if not answers:
            return

        report_type = answers["report_type"].lower()
        duration = None
        if report_type == "custom":
            duration_question = [
                inquirer.Text("duration", message="Enter the number of days:")
            ]
            duration_answer = inquirer.prompt(duration_question)
            if not duration_answer:
                return
            duration = int(duration_answer["duration"])

        report_controller = ReportController(
            user_id=self.user_id, task_service=self.task_service
        )
        report_controller.generate_report(report_type, duration)

    def create_task(self) -> None:
        """Handle the creation of a new task."""
        clear_console()
        categories = [
            "Billable",
            "Non-billable",
            "Meeting",
            "Personal",
            "Training",
            "Create a new category",
        ]
        category_question = [
            inquirer.List(
                "category",
                message="Choose a category or create one",
                choices=categories,
            )
        ]
        category_answer = inquirer.prompt(category_question)
        if not category_answer:
            return

        category_name = category_answer["category"]
        if category_name == "Create a new category":
            new_category_question = [
                inquirer.Text(
                    "new_category", message="Enter new category name"
                )
            ]
            new_category_answer = inquirer.prompt(new_category_question)
            if not new_category_answer:
                return
            category_name = new_category_answer["new_category"]

        task_questions = [
            inquirer.Text("task_name", message="Enter task/activity name"),
            inquirer.Text(
                "duration", message="Enter duration (in seconds)", default="0"
            ),
        ]
        task_answers = inquirer.prompt(task_questions)
        if not task_answers:
            return

        task_name = task_answers["task_name"]
        try:
            duration = float(task_answers["duration"])
        except ValueError:
            duration = 0.0

        category_obj = self.category_service.create_category(category_name)
        if not category_obj or not hasattr(category_obj, "name"):
            self.console.print(
                f"[red]Failed to create/retrieve category '{category_name}'"
                "[/red]"
            )
            self.console.print(
                "\n[bold magenta]Press Enter to return to the dashboard..."
                "[/bold magenta]"
            )
            input()
            return

        try:
            task = self.task_service.create_task(
                self.user_id, category_obj.name, task_name, duration
            )
            self.console.print(
                f"[green]Task created successfully with ID: {task.id}[/green]"
            )
        except ValueError as err:
            self.console.print(f"[red]{err}[/red]")

        self.console.print(
            "\n[bold magenta]Press Enter to return to the dashboard..."
            "[/bold magenta]"
        )
        input()

    def handle_task_options(self, task_id: int) -> Optional[str]:
        """Handle the options for a selected task.

        Args:
            task_id (int): The ID of the task to handle.

        Returns:
            Optional[str]: The action to take after handling the task options.
        """
        task = self.task_service.get_task_by_id(self.user_id, task_id)
        if not task:
            self.console.print("[red]Task not found.[/red]")
            return None

        time_tracker = TimeTrackerController(
            user_id=self.user_id, task_id=task_id
        )

        if task.task_status == "Not Started":
            options = ["Start Task", "Update Task", "Delete Task", "Back"]
        elif task.task_status == "In Progress":
            options = [
                "Pause Task",
                "Stop Task",
                "Update Task",
                "Delete Task",
                "Back",
            ]
        elif task.task_status == "Paused":
            options = [
                "Resume Task",
                "Stop Task",
                "Update Task",
                "Delete Task",
                "Back",
            ]
        elif task.task_status == "Completed":
            options = ["Edit Timing", "Update Task", "Delete Task", "Back"]
        else:
            options = []

        questions = [
            inquirer.List(
                "action", message="Select an action:", choices=options
            )
        ]
        answers = inquirer.prompt(questions)
        if not answers:
            return None

        action = answers["action"]
        if action == "Start Task":
            # Get the category for the task
            category = (
                task.category_name
            )  # Assuming the task has a `category_name` attribute
            time_tracker.start_timer(category)
            self.task_service.update_task_status(task_id, "In Progress")
            self.show_dashboard()
        elif action == "Pause Task":
            time_tracker.pause_timer()
            self.task_service.update_task_status(task_id, "Paused")
            self.show_dashboard()
        elif action == "Resume Task":
            # Get the category for the task
            category = (
                task.category_name
            )  # Assuming the task has a `category_name` attribute
            time_tracker.resume_timer(category)
            self.task_service.update_task_status(task_id, "In Progress")
            self.show_dashboard()
        elif action == "Stop Task":
            time_tracker.stop_timer()
            self.task_service.update_task_status(task_id, "Completed")
            self.show_dashboard()
        elif action == "Update Task":
            self.update_task(task_id)
            self.show_dashboard()
        elif action == "Delete Task":
            self.delete_task(task_id)
            self.show_dashboard()
        elif action == "Edit Timing":
            self.update_task_timings(task_id)
            self.show_dashboard()
        elif action == "Back":
            self.show_dashboard()
        clear_console()
        return None

    def update_task_timings(self, task_id: int) -> None:
        """Update the start and stop timings of a task."""
        questions = [
            inquirer.Text(
                "start_time",
                message="Enter new start time (YYYY-MM-DD HH:MM:SS):",
            ),
            inquirer.Text(
                "stop_time",
                message="Enter new stop time (YYYY-MM-DD HH:MM:SS):",
            ),
        ]
        answers = inquirer.prompt(questions)
        if not answers:
            return

        try:
            start_time = datetime.strptime(
                answers["start_time"], "%Y-%m-%d %H:%M:%S"
            )
            stop_time = datetime.strptime(
                answers["stop_time"], "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            self.console.print(
                "[red]Invalid date format. "
                "Please use YYYY-MM-DD HH:MM:SS.[/red]"
            )
            self.console.print(
                "\n[bold magenta]Press Enter to return to the dashboard..."
                "[/bold magenta]"
            )
            input()
            return

        time_tracker = TimeTrackerController(
            user_id=self.user_id, task_id=task_id
        )
        time_tracker.update_time_tracker(
            start_time=start_time, stop_time=stop_time
        )

        self.console.print(
            "\n[bold magenta]Press Enter to return to the dashboard..."
            "[/bold magenta]"
        )
        input()

    def update_task(self, task_id: int) -> None:
        """Update an existing task.

        Args:
            task_id (int): The ID of the task to update.
        """
        questions = [
            inquirer.Text("category", message="Enter new category name"),
            inquirer.Text("task_name", message="Enter new task/activity name"),
            inquirer.Text(
                "duration",
                message="Enter new duration (in hours)",
                default="0",
            ),
        ]
        answers = inquirer.prompt(questions)
        clear_console()
        if not answers:
            return

        category_name = answers["category"]
        task_name = answers["task_name"]
        try:
            duration = float(answers["duration"])
        except ValueError:
            duration = 0.0

        try:
            self.task_service.update_task(
                self.user_id, task_id, category_name, task_name, duration
            )
            self.console.print("[green]Task updated successfully.[/green]")
        except ValueError as err:
            self.console.print(f"[red]{err}[/red]")

        self.console.print(
            "\n[bold magenta]Press Enter to return to the dashboard..."
            "[/bold magenta]"
        )
        input()

    def delete_task(self, task_id: int) -> None:
        """Delete an existing task.

        Args:
            task_id (int): The ID of the task to delete.
        """
        self.task_service.delete_task(self.user_id, task_id)
        clear_console()
        self.console.print("[green]Task deleted successfully.[/green]")
        self.console.print(
            "\n[bold magenta]Press Enter to return to the dashboard..."
            "[/bold magenta]"
        )
        input()
