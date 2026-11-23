"""Account models: User, Profile and PasswordResetToken.

Table and column names follow the Phase 3 design document (section 4.4).
"""
import secrets
from datetime import datetime, timedelta

from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False, default="member")
    status = db.Column(db.String(20), nullable=False, default="active")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    profile = db.relationship("Profile", backref="user", uselist=False,
                              cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def verify_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    @property
    def is_admin(self):
        return self.role == "admin"


class Profile(db.Model):
    __tablename__ = "profiles"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    display_name = db.Column(db.String(100), nullable=False)
    preferences = db.Column(db.Text, nullable=True)
    daily_calorie_target = db.Column(db.Numeric(8, 2), nullable=True)


class PasswordResetToken(db.Model):
    """Single-use, expiring reset token. Only the hash is stored."""

    __tablename__ = "reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token_hash = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)

    @classmethod
    def create_for(cls, user):
        """Return (token_record, raw_token). The raw token is shown once."""
        raw_token = secrets.token_urlsafe(32)
        minutes = current_app.config["RESET_TOKEN_MINUTES"]
        record = cls(
            user_id=user.id,
            token_hash=generate_password_hash(raw_token),
            expires_at=datetime.utcnow() + timedelta(minutes=minutes),
        )
        # Any earlier unused tokens for this account stop being valid.
        for old in cls.query.filter_by(user_id=user.id, used_at=None).all():
            old.used_at = datetime.utcnow()
        db.session.add(record)
        return record, raw_token

    def is_valid(self):
        return self.used_at is None and datetime.utcnow() < self.expires_at

    def matches(self, raw_token):
        return check_password_hash(self.token_hash, raw_token)

    def mark_used(self):
        self.used_at = datetime.utcnow()
