"""
Defines Category model.

This module represents a category model with id and category_name attributes.
"""

from pydantic import BaseModel


class Category(BaseModel):
    """Represent a category model using Pydantic for validation."""

    name: str
