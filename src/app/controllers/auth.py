"""AuthController: registration, sign in/out, password change and reset.

Covers FR-01, FR-02 and FR-03 from the Phase 2 SRS.
"""
import re

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, session, url_for)

from ..extensions import db
from ..models import PasswordResetToken, Profile, User
from .common import check_csrf, current_user, get_csrf_token, require_login

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LEN = 8


def _valid_registration(name, email, password, confirm):
    errors = []
    if not name or len(name) > 100:
        errors.append("Enter a display name (max 100 characters).")
    if not email or not EMAIL_RE.match(email):
        errors.append("Enter a valid email address.")
    elif User.query.filter(db.func.lower(User.email) == email.lower()).first():
        errors.append("This email is already registered.")
    if not password or len(password) < MIN_PASSWORD_LEN:
        errors.append("Password must be at least %d characters."
                      % MIN_PASSWORD_LEN)
    if password != confirm:
        errors.append("Passwords do not match.")
    return errors


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        check_csrf()
        name = request.form.get("display_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        errors = _valid_registration(name, email, password, confirm)
        if errors:
            for e in errors:
                flash(e, "error")
        else:
            user = User(email=email.lower(), role="member", status="active")
            user.set_password(password)
            user.profile = Profile(display_name=name)
            db.session.add(user)
            db.session.commit()
            flash("Account created. You can sign in now.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", csrf_token=get_csrf_token())


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        check_csrf()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter(db.func.lower(User.email) == email).first()
        if user and user.status == "active" and user.verify_password(password):
            session.clear()
            session["user_id"] = user.id
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("dashboard.summary"))
        flash("Invalid email or password.", "error")
    return render_template("auth/login.html", csrf_token=get_csrf_token())


@auth_bp.route("/logout", methods=["POST"])
def logout():
    check_csrf()
    session.clear()
    flash("Signed out.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/password/change", methods=["GET", "POST"])
@require_login
def change_password():
    user = current_user()
    if request.method == "POST":
        check_csrf()
        current = request.form.get("current_password", "")
        new = request.form.get("new_password", "")
        confirm = request.form.get("confirm", "")
        if not user.verify_password(current):
            flash("Current password is wrong.", "error")
        elif len(new) < MIN_PASSWORD_LEN:
            flash("New password must be at least %d characters."
                  % MIN_PASSWORD_LEN, "error")
        elif new != confirm:
            flash("New passwords do not match.", "error")
        else:
            user.set_password(new)
            db.session.commit()
            flash("Password changed.", "success")
            return redirect(url_for("profile.show"))
    return render_template("auth/change_password.html",
                           csrf_token=get_csrf_token())


@auth_bp.route("/password/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        check_csrf()
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter(db.func.lower(User.email) == email).first()
        if user:
            token, raw = PasswordResetToken.create_for(user)
            db.session.commit()
            link = url_for("auth.reset_password", token_id=token.id,
                           raw=raw, _external=True)
            # MAIL_DELIVERY=console: no SMTP configured, so the link is
            # printed to the server console. The flow stays the same once
            # real email delivery is added.
            current_app.logger.info("Password reset link for user %s: %s",
                                    user.id, link)
            print("Password reset link:", link, flush=True)
        # Same message either way so the form never reveals whether an
        # email address is registered (FR-03).
        flash("If that email is registered, a reset link has been sent.",
              "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/forgot.html", csrf_token=get_csrf_token())


@auth_bp.route("/password/reset/<int:token_id>", methods=["GET", "POST"])
def reset_password(token_id):
    token = PasswordResetToken.query.get_or_404(token_id)
    raw = request.values.get("raw", "")
    if not token.is_valid() or not token.matches(raw):
        flash("This reset link is invalid or has expired.", "error")
        return redirect(url_for("auth.forgot_password"))
    if request.method == "POST":
        check_csrf()
        new = request.form.get("new_password", "")
        confirm = request.form.get("confirm", "")
        if len(new) < MIN_PASSWORD_LEN:
            flash("New password must be at least %d characters."
                  % MIN_PASSWORD_LEN, "error")
        elif new != confirm:
            flash("New passwords do not match.", "error")
        else:
            user = User.query.get(token.user_id)
            user.set_password(new)
            token.mark_used()  # single-use
            db.session.commit()
            flash("Password reset. Sign in with your new password.",
                  "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/reset.html", csrf_token=get_csrf_token(),
                           token_id=token.id, raw=raw)
