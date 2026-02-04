# Setup Guide

This guide will help you set up the Smart Student Expense & Budget System backend.

## Prerequisites

- Python 3.9 or higher
- PostgreSQL database (Supabase recommended)
- Supabase account with project created

## Step 1: Clone and Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# Supabase Configuration
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Application Settings
APP_NAME=Smart Student Expense & Budget System
DEBUG=True
ENVIRONMENT=development
```

### Getting Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to **Settings** > **API**
3. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_KEY`
   - **JWT Secret** → `SUPABASE_JWT_SECRET`
4. Navigate to **Settings** > **Database**
5. Copy the connection string → `DATABASE_URL` (replace `[YOUR-PASSWORD]` with your database password)

## Step 3: Database Setup

### 3.1 Create Database Tables

Run Alembic migrations to create all database tables:

```bash
# Create initial migration (first time only)
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 3.2 Initialize Default Data

Run the initialization script to create default expense categories and templates:

```bash
python scripts/init_db.py
```

This will create:
- Default expense categories (Food, Transport, Entertainment, etc.)
- Daily expense checklist templates

## Step 4: Start the Server

```bash
# Development server with auto-reload
uvicorn app.main:app --reload

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Step 5: Set Up Scheduled Tasks (Optional)

### Monthly Interest Credit

Set up a cron job or scheduled task to credit monthly interest to investments:

```bash
# Add to crontab (runs on 1st of each month at midnight)
0 0 1 * * cd /path/to/project && python scripts/monthly_interest_task.py
```

Or use a task scheduler like:
- **Linux**: cron
- **Windows**: Task Scheduler
- **Cloud**: AWS Lambda, Google Cloud Functions, etc.

## API Authentication

All protected endpoints require a JWT token from Supabase Auth in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Testing Authentication

1. Register/login via Supabase Auth (frontend or Supabase dashboard)
2. Get the JWT token from the auth response
3. Use it in API requests:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/students/me
```

## Project Structure

```
app/
├── main.py                 # FastAPI application
├── config.py              # Configuration
├── database.py            # Database connection
├── models/                # SQLAlchemy models
├── schemas/               # Pydantic schemas
├── api/routes/            # API endpoints
├── services/              # Business logic
└── auth/                  # Authentication

alembic/                   # Database migrations
scripts/                   # Utility scripts
```

## Common Issues

### Database Connection Error

- Verify `DATABASE_URL` is correct
- Check if Supabase database is accessible
- Ensure IP is whitelisted in Supabase (if using IP restrictions)

### JWT Verification Fails

- Verify `SUPABASE_JWT_SECRET` matches your Supabase project
- Check token expiration
- Ensure token is from the correct Supabase project

### Migration Errors

- Ensure all models are imported in `app/models/__init__.py`
- Check database permissions
- Verify SQLAlchemy version compatibility

## Next Steps

1. **Frontend Integration**: Connect your React.js frontend to these APIs
2. **Testing**: Set up unit and integration tests
3. **Deployment**: Deploy to production (Heroku, AWS, etc.)
4. **Monitoring**: Set up logging and error tracking

## Support

For issues or questions, refer to:
- FastAPI documentation: https://fastapi.tiangolo.com/
- Supabase documentation: https://supabase.com/docs
- SQLAlchemy documentation: https://docs.sqlalchemy.org/
