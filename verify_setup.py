"""
Verification script to check if the project is properly configured.
Run: python verify_setup.py
"""
import sys

def check_imports():
    """Check all required packages are installed."""
    print("\n1. Checking Python packages...")
    required = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("psycopg2", "PostgreSQL driver"),
        ("pydantic", "Pydantic"),
        ("pydantic_settings", "Pydantic Settings"),
        ("jose", "python-jose (JWT)"),
        ("passlib", "Passlib (password hashing)"),
    ]

    all_ok = True
    for module, name in required:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - NOT INSTALLED")
            all_ok = False

    return all_ok


def check_env():
    """Check .env file exists and has required variables."""
    print("\n2. Checking .env configuration...")
    import os

    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        print("  ❌ .env file not found")
        return False

    required_vars = ["DATABASE_URL", "JWT_SECRET"]
    with open(env_path) as f:
        content = f.read()

    all_ok = True
    for var in required_vars:
        if var in content:
            print(f"  ✅ {var} is set")
        else:
            print(f"  ❌ {var} is NOT set")
            all_ok = False

    return all_ok


def check_database():
    """Check database connection."""
    print("\n3. Checking PostgreSQL connection...")
    try:
        from app.config import settings
        from sqlalchemy import create_engine, text

        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.close()
        print(f"  ✅ Connected to PostgreSQL")
        print(f"     URL: {settings.DATABASE_URL[:50]}...")
        return True
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        print("\n  Make sure:")
        print("  - PostgreSQL is running on localhost:5432")
        print("  - Database 'spendwise' exists")
        print("  - Username/password in .env are correct")
        return False


def check_app_imports():
    """Check if the FastAPI app can be imported."""
    print("\n4. Checking FastAPI app imports...")
    try:
        from app.main import app
        print("  ✅ FastAPI app imports successfully")
        return True
    except Exception as e:
        print(f"  ❌ App import failed: {e}")
        return False


def main():
    print("=" * 50)
    print("Smart Student Expense System - Setup Verification")
    print("=" * 50)

    results = []
    results.append(("Python packages", check_imports()))
    results.append(("Environment config", check_env()))
    results.append(("Database connection", check_database()))
    results.append(("App imports", check_app_imports()))

    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All checks passed! You can start the server with:")
        print("   python run_server.py")
        print("\n   Frontend: cd frontend && npm run dev")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
