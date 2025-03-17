"""
Authentication Exceptions.

This module has custom exceptions for authentication service.
"""


class UserAlreadyExistsError(Exception):
    """Exception raised when a user with the provided email already exists."""

    pass


class AuthenticationError(Exception):
    """Exception raised when authentication fails."""

    pass
