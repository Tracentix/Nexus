"""Tracking models: WorkoutEntry (FR-05..07) and MealEntry (FR-09/10)."""
from datetime import date, datetime

from ..extensions import db

WORKOUT_TYPES = [
    "Running", "Walking", "Cycling", "Swimming", "Gym / weights",
    "Football", "Basketball", "Yoga", "Other",
]

MEAL_LABELS = ["breakfast", "lunch", "dinner", "snack"]


class WorkoutEntry(db.Model):
    __tablename__ = "workout_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False,
                        index=True)
    activity_type = db.Column(db.String(80), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    estimated_kcal = db.Column(db.Numeric(8, 2), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def validate(self):
        """Return a list of validation errors (empty means valid)."""
        errors = []
        if self.activity_type not in WORKOUT_TYPES:
            errors.append("Choose a valid workout type.")
        if self.duration_minutes is None or self.duration_minutes <= 0:
            errors.append("Duration must be a positive number of minutes.")
        if self.started_at is None:
            errors.append("Enter a valid workout date.")
        elif self.started_at.date() > date.today():
            errors.append("Workout date cannot be in the future.")
        if self.estimated_kcal is not None and self.estimated_kcal < 0:
            errors.append("Calories cannot be negative.")
        return errors


class MealEntry(db.Model):
    __tablename__ = "meal_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False,
                        index=True)
    food_id = db.Column(db.Integer, db.ForeignKey("food_items.id"),
                        nullable=False)
    eaten_on = db.Column(db.Date, nullable=False)
    meal_label = db.Column(db.String(32), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    calorie_snapshot = db.Column(db.Numeric(10, 2), nullable=False)

    food = db.relationship("FoodItem")

    def recalculate_calories(self):
        """Snapshot calories from the catalogue value and quantity (FR-09).

        The snapshot is stored so later catalogue edits do not rewrite the
        member's history.
        """
        self.calorie_snapshot = round(float(self.food.calories_per_unit)
                                      * float(self.quantity), 2)

    def validate(self):
        errors = []
        if self.food is None or not self.food.is_selectable():
            errors.append("Choose an active food item from the catalogue.")
        if self.meal_label not in MEAL_LABELS:
            errors.append("Choose a valid meal label.")
        if self.quantity is None or float(self.quantity) <= 0:
            errors.append("Quantity must be a positive number.")
        if self.eaten_on is None:
            errors.append("Enter a valid date.")
        elif self.eaten_on > date.today():
            errors.append("Meal date cannot be in the future.")
        return errors


def day_bounds(day):
    """Start/end datetimes for a calendar day, used to scope queries."""
    start = datetime.combine(day, datetime.min.time())
    end = datetime.combine(day, datetime.max.time())
    return start, end
