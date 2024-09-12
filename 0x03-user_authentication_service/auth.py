#!/usr/bin/env python3
"""Auth module for user registration,
login and password management.
"""
import bcrypt

from db import DB


def _hash_password(password: str) -> bytes:
    """takes in a password string arguments
    and returns bytes.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Register a new user.
        """
        user_exist = True
        while user_exist:
            try:
                self._db.find_user_by(email=email)
            except NoResultFound:
                user_exist = False
            else:
                raise ValueError("User {} already exists".format(email))
        return self._db.add_user(email, _hash_password(password))
