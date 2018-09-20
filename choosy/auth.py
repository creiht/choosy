"""HTTP Handlers for /auth/* calls"""
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash

from choosy import db

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=("GET", "POST"))
def register():
    # TODO: Add password strength check
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password2 = request.form["password2"]
        error = None

        if not username:
            error = "Username required."
        elif not password:
            error = "Password required."
        elif not password2:
            error = "Password confirmation required."
        elif password != password2:
            error = "Passwords do not match."
        elif db.get_user_by_name(username) is not None:
            error = "User {} is already registered.".format(username)

        if error is None:
            user_id = db.create_user(username, password)
            # Go ahead and log the new user in by setting the session info
            session.clear()
            session["user_id"] = user_id
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None

        user = db.get_user_by_name(username)

        if user is None or not check_password_hash(user["password"], password):
            error = "Incorrect password or username."

        if error is None:
            # User checks out, so create a new session
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        # If we get here then show the error
        flash(error)

    return render_template("auth/login.html")

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

@bp.before_app_request
def load_logged_in_user():
    # TODO: Don't load this from the DB on every request
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        user = db.get_user_by_id(user_id)
        if user is None:
            # Something got reset since the last time this user was here
            g.user = None
        else:
            g.user = {
                "id": user["id"],
                "username": user["username"],
            }

def login_required(view):
    """Decorator to use with other views when login is required."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view
