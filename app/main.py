"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import students, expenses, investments, ai

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Smart Student Expense & Budget System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(students.router)
app.include_router(expenses.router)
app.include_router(investments.router)
app.include_router(ai.router)


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
