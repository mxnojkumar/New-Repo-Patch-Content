"""
config.py module.

This module generates a secret key for JWT token
"""

import secrets

SECRET_KEY = secrets.token_urlsafe(32)
