"""Shared extensions, created once and bound to the app in the factory."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
