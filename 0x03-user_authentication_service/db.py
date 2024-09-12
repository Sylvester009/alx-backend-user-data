#!/usr/bin/env python3
"""DB module
"""
from sqlalchemy import create_engine, tuple_
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from user import Base, User


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=True)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add new user to the database."""
        try:
            new_user = User(email=email, hashed_password=hashed_password)
            self._session.add(new_user)
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        return new_user

    def find_user_by(self, **kwargs) -> User:
        """Based on given filters, find user."""
        for key in kwargs:
            if not hasattr(User, key):
                raise InvalidRequestError(f"'{key}' is not a valid attribute of User")
        try:
            result = self._session.query(User).filter_by(**kwargs).first()
        except NoResultFound:
            raise NoResultFound(f"No user found for given filters: {kwargs}")
        return result

    def update_user(self, user_id: int, **kwargs) -> None:
        """Update user details via id."""
        user = self.find_user_by(id=user_id)
        update_info = {}
        for key, value in kwargs.items():
            if not hasattr(User, key):
                raise ValueError(f"'{key}' is not a valid attribute of User")
            setattr(user, key, value)
        self._session.commit()
