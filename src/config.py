"""Application configuration.

Secrets and environment-specific values come from environment variables
(see .env.example). Nothing sensitive is hard-coded here.
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "nexus.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Daily calorie target limits used by FR-11 validation.
    MIN_CALORIE_TARGET = 500
    MAX_CALORIE_TARGET = 10000

    # Password reset tokens (FR-03) expire after this many minutes.
    RESET_TOKEN_MINUTES = 30

    # "console" prints reset links to the server console instead of sending
    # email. SMTP delivery can be added later without changing the flow.
    MAIL_DELIVERY = os.environ.get("MAIL_DELIVERY", "console")
