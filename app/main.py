"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api.routes import students, expenses, investments, ai, auth, chatbot

# Import all models so SQLAlchemy knows about them
from app.models import (
    Student, StudentCategoryBudget,
    ExpenseCategory, DailyExpenseTemplate, Expense, MonthlyBudgetSnapshot,
    Investment, InvestmentTransaction,
    AIAlert,
)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Smart Student Expense & Budget System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(expenses.router)
app.include_router(investments.router)
app.include_router(ai.router)
app.include_router(chatbot.router)


@app.on_event("startup")
def on_startup():
    """Create all database tables on startup and seed initial data."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created/verified")

    # Log API key configuration status
    fh = "SET" if settings.MARKETAUX_API_TOKEN else "NOT SET"
    gq = "SET" if settings.GROQ_API_KEY else "NOT SET"
    print(f"[CONFIG] MARKETAUX_API_TOKEN: {fh}")
    print(f"[CONFIG] GROQ_API_KEY:    {gq}")
    print(f"[CONFIG] DATABASE_URL:    {settings.DATABASE_URL[:30]}...")

    # Run seed data
    try:
        from app.seed_data import run_seeder
        run_seeder()
    except Exception as e:
        print(f"[WARNING] Seed data: {e}")


@app.get("/")
def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Smart Student Expense & Budget System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}
