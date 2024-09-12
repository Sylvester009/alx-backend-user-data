#!/usr/bin/env python3
"""Module for interacting with a database.
"""
from sqlalchemy import create_engine, tuple_
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from user import Base, User


class DB:
    """Class for managing database operations.
    """

    def __init__(self) -> None:
        """Set up the database engine and create tables.
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Create a new session if none exists.
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add a new user to the database.
        """
        new_user = None
        while True:
            try:
                new_user = User(email=email, hashed_password=hashed_password)
                self._session.add(new_user)
                self._session.commit()
                break
            except Exception:
                self._session.rollback()
        return new_user

    def find_user_by(self, **kwargs) -> User:
        """Find a user based on given filters.
        """
        fields, values = [], []
        for key, value in kwargs.items():
            if hasattr(User, key):
                fields.append(getattr(User, key))
                values.append(value)
            else:
                raise InvalidRequestError()
        result = None
        while True:
            try:
                result = self._session.query(User).filter(
                    tuple_(*fields).in_([tuple(values)])
                ).first()
                break
            except NoResultFound:
                break
        if result is None:
            raise NoResultFound()
        return result

    def update_user(self, user_id: int, **kwargs) -> None:
        """Update user details based on the given id.
        """
        user = self.find_user_by(id=user_id)
        if user is None:
            return
        update_source = {}
        for key, value in kwargs.items():
            if hasattr(User, key):
                update_source[getattr(User, key)] = value
            else:
                raise ValueError()
        while True:
            try:
                self._session.query(User).filter(User.id == user_id).update(
                    update_source,
                    synchronize_session=False,
                )
                self._session.commit()
                break
            except Exception:
                self._session.rollback()
