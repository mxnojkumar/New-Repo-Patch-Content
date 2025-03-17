"""
Handle Category Service.

This module handles category management logic for the Time Tracker Console
Application.
It includes functions for creating and retrieving categories.
"""

from typing import List, Optional

from src.data_loader.category_database import CategoryDatabase
from src.models.category import Category


class CategoryService:
    """Service class for managing categories."""

    def __init__(self, db: Optional[CategoryDatabase] = None) -> None:
        """Initialize the category service with a database instance.

        Args:
            db (Optional[CategoryDatabase], optional): The database instance
            to use. Defaults to None.
        """
        self.db = db if db is not None else CategoryDatabase()

    def create_category(self, name: str) -> Category:
        """Create a new category if it doesn't exist.

        Args:
            name (str): The name of the category.

        Returns:
            Category: The created category.
        """
        return self.db.get_or_create_category(name)

    def get_all_categories(self) -> List[Category]:
        """Retrieve all categories.

        Returns:
            List[Category]: A list of all categories.
        """
        return self.db.get_all_categories()
