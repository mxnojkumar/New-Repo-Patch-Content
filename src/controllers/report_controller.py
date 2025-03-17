"""
Handles report generation.

This module contains the ReportController class, which is responsible for
generating reports based on the user's time entries.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel

from src.models.time_tracker import TimeTracker
from src.services.report_service import ReportService
from src.services.task_service import TaskService
from src.utils.helpers import clear_console


class ReportController:
    """Controller for generating time tracking reports."""

    def __init__(
        self, user_id: int, task_service: Optional[TaskService] = None
    ) -> None:
        """Initialize ReportController with user id, and task service.

        Args:
            user_id (int): The ID of the user.
            task_service (Optional[TaskService], optional): TaskService
            instance. Defaults to None.
        """
        self.user_id = user_id
        self.task_service = (
            task_service if task_service is not None else TaskService()
        )
        self.report_service = ReportService(task_service=self.task_service)
        self.console = Console()

    def generate_report(
        self, report_type: str, duration: Optional[int] = None
    ) -> None:
        """Generate a report based on the specified type and duration."""
        clear_console()
        if report_type == "overall":
            self._generate_overall_report()
        elif report_type == "daily":
            self._generate_daily_report()
        elif report_type == "weekly":
            self._generate_weekly_report()
        elif report_type == "monthly":
            self._generate_monthly_report()
        elif report_type == "category":
            self._generate_category_report()
        elif report_type == "custom":
            if duration:
                self._generate_custom_report(duration)
            else:
                self.console.print("[red]Invalid duration specified.[/red]")
        else:
            self.console.print("[red]Invalid report type.[/red]")

        # Wait for user input before returning to the dashboard
        self.console.print(
            "\n[bold magenta]Press Enter to return to the dashboard..."
            "[/bold magenta]"
        )
        input()

    def _generate_overall_report(self) -> None:
        """Generate an overall report."""
        time_trackers = self.report_service.get_time_trackers_by_user(
            self.user_id
        )
        self._display_insights(time_trackers)

    def _generate_daily_report(self) -> None:
        """Generate a daily report."""
        today = datetime.now().date()
        time_trackers = self.report_service.get_time_trackers_by_user_and_date(
            self.user_id, today
        )
        self._display_insights(time_trackers)

    def _generate_weekly_report(self) -> None:
        """Generate a weekly report."""
        start_date = datetime.now().date() - timedelta(days=7)
        time_trackers = (
            self.report_service.get_time_trackers_by_user_and_date_range(
                self.user_id, start_date, datetime.now().date()
            )
        )
        self._display_insights(time_trackers)

    def _generate_monthly_report(self) -> None:
        """Generate a monthly report."""
        start_date = datetime.now().date() - timedelta(days=30)
        time_trackers = (
            self.report_service.get_time_trackers_by_user_and_date_range(
                self.user_id, start_date, datetime.now().date()
            )
        )
        self._display_insights(time_trackers)

    def _generate_category_report(self) -> None:
        """Generate a category-wise report."""
        time_trackers = self.report_service.get_time_trackers_by_user(
            self.user_id
        )
        categories = self.report_service.get_category_insights(time_trackers)
        self.console.print(
            Panel.fit("[bold magenta]Category-wise Report[/bold magenta]")
        )
        for category, total_time in categories.items():
            self.console.print(
                f"[cyan]{category}: {total_time} seconds[/cyan]"
            )

    def _generate_custom_report(self, duration: int) -> None:
        """Generate a custom duration report."""
        if duration <= 0 or not str(duration).isdigit():
            self.console.print("[red]Invalid duration specified.[/red]")
        else:
            start_date = datetime.now().date() - timedelta(days=duration)
            time_trackers = (
                self.report_service.get_time_trackers_by_user_and_date_range(
                    self.user_id, start_date, datetime.now().date()
                )
            )
            self._display_insights(time_trackers)

    def _display_insights(self, time_trackers: List[TimeTracker]) -> None:
        """Display insights based on time trackers."""
        if not time_trackers:
            self.console.print(
                "[yellow]No data available for the selected report.[/yellow]"
            )
            return

        total_time = self.report_service.get_total_time(time_trackers)
        categories = self.report_service.get_category_insights(time_trackers)
        task_insights = self.report_service.get_task_insights(
            time_trackers, self.user_id
        )

        self.console.print(Panel.fit("[bold magenta]Insights[/bold magenta]"))
        self.console.print(
            f"[green]Total time spent: {total_time} seconds[/green]"
        )

        # Display category insights
        if categories:
            most_time_category = max(
                categories.keys(), key=lambda k: categories[k]
            )
            least_time_category = min(
                categories.keys(), key=lambda k: categories[k]
            )
            self.console.print(
                f"[cyan]Most time spent on: {most_time_category} "
                f"({categories[most_time_category]:.2f} seconds)[/cyan]"
            )
            self.console.print(
                f"[cyan]Least time spent on: {least_time_category} "
                f"({categories[least_time_category]:.2f} seconds)[/cyan]"
            )
            self.console.print(
                f"[cyan]Frequent categories: {', '.join(categories.keys())}"
                "[/cyan]"
            )
        else:
            self.console.print("[yellow]No category data available.[/yellow]")

        # Display task-specific insights
        self.console.print(
            Panel.fit("[bold magenta]Task-specific Insights[/bold magenta]")
        )
        for insight in task_insights:
            self.console.print(
                f"[cyan]Task {insight['task_id']}: {insight['task_name']} "
                f"({insight['category']})[/cyan]"
            )
            self.console.print(f"  - Start Time: {insight['start_time']}")
            self.console.print(f"  - Stop Time: {insight['stop_time']}")
            self.console.print(
                f"  - Total Time: {insight['total_time']:.2f} seconds"
            )
            self.console.print(
                f"  - Estimated Duration: {insight['estimated_duration']:.2f} "
                "seconds"
            )
            self.console.print(f"  - Status: {insight['status']}")
            duration_insight = self.report_service.get_task_duration_insights(
                insight["task_id"], self.user_id
            )
            self.console.print(f"  - Duration Insight: {duration_insight}")
