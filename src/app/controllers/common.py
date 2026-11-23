"""Shared controller helpers: session auth, CSRF, ownership checks."""
import secrets
from functools import wraps

from flask import abort, request, session

from ..models import User


def current_user():
    """Return the signed-in User row, or None."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = User.query.get(user_id)
    if user is None or user.status != "active":
        session.clear()
        return None
    return user


def require_login(view):
    """Block protected pages when there is no valid session (FR-02)."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if current_user() is None:
            return _login_redirect()
        return view(*args, **kwargs)
    return wrapper


def _login_redirect():
    from flask import redirect, url_for
    return redirect(url_for("auth.login", next=request.path))


def get_csrf_token():
    """One token per session, embedded in every form."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def check_csrf():
    """Reject POSTs without the session's CSRF token."""
    token = request.form.get("csrf_token", "")
    if not token or token != session.get("csrf_token"):
        abort(400, "Invalid form token. Go back and try again.")


def owned_or_403(query, user_id):
    """Load a row and make sure it belongs to the signed-in member.

    Ownership is enforced on the server, not by hiding buttons in the UI.
    """
    row = query.first_or_404()
    if row.user_id != user_id:
        abort(403)
    return row
