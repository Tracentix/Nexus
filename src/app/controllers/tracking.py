"""TrackingController: workouts (FR-05..07) and meals (FR-08..10)."""
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for)

from ..extensions import db
from ..models import FoodItem, MealEntry, WorkoutEntry
from ..models.tracking import MEAL_LABELS, WORKOUT_TYPES
from .common import (check_csrf, current_user, get_csrf_token, owned_or_403,
                     require_login)

tracking_bp = Blueprint("tracking", __name__)


def _parse_date(raw):
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _parse_decimal(raw):
    try:
        return Decimal(raw)
    except (TypeError, InvalidOperation):
        return None


# ---------------------------------------------------------------- workouts

def _workout_query(user_id):
    return WorkoutEntry.query.filter_by(user_id=user_id)


@tracking_bp.route("/workouts")
@require_login
def workouts():
    """Workout history with optional date-range and type filters (FR-07)."""
    user = current_user()
    query = _workout_query(user.id)

    date_from = _parse_date(request.args.get("from"))
    date_to = _parse_date(request.args.get("to"))
    type_filter = request.args.get("type", "").strip()

    if date_from:
        query = query.filter(WorkoutEntry.started_at >=
                             datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(WorkoutEntry.started_at <=
                             datetime.combine(date_to, datetime.max.time()))
    if type_filter in WORKOUT_TYPES:
        query = query.filter(WorkoutEntry.activity_type == type_filter)

    entries = query.order_by(WorkoutEntry.started_at.desc()).all()
    return render_template(
        "workouts/list.html", entries=entries, types=WORKOUT_TYPES,
        date_from=request.args.get("from", ""), date_to=request.args.get("to", ""),
        type_filter=type_filter, csrf_token=get_csrf_token())


def _workout_from_form(entry):
    entry.activity_type = request.form.get("activity_type", "")
    entry.duration_minutes = int(_parse_decimal(
        request.form.get("duration_minutes")) or -1)
    day = _parse_date(request.form.get("started_on"))
    entry.started_at = (datetime.combine(day, datetime.min.time())
                        if day else None)
    kcal = _parse_decimal(request.form.get("estimated_kcal", "").strip() or "0")
    entry.estimated_kcal = kcal if kcal and kcal > 0 else None
    entry.notes = request.form.get("notes", "").strip() or None
    return entry.validate()


@tracking_bp.route("/workouts/new", methods=["GET", "POST"])
@require_login
def workout_new():
    user = current_user()
    entry = WorkoutEntry(user_id=user.id)
    if request.method == "POST":
        check_csrf()
        errors = _workout_from_form(entry)
        if errors:
            for e in errors:
                flash(e, "error")
        else:
            db.session.add(entry)
            db.session.commit()
            flash("Workout recorded.", "success")
            return redirect(url_for("tracking.workouts"))
    return render_template("workouts/form.html", entry=entry,
                           types=WORKOUT_TYPES, action="Record",
                           today=date.today().isoformat(),
                           csrf_token=get_csrf_token())


@tracking_bp.route("/workouts/<int:entry_id>/edit", methods=["GET", "POST"])
@require_login
def workout_edit(entry_id):
    user = current_user()
    entry = owned_or_403(_workout_query(user.id).filter_by(id=entry_id),
                         user.id)
    if request.method == "POST":
        check_csrf()
        errors = _workout_from_form(entry)
        if errors:
            for e in errors:
                flash(e, "error")
        else:
            db.session.commit()
            flash("Workout updated.", "success")
            return redirect(url_for("tracking.workouts"))
    return render_template("workouts/form.html", entry=entry,
                           types=WORKOUT_TYPES, action="Save",
                           today=date.today().isoformat(),
                           csrf_token=get_csrf_token())


@tracking_bp.route("/workouts/<int:entry_id>/delete", methods=["GET", "POST"])
@require_login
def workout_delete(entry_id):
    """Two-step delete: a confirmation page, then the POST (FR-06)."""
    user = current_user()
    entry = owned_or_403(_workout_query(user.id).filter_by(id=entry_id),
                         user.id)
    if request.method == "POST":
        check_csrf()
        db.session.delete(entry)
        db.session.commit()
        flash("Workout deleted.", "success")
        return redirect(url_for("tracking.workouts"))
    return render_template("confirm_delete.html", what="workout",
                           detail="%s on %s" % (
                               entry.activity_type,
                               entry.started_at.strftime("%Y-%m-%d")),
                           csrf_token=get_csrf_token())


# -------------------------------------------------------------------- meals

@tracking_bp.route("/meals")
@require_login
def meals():
    user = current_user()
    day = _parse_date(request.args.get("date")) or date.today()
    entries = (MealEntry.query
               .filter_by(user_id=user.id, eaten_on=day)
               .order_by(MealEntry.id).all())
    total = round(sum(float(e.calorie_snapshot) for e in entries), 2)
    return render_template("meals/list.html", entries=entries, day=day,
                           total=total, csrf_token=get_csrf_token())


@tracking_bp.route("/foods/search")
@require_login
def food_search():
    """Partial-name catalogue search over active items (FR-08)."""
    term = request.args.get("q", "")
    results = FoodItem.search(term) if term.strip() else []
    return render_template("meals/food_results.html", results=results,
                           term=term)


def _meal_from_form(entry):
    food = FoodItem.query.get(request.form.get("food_id", type=int) or 0)
    entry.food = food
    entry.meal_label = request.form.get("meal_label", "")
    entry.quantity = _parse_decimal(request.form.get("quantity"))
    entry.eaten_on = _parse_date(request.form.get("eaten_on"))
    errors = entry.validate()
    if not errors:
        entry.recalculate_calories()
    return errors


@tracking_bp.route("/meals/new", methods=["GET", "POST"])
@require_login
def meal_new():
    user = current_user()
    entry = MealEntry(user_id=user.id)
    if request.method == "POST":
        check_csrf()
        errors = _meal_from_form(entry)
        if errors:
            for e in errors:
                flash(e, "error")
        else:
            db.session.add(entry)
            db.session.commit()
            flash("Meal recorded (%s kcal)." % entry.calorie_snapshot,
                  "success")
            return redirect(url_for("tracking.meals",
                                    date=entry.eaten_on.isoformat()))
    return render_template("meals/form.html", entry=entry, labels=MEAL_LABELS,
                           foods=FoodItem.search(""), action="Record",
                           today=date.today().isoformat(),
                           csrf_token=get_csrf_token())


@tracking_bp.route("/meals/<int:entry_id>/edit", methods=["GET", "POST"])
@require_login
def meal_edit(entry_id):
    user = current_user()
    entry = owned_or_403(MealEntry.query.filter_by(id=entry_id), user.id)
    if request.method == "POST":
        check_csrf()
        errors = _meal_from_form(entry)
        if errors:
            for e in errors:
                flash(e, "error")
        else:
            db.session.commit()
            flash("Meal updated.", "success")
            return redirect(url_for("tracking.meals",
                                    date=entry.eaten_on.isoformat()))
    return render_template("meals/form.html", entry=entry, labels=MEAL_LABELS,
                           foods=FoodItem.search(""), action="Save",
                           today=date.today().isoformat(),
                           csrf_token=get_csrf_token())


@tracking_bp.route("/meals/<int:entry_id>/delete", methods=["GET", "POST"])
@require_login
def meal_delete(entry_id):
    user = current_user()
    entry = owned_or_403(MealEntry.query.filter_by(id=entry_id), user.id)
    if request.method == "POST":
        check_csrf()
        day = entry.eaten_on.isoformat()
        db.session.delete(entry)
        db.session.commit()
        flash("Meal deleted.", "success")
        return redirect(url_for("tracking.meals", date=day))
    return render_template("confirm_delete.html", what="meal",
                           detail="%s on %s" % (
                               entry.food.name, entry.eaten_on),
                           csrf_token=get_csrf_token())
