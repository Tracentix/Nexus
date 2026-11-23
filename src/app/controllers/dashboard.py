"""DashboardController: daily summary (FR-13) and progress charts (FR-14)."""
from datetime import date, datetime, timedelta

from flask import Blueprint, render_template, request

from ..models import (BodyMeasurement, FitnessGoal, MealEntry, WorkoutEntry)
from ..models.tracking import MEAL_LABELS, day_bounds
from ..utils.svgcharts import bar_chart
from .common import current_user, get_csrf_token, require_login

dashboard_bp = Blueprint("dashboard", __name__)


def _parse_date(raw):
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


@dashboard_bp.route("/dashboard")
@require_login
def summary():
    """Date-specific dashboard; totals come from stored entries (FR-13)."""
    user = current_user()
    day = _parse_date(request.args.get("date")) or date.today()
    start, end = day_bounds(day)

    workouts = (WorkoutEntry.query
                .filter(WorkoutEntry.user_id == user.id,
                        WorkoutEntry.started_at >= start,
                        WorkoutEntry.started_at <= end)
                .order_by(WorkoutEntry.started_at).all())
    meals = (MealEntry.query
             .filter_by(user_id=user.id, eaten_on=day)
             .order_by(MealEntry.id).all())

    workout_minutes = sum(w.duration_minutes for w in workouts)
    workout_kcal = round(sum(float(w.estimated_kcal) for w in workouts
                             if w.estimated_kcal), 2)
    meal_kcal = round(sum(float(m.calorie_snapshot) for m in meals), 2)
    meals_by_label = {label: [m for m in meals if m.meal_label == label]
                      for label in MEAL_LABELS}

    target = (float(user.profile.daily_calorie_target)
              if user.profile and user.profile.daily_calorie_target is not None
              else None)
    remaining = round(target - meal_kcal, 2) if target is not None else None

    active_goals = (FitnessGoal.query
                    .filter_by(user_id=user.id, status="active")
                    .order_by(FitnessGoal.id.desc()).all())
    latest_weight = (BodyMeasurement.query
                     .filter_by(user_id=user.id, kind="weight")
                     .order_by(BodyMeasurement.measured_on.desc()).first())

    return render_template(
        "dashboard.html", day=day, workouts=workouts,
        workout_minutes=workout_minutes, workout_kcal=workout_kcal,
        meals_by_label=meals_by_label, meal_kcal=meal_kcal, target=target,
        remaining=remaining, active_goals=active_goals,
        latest_weight=latest_weight, csrf_token=get_csrf_token())


@dashboard_bp.route("/charts")
@require_login
def charts():
    """Progress charts over a selectable period, from stored records (FR-14)."""
    user = current_user()
    days = request.args.get("days", default=7, type=int)
    if days not in (7, 14, 30):
        days = 7
    end_day = date.today()
    start_day = end_day - timedelta(days=days - 1)

    meals = (MealEntry.query
             .filter(MealEntry.user_id == user.id,
                     MealEntry.eaten_on >= start_day,
                     MealEntry.eaten_on <= end_day).all())
    kcal_by_day = {}
    for m in meals:
        kcal_by_day[m.eaten_on] = (kcal_by_day.get(m.eaten_on, 0)
                                   + float(m.calorie_snapshot))

    start_dt, _ = day_bounds(start_day)
    _, end_dt = day_bounds(end_day)
    workouts = (WorkoutEntry.query
                .filter(WorkoutEntry.user_id == user.id,
                        WorkoutEntry.started_at >= start_dt,
                        WorkoutEntry.started_at <= end_dt).all())
    minutes_by_day = {}
    for w in workouts:
        d = w.started_at.date()
        minutes_by_day[d] = minutes_by_day.get(d, 0) + w.duration_minutes

    all_days = [start_day + timedelta(days=i) for i in range(days)]
    labels = [d.strftime("%d/%m") for d in all_days]
    kcal_rows = list(zip(labels, [kcal_by_day.get(d, 0) for d in all_days]))
    min_rows = list(zip(labels, [minutes_by_day.get(d, 0) for d in all_days]))

    days_with_data = len(set(kcal_by_day) | set(minutes_by_day))

    return render_template(
        "charts.html", days=days, start_day=start_day, end_day=end_day,
        kcal_chart=bar_chart(kcal_rows, unit=" kcal"),
        minutes_chart=bar_chart(min_rows, unit=" min"),
        days_with_data=days_with_data)


@dashboard_bp.app_errorhandler(403)
def forbidden(e):
    return render_template("error.html", code=403,
                           message="You do not have access to this record."), 403


@dashboard_bp.app_errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404,
                           message="Page or record not found."), 404
