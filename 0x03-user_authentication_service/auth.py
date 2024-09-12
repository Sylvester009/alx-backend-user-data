#!/usr/bin/env python3
"""Auth module for user registration,
login and password management.
"""
import bcrypt


def _hash_password(password: str) -> bytes:
    """takes in a password string arguments
    and returns bytes.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
