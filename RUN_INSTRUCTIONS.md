# How to Run the Application

## Quick Run (After Setup)

Once you have your `.env` file configured:

```bash
python run_server.py
```

Or directly with uvicorn:

```bash
uvicorn app.main:app --reload
```

## Complete Setup & Run

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create .env File
Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here
APP_NAME=Smart Student Expense & Budget System
DEBUG=True
ENVIRONMENT=development
```

### Step 3: Set Up Database
```bash
# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head

# Initialize default data
python scripts/init_db.py
```

### Step 4: Run Server
```bash
python run_server.py
```

The server will start at: **http://localhost:8000**

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Verification

1. **Check Health**: Open http://localhost:8000/health
   - Should return: `{"status": "healthy"}`

2. **View API Docs**: Open http://localhost:8000/docs
   - Interactive Swagger UI

3. **Test Endpoint** (no auth required):
   ```bash
   curl http://localhost:8000/expenses/categories
   ```

## Troubleshooting

### "Module not found" error
- Run: `pip install -r requirements.txt`

### ".env file not found" error
- Create `.env` file with required variables (see Step 2)

### Database connection error
- Verify `DATABASE_URL` is correct
- Check Supabase database is accessible
- Ensure password is correct

### Port already in use
- Change port: `uvicorn app.main:app --port 8001`
- Or kill process using port 8000

## Next Steps

- Connect your React.js frontend
- Test API endpoints via Swagger UI
- Set up scheduled tasks for monthly interest
