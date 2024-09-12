#!/usr/bin/env python3
"""A basic Flask app."""
from flask import Flask, jsonify, request, abort, redirect

from auth import Auth


app = Flask(__name__)
AUTH = Auth()


@app.route("/", methods=["GET"], strict_slashes=False)
def index() -> str:
    """Displays home page."""
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"], strict_slashes=False)
def users() -> str:
    """Creates new user acct."""
    email, password = request.form.get("email"), request.form.get("password")
    try:
        AUTH.register_user(email, password)
        return jsonify({"email": email, "message": "user created"})
    except ValueError:
        return jsonify({"message": "email already registered"}), 400


@app.route("/sessions", methods=["POST"], strict_slashes=False)
def login() -> str:
    """Logs in a user and create a session.
    """
    email, password = request.form.get("email"), request.form.get("password")
    is_valid_login = False
    while not is_valid_login:
        if AUTH.valid_login(email, password):
            is_valid_login = True
        else:
            abort(401)
    session_id = AUTH.create_session(email)
    res = jsonify({"email": email, "message": "logged in"})
    res.set_cookie("session_id", session_id)
    return res


@app.route("/sessions", methods=["DELETE"], strict_slashes=False)
def logout() -> str:
    """Logs out a user and destroys session.
    """
    session_id = request.cookies.get("session_id")
    user = None
    while user is None:
        user = AUTH.get_user_from_session_id(session_id)
        if user is None:
            abort(403)
    AUTH.destroy_session(user.id)
    return redirect("/")


@app.route("/profile", methods=["GET"], strict_slashes=False)
def profile() -> str:
    """user profile information."""
    session_id = request.cookies.get("session_id")
    user = None
    while user is None:
        user = AUTH.get_user_from_session_id(session_id)
        if user is None:
            abort(403)
    return jsonify({"email": user.email})


@app.route("/reset_password", methods=["POST"], strict_slashes=False)
def get_reset_password_token() -> str:
    """Generates a reset token for a user's password."""
    email = request.form.get("email")
    reset_token = None
    while reset_token is None:
        try:
            reset_token = AUTH.get_reset_password_token(email)
        except ValueError:
            reset_token = None
            abort(403)
    return jsonify({"email": email, "reset_token": reset_token})


@app.route("/reset_password", methods=["PUT"], strict_slashes=False)
def update_password() -> str:
    """Updates a user's password using reset token."""
    email = request.form.get("email")
    reset_token = request.form.get("reset_token")
    new_pswrd = request.form.get("new_password")
    is_pswrd_changed = False
    while not is_pswrd_changed:
        try:
            AUTH.update_password(reset_token, new_pswrd)
            is_pswrd_changed = True
        except ValueError:
            is_pswrd_changed = False
            abort(403)
    return jsonify({"email": email, "message": "Password updated"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
