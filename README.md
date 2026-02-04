# Smart Student Expense & Budget System - Backend

A FastAPI-based backend for student financial management with expense tracking, budget monitoring, and AI-powered advisory alerts.

## Features

- **Student & Budget Management**: Monthly budget tracking with automatic resets
- **Daily Expense Checklist**: Fixed daily expense categories with checkbox-based submission
- **Investment Tracking**: Track investments with monthly interest calculations
- **AI Advisory System**: Rule-based alerts and suggestions (read-only, no auto-actions)

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy
- **Auth**: Supabase Auth (JWT-based)

## Quick Start

**For detailed setup instructions, see [QUICKSTART.md](QUICKSTART.md)**

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file with your Supabase credentials:
```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT].supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
APP_NAME=Smart Student Expense & Budget System
DEBUG=True
```

### 3. Set Up Database
```bash
# Create tables
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Initialize default data
python scripts/init_db.py
```

### 4. Run Server
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
app/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration settings
├── database.py            # Database connection and session
├── models/                # SQLAlchemy models
│   ├── __init__.py
│   ├── student.py
│   ├── expense.py
│   ├── investment.py
│   └── ai_alert.py
├── schemas/               # Pydantic schemas
│   ├── __init__.py
│   ├── student.py
│   ├── expense.py
│   ├── investment.py
│   └── ai_alert.py
├── api/                   # API endpoints
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── students.py
│   │   ├── expenses.py
│   │   ├── investments.py
│   │   └── ai.py
├── services/              # Business logic
│   ├── __init__.py
│   ├── budget_service.py
│   ├── investment_service.py
│   └── ai_service.py
├── auth/                  # Authentication
│   ├── __init__.py
│   └── middleware.py
└── alembic/               # Database migrations
    └── versions/
```

## Important Notes

- **Financial Data**: All financial transactions are append-only for audit purposes
- **AI System**: The AI module only reads data and creates alerts. It never modifies budgets, expenses, or investments automatically.
- **Daily Expenses**: Only checked expense categories are saved. Unchecked categories are ignored.
