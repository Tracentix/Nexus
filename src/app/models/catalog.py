"""Food catalogue model (FR-08)."""
from ..extensions import db


class FoodItem(db.Model):
    __tablename__ = "food_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    serving_unit = db.Column(db.String(40), nullable=False)
    calories_per_unit = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def is_selectable(self):
        """Only active items can be chosen for new meal entries."""
        return self.is_active

    @classmethod
    def search(cls, term):
        """Partial, case-insensitive name search over active items."""
        query = cls.query.filter_by(is_active=True)
        if term:
            query = query.filter(cls.name.ilike("%" + term.strip() + "%"))
        return query.order_by(cls.name).all()
