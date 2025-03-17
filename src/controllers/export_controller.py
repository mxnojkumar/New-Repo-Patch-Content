"""Handle Data Export Controller.

This module handles the user interface for exporting time tracking data.
"""

from typing import Optional

import inquirer  # type: ignore
from rich.console import Console

from src.services.export_service import ExportService
from src.utils.helpers import clear_console


class ExportController:
    """Controller for exporting time tracking data."""

    def __init__(self, user_id: int) -> None:
        """Initialize the export controller with the user ID.

        Args:
            user_id (int): The ID of the user.
        """
        self.user_id = user_id
        self.console = Console()
        self.export_service = ExportService()

    def export_data(self) -> None:
        """Export time tracking data to a CSV file."""
        clear_console()
        questions = [
            inquirer.List(
                "report_type",
                message="Select a report type:",
                choices=[
                    ("Overall", "overall"),
                    ("Daily", "daily"),
                    ("Weekly", "weekly"),
                    ("Monthly", "monthly"),
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

        try:
            filename = self.export_service.export_to_csv(self.user_id, report_type, duration)
            self.console.print(f"[green]Data exported successfully to {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error exporting data: {e}[/red]")

        self.console.print("\n[bold magenta]Press Enter to return to the dashboard...[/bold magenta]")
        input()
