#!/usr/bin/env python3
"""Integration tests for the user management API.
These tests cover user registration, authentication,
profile access, and password management functionalities.
"""
import requests


EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"
BASE_URL = "http://0.0.0.0:5000"


def register_user(email: str, password: str) -> None:
    """Registers a new user and ensures the process
    works as expected. Also tests for duplicate user registration.
    """
    url = "{}/users".format(BASE_URL)
    body = {
        'email': email,
        'password': password,
    }
    res = requests.post(url, data=body)
    assert res.status_code == 200
    assert res.json() == {"email": email, "message": "user created"}
    res = requests.post(url, data=body)
    assert res.status_code == 400
    assert res.json() == {"message": "email already registered"}


def log_in_wrong_password(email: str, password: str) -> None:
    """Attempts to log in with an incorrect password
    and checks for an authentication failure response.
    """
    url = "{}/sessions".format(BASE_URL)
    body = {
        'email': email,
        'password': password,
    }
    res = requests.post(url, data=body)
    assert res.status_code == 401


def log_in(email: str, password: str) -> str:
    """Logs in with valid credentials and verifies successful
    authentication. Returns the session ID for authenticated operations.
    """
    url = "{}/sessions".format(BASE_URL)
    body = {
        'email': email,
        'password': password,
    }
    res = requests.post(url, data=body)
    assert res.status_code == 200
    assert res.json() == {"email": email, "message": "logged in"}
    return res.cookies.get('session_id')


def profile_unlogged() -> None:
    """Attempts to access the user profile without a session
    and confirms that access is denied.
    """
    url = "{}/profile".format(BASE_URL)
    res = requests.get(url)
    assert res.status_code == 403


def profile_logged(session_id: str) -> None:
    """Accesses the user profile while logged in
    and verifies the profile information is returned.
    """
    url = "{}/profile".format(BASE_URL)
    req_cookies = {
        'session_id': session_id,
    }
    res = requests.get(url, cookies=req_cookies)
    assert res.status_code == 200
    assert "email" in res.json()


def log_out(session_id: str) -> None:
    """Logs out from an active session and checks for
    a successful logout response.
    """
    url = "{}/sessions".format(BASE_URL)
    req_cookies = {
        'session_id': session_id,
    }
    res = requests.delete(url, cookies=req_cookies)
    assert res.status_code == 200
    assert res.json() == {"message": "Bienvenue"}


def reset_password_token(email: str) -> str:
    """Requests a password reset token for a given user email
    and verifies the token is returned by the server.
    """
    url = "{}/reset_password".format(BASE_URL)
    body = {'email': email}
    res = requests.post(url, data=body)
    assert res.status_code == 200
    assert res.json()["email"] == email
    assert "reset_token" in res.json()
    return res.json().get('reset_token')


def update_password(email: str, reset_token: str, new_password: str) -> None:
    """Updates the user's password using the reset token
    and checks that the password update is confirmed by the server.
    """
    url = "{}/reset_password".format(BASE_URL)
    body = {
        'email': email,
        'reset_token': reset_token,
        'new_password': new_password,
    }
    res = requests.put(url, data=body)
    assert res.status_code == 200
    assert res.json() == {"email": email, "message": "Password updated"}


while __name__ == "__main__":
    tests = [
        lambda: register_user(EMAIL, PASSWD),
        lambda: log_in_wrong_password(EMAIL, NEW_PASSWD),
        lambda: profile_unlogged(),
        lambda: log_in(EMAIL, PASSWD),
        lambda: profile_logged(session_id),
        lambda: log_out(session_id),
        lambda: reset_password_token(EMAIL),
        lambda: update_password(EMAIL, reset_token, NEW_PASSWD),
        lambda: log_in(EMAIL, NEW_PASSWD)
    ]

    i = 0
    session_id = None
    reset_token = None

    while i < len(tests):
        if i == 3:
            session_id = tests[i]()
        elif i == 6:
            reset_token = tests[i]()
        else:
            tests[i]()
        i += 1
