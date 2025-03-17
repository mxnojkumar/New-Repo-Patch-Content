"""
category_database.py module.

This module handles database operations for the Category model that includes
methods for creating, retrieving, and updating categories.
"""

import sqlite3
from sqlite3 import Connection, Error
from typing import List, Optional

from src.models.category import Category


class CategoryDatabase:
    """Database class for managing categories."""

    def __init__(self, db_path: str = "src/database/categories.db") -> None:
        """Initialize the database with the path to the database file.

        Args:
            db_path (str, optional): The path to the database file.
            Defaults to "src/database/categories.db".
        """
        self.db_path = db_path
        self.conn: Optional[Connection] = None
        self.connect()
        self.create_categories_table()

    def connect(self) -> None:
        """Establish a connection to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        except Error as e:
            raise Exception(f"Error connecting to database: {e}")

    def create_categories_table(self) -> None:
        """Create the categories table if it doesn't exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS categories (
            name TEXT NOT NULL PRIMARY KEY
        );
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(create_table_sql)
                self.conn.commit()
        except Error as e:
            raise Exception(f"Error creating categories table: {e}")

    def get_or_create_category(self, name: str) -> Category:
        """Retrieve a category by name, or creates it if it doesn't exist.

        Args:
            name (str): The name of the category.

        Raises:
            Exception: When an error occurs while retrieving or creating
            the category.
            ValueError: When the category cannot be created or retrieved.

        Returns:
            Category: The category object.
        """
        select_sql = "SELECT * FROM categories WHERE name = ?"
        insert_sql = "INSERT INTO categories (name) VALUES (?)"
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(select_sql, (name,))
                row = cursor.fetchone()
                if row:
                    return Category(
                        name=row["name"]
                    )  # Return existing category
                cursor.execute(insert_sql, (name,))
                self.conn.commit()
                return Category(name=name)  # Return newly created category
        except Error as e:
            raise Exception(f"Error retrieving or creating category: {e}")
        raise ValueError(f"Failed to create or retrieve category '{name}'.")

    def get_all_categories(self) -> List[Category]:
        """Retrieve all categories.

        Raises:
            Exception: When an error occurs while retrieving categories.

        Returns:
            List[Category]: A list of category objects.
        """
        select_sql = "SELECT * FROM categories"
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(select_sql)
                rows = cursor.fetchall()
                return [Category(name=row["name"]) for row in rows]
        except Error as e:
            raise Exception(f"Error retrieving categories: {e}")
        return []
