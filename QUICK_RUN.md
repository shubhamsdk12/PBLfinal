# Quick Run Guide

## ✅ Servers Started!

Both backend and frontend servers have been started in separate windows.

## 🌐 Access URLs

- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **Frontend App**: http://localhost:3000

## ⚠️ Important: Configure Environment Variables

The servers are running with **placeholder credentials**. You need to update the `.env` files with your real Supabase credentials:

### Backend `.env` (in project root)
```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT].supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
APP_NAME=Smart Student Expense & Budget System
DEBUG=True
```

### Frontend `.env` (in frontend/ directory)
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://[PROJECT].supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

## 🔧 Getting Supabase Credentials

1. Go to https://supabase.com
2. Open your project
3. **Settings** → **API**: Copy URL and anon key
4. **Settings** → **API**: Copy JWT secret (backend only)
5. **Settings** → **Database**: Copy connection string (backend only)

## 📋 Next Steps

1. **Update `.env` files** with real credentials
2. **Restart servers** if needed (they auto-reload on file changes)
3. **Set up database** (if not done):
   ```bash
   alembic upgrade head
   python scripts/init_db.py
   ```
4. **Open frontend**: http://localhost:3000
5. **Register** a new account
6. **Start using** the app!

## 🛑 Stopping Servers

Close the PowerShell windows where the servers are running, or press `Ctrl+C` in each window.

## 🚀 Alternative: Use Start Scripts

You can also use the provided scripts:

**Windows (PowerShell)**:
```powershell
.\start_servers.ps1
```

**Windows (CMD)**:
```cmd
start_servers.bat
```

## ✅ Verification

- **Backend Health**: http://localhost:8000/health
- **Backend Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

## 🐛 Troubleshooting

### Backend not starting
- Check `.env` file exists and has correct values
- Verify database is accessible
- Check port 8000 is not in use

### Frontend not starting
- Check `frontend/.env` file exists
- Verify Node.js is installed (`node --version`)
- Check port 3000 is not in use
- Run `npm install` in frontend directory

### Connection errors
- Ensure both servers are running
- Verify API URL in frontend `.env` matches backend
- Check CORS settings in backend

## 📚 Full Documentation

- **Complete Setup**: See `COMPLETE_SETUP.md`
- **Backend Setup**: See `SETUP.md`
- **Frontend Setup**: See `frontend/SETUP.md`
