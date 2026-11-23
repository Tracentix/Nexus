"""ProfileController: profile editing (FR-04) and calorie target (FR-11)."""
from decimal import Decimal, InvalidOperation

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)

from ..extensions import db
from .common import (check_csrf, current_user, get_csrf_token,
                     require_login)

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/", methods=["GET", "POST"])
@require_login
def show():
    user = current_user()
    profile = user.profile
    if request.method == "POST":
        check_csrf()
        name = request.form.get("display_name", "").strip()
        preferences = request.form.get("preferences", "").strip()
        target_raw = request.form.get("daily_calorie_target", "").strip()

        errors = []
        if not name or len(name) > 100:
            errors.append("Enter a display name (max 100 characters).")
        if len(preferences) > 2000:
            errors.append("Preferences text is too long.")

        target = None
        if target_raw:
            try:
                target = Decimal(target_raw)
            except InvalidOperation:
                errors.append("Calorie target must be a number.")
            else:
                low = current_app.config["MIN_CALORIE_TARGET"]
                high = current_app.config["MAX_CALORIE_TARGET"]
                if target < low or target > high:
                    errors.append(
                        "Calorie target must be between %d and %d."
                        % (low, high))

        if errors:
            for e in errors:
                flash(e, "error")
        else:
            # Members can only change their own permitted fields here;
            # role and status are never taken from the form.
            profile.display_name = name
            profile.preferences = preferences or None
            profile.daily_calorie_target = target
            db.session.commit()
            flash("Profile updated.", "success")
            return redirect(url_for("profile.show"))

    return render_template("profile.html", user=user, profile=profile,
                           csrf_token=get_csrf_token())
