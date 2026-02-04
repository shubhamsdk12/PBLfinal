"""
Database initialization script.
Creates initial expense categories and daily expense templates.
Run this after running Alembic migrations.
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.expense import ExpenseCategory, DailyExpenseTemplate
from app.config import settings


def init_expense_categories(db):
    """Initialize default expense categories."""
    categories = [
        {"name": "Food", "description": "Meals, groceries, snacks"},
        {"name": "Transport", "description": "Public transport, fuel, parking"},
        {"name": "Entertainment", "description": "Movies, games, subscriptions"},
        {"name": "Shopping", "description": "Clothing, electronics, personal items"},
        {"name": "Bills", "description": "Utilities, phone, internet"},
        {"name": "Education", "description": "Books, courses, supplies"},
        {"name": "Health", "description": "Medical, pharmacy, fitness"},
        {"name": "Other", "description": "Miscellaneous expenses"},
    ]
    
    for cat_data in categories:
        existing = db.query(ExpenseCategory).filter(
            ExpenseCategory.name == cat_data["name"]
        ).first()
        
        if not existing:
            category = ExpenseCategory(
                name=cat_data["name"],
                description=cat_data["description"]
            )
            db.add(category)
            print(f"Created category: {cat_data['name']}")
        else:
            print(f"Category already exists: {cat_data['name']}")
    
    db.commit()


def init_daily_templates(db):
    """Initialize daily expense checklist templates."""
    # Get categories
    categories = {
        cat.name: cat.id
        for cat in db.query(ExpenseCategory).all()
    }
    
    # Define template order (which categories appear in daily checklist)
    template_order = [
        "Food",
        "Transport",
        "Entertainment",
        "Shopping",
        "Bills",
        "Education",
        "Health",
        "Other",
    ]
    
    display_order = 0
    for category_name in template_order:
        if category_name in categories:
            existing = db.query(DailyExpenseTemplate).filter(
                DailyExpenseTemplate.category_id == categories[category_name]
            ).first()
            
            if not existing:
                template = DailyExpenseTemplate(
                    category_id=categories[category_name],
                    display_order=display_order,
                    is_active=True
                )
                db.add(template)
                print(f"Created template: {category_name} (order: {display_order})")
            else:
                print(f"Template already exists: {category_name}")
            
            display_order += 1
    
    db.commit()


def main():
    """Main initialization function."""
    print("Initializing database...")
    print(f"Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    
    # Create tables (if not using Alembic)
    # Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("\n1. Initializing expense categories...")
        init_expense_categories(db)
        
        print("\n2. Initializing daily expense templates...")
        init_daily_templates(db)
        
        print("\n✅ Database initialization complete!")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
