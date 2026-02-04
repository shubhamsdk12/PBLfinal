# Environment Setup Guide - Fix Connection Errors

## 🔴 Current Error

You're seeing this error:
```
Failed to load resource: net::ERR_NAME_NOT_RESOLVED
placeholder.supabase.co/auth/v1/signup
```

This means the frontend is trying to connect to a placeholder Supabase URL that doesn't exist.

## ✅ Solution: Update Environment Variables

### Step 1: Get Supabase Credentials

1. **Go to Supabase**: https://supabase.com
2. **Sign in** or create an account (free tier available)
3. **Create a project** (if you don't have one):
   - Click "New Project"
   - Choose organization
   - Enter project name
   - Set database password
   - Choose region
   - Wait 2-3 minutes for setup

4. **Get API Credentials**:
   - Go to **Settings** → **API**
   - Copy **Project URL** (looks like: `https://abcdefghijklmnop.supabase.co`)
   - Copy **anon public** key (long string starting with `eyJ...`)

5. **Get Database URL** (for backend):
   - Go to **Settings** → **Database**
   - Under "Connection string", copy the URI
   - It looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres`
   - Replace `[YOUR-PASSWORD]` with your actual database password

6. **Get JWT Secret** (for backend):
   - Still in **Settings** → **API**
   - Scroll down to find **JWT Secret**
   - Copy this value

### Step 2: Update Frontend `.env`

Edit the file: `frontend/.env`

Replace with your real values:
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://YOUR-PROJECT-REF.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example**:
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://abcdefghijklmnop.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzODU2Nzg5MCwiZXhwIjoxOTU0MTQzODkwfQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Update Backend `.env`

Edit the file: `.env` (in project root)

Replace with your real values:
```env
DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.YOUR-PROJECT-REF.supabase.co:5432/postgres
SUPABASE_URL=https://YOUR-PROJECT-REF.supabase.co
SUPABASE_KEY=YOUR-ANON-KEY-HERE
SUPABASE_JWT_SECRET=YOUR-JWT-SECRET-HERE
APP_NAME=Smart Student Expense & Budget System
DEBUG=True
ENVIRONMENT=development
```

**Example**:
```env
DATABASE_URL=postgresql://postgres:mypassword123@db.abcdefghijklmnop.supabase.co:5432/postgres
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-super-secret-jwt-token-here
APP_NAME=Smart Student Expense & Budget System
DEBUG=True
ENVIRONMENT=development
```

### Step 4: Restart Servers

**Important**: After updating `.env` files, you MUST restart both servers:

1. **Stop the servers**:
   - Close the PowerShell windows
   - Or press `Ctrl+C` in each window

2. **Restart them**:
   ```powershell
   .\start_servers.ps1
   ```

   Or manually:
   - Backend: `python run_server.py`
   - Frontend: `cd frontend && npm run dev`

### Step 5: Set Up Database (First Time Only)

If you haven't set up the database yet:

```bash
# Create database tables
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Initialize default data (categories, templates)
python scripts/init_db.py
```

## ✅ Verification

After updating and restarting:

1. **Open browser console** (F12)
2. **Go to**: http://localhost:3000
3. **Check for errors**: Should see no "Failed to fetch" errors
4. **Try registering**: Click "Sign up" and create an account
5. **Should work!** ✅

## 🎯 Quick Checklist

- [ ] Have Supabase account
- [ ] Created Supabase project
- [ ] Got Project URL from Settings → API
- [ ] Got anon key from Settings → API
- [ ] Got JWT Secret from Settings → API
- [ ] Got Database URL from Settings → Database
- [ ] Updated `frontend/.env` with real values
- [ ] Updated `.env` (root) with real values
- [ ] Restarted both servers
- [ ] Ran database migrations (if first time)
- [ ] Tested registration - works! ✅

## 🆘 Still Having Issues?

### Error: "Failed to fetch"
- ✅ Check `.env` files have real Supabase URLs (not placeholder)
- ✅ Restart servers after updating `.env`
- ✅ Check Supabase project is active
- ✅ Verify anon key is correct

### Error: "Database connection failed"
- ✅ Check `DATABASE_URL` has correct password
- ✅ Verify database is accessible in Supabase dashboard
- ✅ Check IP restrictions in Supabase (Settings → Database)

### Error: "Invalid JWT"
- ✅ Verify `SUPABASE_JWT_SECRET` matches Supabase project
- ✅ Check JWT secret is from correct project

## 📝 Note: React Router Warnings

The React Router warnings are fixed now. They were just future compatibility notices and don't affect functionality.
