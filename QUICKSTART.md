# Quick Start Guide

Get the Smart Student Expense & Budget System backend running in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- PostgreSQL database (Supabase recommended)
- Supabase account

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up Environment Variables

Create a `.env` file in the project root:

```env
# Database (from Supabase Dashboard > Settings > Database)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Supabase (from Supabase Dashboard > Settings > API)
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here

# App Settings
APP_NAME=Smart Student Expense & Budget System
DEBUG=True
ENVIRONMENT=development
```

### How to Get Supabase Credentials:

1. Go to https://supabase.com and sign in
2. Open your project (or create a new one)
3. Go to **Settings** → **API**:
   - Copy **Project URL** → `SUPABASE_URL`
   - Copy **anon public** key → `SUPABASE_KEY`
   - Copy **JWT Secret** → `SUPABASE_JWT_SECRET`
4. Go to **Settings** → **Database**:
   - Copy **Connection string** → `DATABASE_URL`
   - Replace `[YOUR-PASSWORD]` with your database password

## Step 3: Set Up Database

### 3.1 Create Database Tables

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations to create tables
alembic upgrade head
```

### 3.2 Initialize Default Data

```bash
# Create expense categories and daily templates
python scripts/init_db.py
```

This creates:
- 8 default expense categories (Food, Transport, etc.)
- Daily expense checklist templates

## Step 4: Run the Server

### Development Mode (with auto-reload)

```bash
uvicorn app.main:app --reload
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Step 5: Verify It's Working

1. **Check Health**: Open http://localhost:8000/health
   - Should return: `{"status": "healthy"}`

2. **View API Docs**: Open http://localhost:8000/docs
   - Interactive Swagger UI with all endpoints

3. **View ReDoc**: Open http://localhost:8000/redoc
   - Alternative API documentation

## Testing the API

### 1. Get Expense Categories (No Auth Required)

```bash
curl http://localhost:8000/expenses/categories
```

### 2. Create a Student Account

First, get a JWT token from Supabase Auth (via your frontend or Supabase dashboard), then:

```bash
curl -X POST http://localhost:8000/students/ \
  -H "Content-Type: application/json" \
  -d '{
    "supabase_user_id": "your-supabase-user-id",
    "email": "student@example.com",
    "name": "John Doe",
    "monthly_budget": 1000.00,
    "budget_start_date": "2024-01-01"
  }'
```

### 3. Get Student Info (Requires Auth)

```bash
curl http://localhost:8000/students/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Common Issues & Solutions

### Issue: "Module not found" error

**Solution**: Make sure you're in the project root directory and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Database connection error

**Solution**: 
- Verify `DATABASE_URL` is correct
- Check if database password is correct
- Ensure Supabase database is accessible
- Check IP whitelist in Supabase (Settings > Database > Connection Pooling)

### Issue: "No module named 'app'"

**Solution**: Make sure you're running from the project root:
```bash
# Should be in: F:\spendwise
python -m uvicorn app.main:app --reload
```

### Issue: Migration errors

**Solution**: 
- Ensure all models are imported in `app/models/__init__.py`
- Check database permissions
- Try: `alembic upgrade head --sql` to see SQL without executing

### Issue: JWT verification fails

**Solution**:
- Verify `SUPABASE_JWT_SECRET` matches your Supabase project
- Check token expiration
- Ensure token is from the correct Supabase project

## Development Workflow

1. **Start server**: `uvicorn app.main:app --reload`
2. **Make changes**: Code auto-reloads (thanks to `--reload`)
3. **Test endpoints**: Use Swagger UI at http://localhost:8000/docs
4. **Check logs**: Server logs appear in terminal

## Next Steps

- **Frontend Integration**: Connect your React.js app to these APIs
- **Testing**: Set up unit/integration tests
- **Deployment**: Deploy to production (Heroku, AWS, etc.)
- **Scheduled Tasks**: Set up cron job for monthly interest credit

## Useful Commands

```bash
# Run server
uvicorn app.main:app --reload

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Initialize database
python scripts/init_db.py

# Run monthly interest task
python scripts/monthly_interest_task.py
```

## Need Help?

- Check `SETUP.md` for detailed setup instructions
- Check `API_REFERENCE.md` for API documentation
- Check `PROJECT_SUMMARY.md` for architecture overview
- View interactive docs at http://localhost:8000/docs
