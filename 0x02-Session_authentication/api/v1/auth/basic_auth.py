#!/usr/bin/env python3
"""
BasicAuth module for API authentication.
"""
import base64
from typing import TypeVar
from models.user import User
from api.v1.auth.auth import Auth


class BasicAuth(Auth):
    """ BasicAuth class that inherits from Auth. """

    def extract_base64_authorization_header(
           self, authorization_header: str) -> str:
        """
        Extracts the Base64 part of the Authorization
        header for Basic Authentication.
        """
        if authorization_header is None:
            return None
        if not isinstance(authorization_header, str):
            return None
        if not authorization_header.startswith("Basic "):
            return None

        return authorization_header[len("Basic "):]

    def decode_base64_authorization_header(
           self, base64_authorization_header: str) -> str:
        """
        Decodes the Base64 part of the Authorization header.
        """
        if base64_authorization_header is None:
            return None
        if not isinstance(base64_authorization_header, str):
            return None

        try:
            base64_byte = base64.b64decode(base64_authorization_header)
            return base64_byte.decode('utf-8')
        except (TypeError, base64.binascii.Error, UnicodeDecodeError):
            return None

    def extract_user_credentials(
           self, decoded_base64_authorization_header: str) -> (str, str):
        """
        Extracts user credentials from the
        decoded Base64 authorization header.
        """
        if decoded_base64_authorization_header is None:
            return None, None
        if not isinstance(decoded_base64_authorization_header, str):
            return None, None
        if ':' not in decoded_base64_authorization_header:
            return None, None

        usr_email, usr_password =\
            decoded_base64_authorization_header.split(':', 1)

        return usr_email, usr_password

    def user_object_from_credentials(
           self, user_email: str, user_pwd: str) -> TypeVar('User'):
        """
        Retrieves a User instance based on email and password.
        """
        result = None
        while type(user_email) == str and type(user_pwd) == str:
            try:
                users = User.search({'email': user_email})
            except Exception:
                break
            while len(users) > 0:
                if users[0].is_valid_password(user_pwd):
                    result = users[0]
                break
            break
        return result

    def current_user(self, request=None) -> TypeVar('User'):
        """
        Gets user from request using methods with while loops.
        """
        auth_header = self.authorization_header(request)
        b64_auth_header = self.extract_base64_authorization_header(auth_header)
        d_auth_head = self.decode_base64_authorization_header(b64_auth_header)
        email, password = self.extract_user_credentials(d_auth_head)
        return self.user_object_from_credentials(email, password)
