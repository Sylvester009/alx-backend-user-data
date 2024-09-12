#!/usr/bin/env python3
"""Auth module for user registration,
login and password management.
"""
import bcrypt
from uuid import uuid4
from typing import Union
from sqlalchemy.orm.exc import NoResultFound

from db import DB
from user import User


def _hash_password(password: str) -> bytes:
    """takes in a password string arguments
    and returns bytes.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def _generate_uuid() -> str:
    """Generate unique UUID
    """
    return str(uuid4())


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

    def valid_login(self, email: str, password: str) -> bool:
        """Check if email and password are valid.
        """
        user = None
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), user.hashed_password)

    def create_session(self, email: str) -> str:
        """Create a new session.
        """
        user = None
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return None
        session_id = _generate_uuid()
        self._db.update_user(user.id, session_id=session_id)
        return session_id

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        """Find user by session ID
        """
        user = None
        while session_id is not None:
            try:
                user = self._db.find_user_by(session_id=session_id)
                break
            except NoResultFound:
                return None
        return user

    def destroy_session(self, user_id: int) -> None:
        """Destroy session
        """
        while user_id is not None:
            self._db.update_user(user_id, session_id=None)
            break
