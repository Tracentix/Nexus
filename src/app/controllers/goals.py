"""GoalController: fitness goals (FR-12) and body measurements (FR-15)."""
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for)

from ..extensions import db
from ..models import BodyMeasurement, FitnessGoal
from ..models.goals import GOAL_TYPES, MEASUREMENT_KINDS
from .common import (check_csrf, current_user, get_csrf_token, owned_or_403,
                     require_login)

goals_bp = Blueprint("goals", __name__)


def _parse_date(raw):
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _parse_decimal(raw):
    if raw is None or str(raw).strip() == "":
        return None
    try:
        return Decimal(raw)
    except InvalidOperation:
        return Decimal(-1)


# -------------------------------------------------------------------- goals

@goals_bp.route("/goals")
@require_login
def goals():
    user = current_user()
    active = (FitnessGoal.query
              .filter_by(user_id=user.id, status="active")
              .order_by(FitnessGoal.id.desc()).all())
    archived = (FitnessGoal.query
                .filter(FitnessGoal.user_id == user.id,
                        FitnessGoal.status != "active")
                .order_by(FitnessGoal.id.desc()).all())
    return render_template("goals/list.html", active=active,
                           archived=archived, csrf_token=get_csrf_token())


def _goal_from_form(goal):
    goal.goal_type = request.form.get("goal_type", "")
    goal.description = request.form.get("description", "").strip()
    goal.target_value = _parse_decimal(request.form.get("target_value"))
    goal.target_date = _parse_date(request.form.get("target_date"))
    return goal.validate()


@goals_bp.route("/goals/new", methods=["GET", "POST"])
@require_login
def goal_new():
    user = current_user()
    goal = FitnessGoal(user_id=user.id, status="active")
    if request.method == "POST":
        check_csrf()
        errors = _goal_from_form(goal)
        if errors:
            for e in errors:
                flash(e, "error")
        else:
            db.session.add(goal)
            db.session.commit()
            flash("Goal created.", "success")
            return redirect(url_for("goals.goals"))
    return render_template("goals/form.html", goal=goal, types=GOAL_TYPES,
                           action="Create", csrf_token=get_csrf_token())


@goals_bp.route("/goals/<int:goal_id>/edit", methods=["GET", "POST"])
@require_login
def goal_edit(goal_id):
    user = current_user()
    goal = owned_or_403(FitnessGoal.query.filter_by(id=goal_id), user.id)
    if request.method == "POST":
        check_csrf()
        errors = _goal_from_form(goal)
        if errors:
            for e in errors:
                flash(e, "error")
        else:
            db.session.commit()
            flash("Goal updated.", "success")
            return redirect(url_for("goals.goals"))
    return render_template("goals/form.html", goal=goal, types=GOAL_TYPES,
                           action="Save", csrf_token=get_csrf_token())


@goals_bp.route("/goals/<int:goal_id>/status", methods=["POST"])
@require_login
def goal_status(goal_id):
    """Complete or deactivate a goal; completed goals leave the active list."""
    user = current_user()
    goal = owned_or_403(FitnessGoal.query.filter_by(id=goal_id), user.id)
    check_csrf()
    new_status = request.form.get("status", "")
    try:
        goal.set_status(new_status)
    except ValueError:
        flash("Invalid status.", "error")
    else:
        db.session.commit()
        flash("Goal marked as %s." % new_status, "success")
    return redirect(url_for("goals.goals"))


# ------------------------------------------------------------- measurements

@goals_bp.route("/measurements", methods=["GET", "POST"])
@require_login
def measurements():
    user = current_user()
    if request.method == "POST":
        check_csrf()
        kind = request.form.get("kind", "")
        entry = BodyMeasurement(
            user_id=user.id,
            kind=kind,
            value=_parse_decimal(request.form.get("value")),
            unit=MEASUREMENT_KINDS.get(kind, ""),
            measured_on=_parse_date(request.form.get("measured_on")),
        )
        errors = entry.validate()
        if errors:
            for e in errors:
                flash(e, "error")
        else:
            db.session.add(entry)
            db.session.commit()
            flash("Measurement recorded.", "success")
            return redirect(url_for("goals.measurements"))
    entries = (BodyMeasurement.query.filter_by(user_id=user.id)
               .order_by(BodyMeasurement.measured_on.desc()).all())
    return render_template("measurements.html", entries=entries,
                           kinds=MEASUREMENT_KINDS,
                           today=date.today().isoformat(),
                           csrf_token=get_csrf_token())


@goals_bp.route("/measurements/<int:entry_id>/delete", methods=["POST"])
@require_login
def measurement_delete(entry_id):
    user = current_user()
    entry = owned_or_403(BodyMeasurement.query.filter_by(id=entry_id),
                         user.id)
    check_csrf()
    db.session.delete(entry)
    db.session.commit()
    flash("Measurement deleted.", "success")
    return redirect(url_for("goals.measurements"))
