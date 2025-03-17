"""Main module to run the Time Tracker application."""

import inquirer  # type: ignore
from rich.console import Console
from rich.panel import Panel

from src.controllers.authentication_controller import AuthenticationController
from src.controllers.task_controller import TaskController
from src.services.category_service import CategoryService
from src.services.task_service import TaskService
from src.utils.helpers import clear_console

# Create a Rich console instance
console = Console()


def main() -> None:
    """Run main function to handle authentication and task management."""
    auth_controller = AuthenticationController()
    task_service = TaskService()
    category_service = CategoryService()
    logged_in_user = None

    clear_console()
    console.print(
        Panel.fit(
            "[bold magenta]Welcome to Time Tracker App[/bold magenta]",
            title="Time Tracker",
        )
    )

    while True:
        if not logged_in_user:
            questions = [
                inquirer.List(
                    "action",
                    message="What do you want to do?",
                    choices=["Register", "Login", "Exit"],
                )
            ]
            answers = inquirer.prompt(questions)
            if not answers or "action" not in answers:
                console.print("[red]No action selected. Exiting.[/red]")
                break

            action = answers.get("action")
            if action == "Register":
                clear_console()
                console.print(
                    Panel.fit(
                        "[bold magenta]Register to Time Tracker App"
                        "[/bold magenta]",
                        title="User Registration",
                    )
                )
                auth_controller.register_user()
            elif action == "Login":
                clear_console()
                console.print(
                    Panel.fit(
                        "[bold magenta]Login to Time Tracker App"
                        "[/bold magenta]",
                        title="User Login",
                    )
                )
                result = auth_controller.login_user()
                if result is None:
                    console.print("[red]Login failed. Please try again.[/red]")
                    continue
                token, logged_in_user = result
                if logged_in_user is None:
                    console.print("[red]Login failed. Please try again.[/red]")
                    continue
            elif action == "Exit":
                clear_console()
                console.print(
                    "[bold magenta]Exiting the application. "
                    "Goodbye![/bold magenta]"
                )
                break
        else:
            if logged_in_user.id:
                clear_console()
                console.print(
                    Panel.fit(
                        f"[green]Logged in as {logged_in_user.email}[/green]",
                        title="User Dashboard",
                    )
                )
                task_controller = TaskController(
                    logged_in_user.id, task_service, category_service
                )
                task_controller.show_dashboard()  # Show the dashboard once
                result = task_controller.show_task_menu()  # Show the task menu
                if result == "logout":  # Handle log out
                    logged_in_user = None  # Reset the logged-in user
                    console.print(
                        "[bold magenta]Logged out successfully.[/bold magenta]"
                    )


if __name__ == "__main__":
    main()
