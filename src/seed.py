"""Seed the database with starter catalogue data and a demo account.

Run once after creating the tables:

    flask --app run.py shell   # then: from app.extensions import db; db.create_all()

or simply:

    python seed.py

The food items are starter data so members can log meals right away
(FR-08/09). Administrators manage the catalogue from Phase 5 onward.
"""
from app import create_app
from app.extensions import db
from app.models import FoodItem, Profile, User

FOODS = [
    # name, serving unit, kcal per unit
    ("White rice, cooked", "cup (158g)", 205),
    ("Brown rice, cooked", "cup (195g)", 216),
    ("Baladi bread", "loaf (60g)", 160),
    ("Pasta, cooked", "cup (140g)", 220),
    ("Chicken breast, grilled", "100g", 165),
    ("Beef, cooked", "100g", 250),
    ("Eggs, boiled", "piece (50g)", 78),
    ("Foul medames", "cup (170g)", 187),
    ("Falafel (taameya)", "piece (17g)", 57),
    ("Lentil soup", "cup (240g)", 140),
    ("Potatoes, boiled", "100g", 87),
    ("French fries", "100g", 312),
    ("Tomatoes", "piece (123g)", 22),
    ("Cucumber", "piece (200g)", 30),
    ("Banana", "piece (118g)", 105),
    ("Apple", "piece (182g)", 95),
    ("Orange", "piece (131g)", 62),
    ("Dates", "piece (7g)", 20),
    ("Milk, whole", "cup (244g)", 149),
    ("Yogurt, plain", "cup (245g)", 154),
    ("White cheese, light", "30g", 70),
    ("Feta cheese", "30g", 75),
    ("Honey", "tablespoon (21g)", 64),
    ("Olive oil", "tablespoon (14g)", 119),
    ("Koshari", "plate (300g)", 550),
    ("Shawarma, chicken", "sandwich (200g)", 400),
    ("Pizza, cheese", "slice (107g)", 285),
    ("Orange juice", "cup (248g)", 112),
]

DEMO_EMAIL = "demo@nexus.local"
DEMO_PASSWORD = "demo1234"


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        added = 0
        for name, unit, kcal in FOODS:
            exists = FoodItem.query.filter_by(name=name).first()
            if not exists:
                db.session.add(FoodItem(name=name, serving_unit=unit,
                                        calories_per_unit=kcal,
                                        is_active=True))
                added += 1

        if not User.query.filter_by(email=DEMO_EMAIL).first():
            demo = User(email=DEMO_EMAIL, role="member", status="active")
            demo.set_password(DEMO_PASSWORD)
            demo.profile = Profile(display_name="Demo Member",
                                   daily_calorie_target=2200)
            db.session.add(demo)

        db.session.commit()
        print("Seeded %d new food items. Demo account: %s / %s"
              % (added, DEMO_EMAIL, DEMO_PASSWORD))


if __name__ == "__main__":
    seed()
