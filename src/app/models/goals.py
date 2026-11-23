"""Goal and measurement models (FR-12, FR-15)."""
from datetime import date

from ..extensions import db

GOAL_TYPES = [
    "weight", "workouts_per_week", "daily_calories", "distance_km", "other",
]

GOAL_STATUSES = ["active", "completed", "inactive"]

MEASUREMENT_KINDS = {
    "weight": "kg",
    "waist": "cm",
    "chest": "cm",
    "hips": "cm",
    "body_fat": "%",
}


class FitnessGoal(db.Model):
    __tablename__ = "fitness_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False,
                        index=True)
    goal_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    target_value = db.Column(db.Numeric(10, 2), nullable=True)
    target_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="active")

    def validate(self):
        errors = []
        if self.goal_type not in GOAL_TYPES:
            errors.append("Choose a valid goal type.")
        if not (self.description or "").strip():
            errors.append("Describe the goal.")
        if self.target_value is not None and float(self.target_value) <= 0:
            errors.append("Target value must be positive.")
        if self.status not in GOAL_STATUSES:
            errors.append("Invalid goal status.")
        return errors

    def set_status(self, status):
        if status not in GOAL_STATUSES:
            raise ValueError("unknown goal status")
        self.status = status


class BodyMeasurement(db.Model):
    __tablename__ = "body_measurements"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False,
                        index=True)
    measured_on = db.Column(db.Date, nullable=False)
    kind = db.Column(db.String(40), nullable=False)
    value = db.Column(db.Numeric(10, 2), nullable=False)
    unit = db.Column(db.String(20), nullable=False)

    def validate(self):
        errors = []
        if self.kind not in MEASUREMENT_KINDS:
            errors.append("Choose a valid measurement kind.")
        if self.value is None or float(self.value) <= 0:
            errors.append("Value must be a positive number.")
        if self.measured_on is None:
            errors.append("Enter a valid date.")
        elif self.measured_on > date.today():
            errors.append("Measurement date cannot be in the future.")
        return errors
