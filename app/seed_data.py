"""
Database seeder for initial expense categories and templates.

Run this script after migrations to populate the database with default categories.
Usage: python -m app.seed_data
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.expense import ExpenseCategory, DailyExpenseTemplate


DEFAULT_CATEGORIES = [
    {"name": "Food", "description": "Meals, groceries, and food-related expenses"},
    {"name": "Travel", "description": "Transportation, commute, and travel expenses"},
    {"name": "Snacks", "description": "Snacks, beverages, and small food items"},
    {"name": "Entertainment", "description": "Movies, games, and leisure activities"},
    {"name": "Printing / Misc", "description": "Printing, stationery, and miscellaneous items"},
    {"name": "Shopping", "description": "Clothing, electronics, and general shopping"},
    {"name": "Utilities", "description": "Phone bills, internet, and utility expenses"},
    {"name": "Health", "description": "Medical expenses, pharmacy, and health-related costs"},
]


def seed_categories(db: Session):
    """Seed expense categories if they don't exist."""
    existing_categories = db.query(ExpenseCategory).all()
    existing_names = {cat.name for cat in existing_categories}

    created_count = 0
    for cat_data in DEFAULT_CATEGORIES:
        if cat_data["name"] not in existing_names:
            category = ExpenseCategory(
                name=cat_data["name"],
                description=cat_data["description"]
            )
            db.add(category)
            created_count += 1

    db.commit()
    print(f"Created {created_count} new expense categories")
    return created_count


def seed_daily_templates(db: Session):
    """Seed daily expense templates based on common categories."""
    # Categories that should be in the daily checklist
    daily_checklist_categories = [
        "Food",
        "Travel",
        "Snacks",
        "Entertainment",
        "Printing / Misc",
    ]

    existing_templates = db.query(DailyExpenseTemplate).all()
    existing_category_ids = {t.category_id for t in existing_templates}

    created_count = 0
    for order, cat_name in enumerate(daily_checklist_categories):
        category = db.query(ExpenseCategory).filter(
            ExpenseCategory.name == cat_name
        ).first()

        if category and category.id not in existing_category_ids:
            template = DailyExpenseTemplate(
                category_id=category.id,
                display_order=order + 1,
                is_active=True
            )
            db.add(template)
            created_count += 1

    db.commit()
    print(f"Created {created_count} new daily expense templates")
    return created_count


def run_seeder():
    """Run all seeders."""
    print("Starting database seeding...")
    db = SessionLocal()
    try:
        seed_categories(db)
        seed_daily_templates(db)
        print("Database seeding completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seeder()
