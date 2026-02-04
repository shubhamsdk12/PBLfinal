# Complete Setup Guide - Full Stack Application

This guide will help you set up both the backend and frontend for the Smart Student Expense & Budget System.

## 📦 Project Structure

```
spendwise/
├── app/                    # Backend (FastAPI)
│   ├── api/               # API endpoints
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── main.py            # FastAPI app
├── frontend/               # Frontend (React)
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/   # Reusable components
│   │   └── lib/          # API client, utilities
│   └── package.json
└── alembic/               # Database migrations
```

## 🚀 Quick Start

### Backend Setup

1. **Navigate to project root**:
   ```bash
   cd F:\spendwise
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file** (in project root):
   ```env
   DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
   SUPABASE_URL=https://[PROJECT].supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_JWT_SECRET=your-jwt-secret
   APP_NAME=Smart Student Expense & Budget System
   DEBUG=True
   ```

4. **Set up database**:
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   python scripts/init_db.py
   ```

5. **Start backend server**:
   ```bash
   python run_server.py
   # Or: uvicorn app.main:app --reload
   ```
   
   Backend runs at: http://localhost:8000

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create `.env` file** (in frontend directory):
   ```env
   VITE_API_URL=http://localhost:8000
   VITE_SUPABASE_URL=https://[PROJECT].supabase.co
   VITE_SUPABASE_ANON_KEY=your-anon-key
   ```

4. **Start frontend server**:
   ```bash
   npm run dev
   ```
   
   Frontend runs at: http://localhost:3000

## 🔑 Getting Supabase Credentials

1. Go to https://supabase.com and sign in
2. Open your project (or create a new one)
3. **Settings** → **API**:
   - Copy **Project URL** → `SUPABASE_URL` / `VITE_SUPABASE_URL`
   - Copy **anon public** key → `SUPABASE_KEY` / `VITE_SUPABASE_ANON_KEY`
   - Copy **JWT Secret** → `SUPABASE_JWT_SECRET` (backend only)
4. **Settings** → **Database**:
   - Copy **Connection string** → `DATABASE_URL` (backend only)
   - Replace `[YOUR-PASSWORD]` with your database password

## ✅ Verification

### Backend
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs
- Test endpoint: `curl http://localhost:8000/expenses/categories`

### Frontend
- Open: http://localhost:3000
- Register a new account
- Login and explore the dashboard

## 📋 Complete Checklist

### Backend
- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with Supabase credentials
- [ ] Database migrations run (`alembic upgrade head`)
- [ ] Default data initialized (`python scripts/init_db.py`)
- [ ] Backend server running (`python run_server.py`)

### Frontend
- [ ] Node.js 18+ installed
- [ ] Dependencies installed (`npm install` in frontend/)
- [ ] `.env` file created in frontend/ with credentials
- [ ] Frontend server running (`npm run dev`)

### Supabase
- [ ] Project created
- [ ] Auth enabled
- [ ] Database accessible
- [ ] Credentials copied

## 🎯 First Steps After Setup

1. **Register Account**: Go to http://localhost:3000/register
2. **Set Budget**: Update your monthly budget in dashboard
3. **Add Expenses**: Use the daily expense checklist
4. **Create Investment**: Set up an investment account
5. **View Alerts**: Check AI-generated recommendations

## 🔧 Troubleshooting

### Backend Issues

**Database connection error**:
- Verify `DATABASE_URL` is correct
- Check Supabase database is accessible
- Ensure password is correct

**JWT verification fails**:
- Verify `SUPABASE_JWT_SECRET` matches Supabase project
- Check token expiration

**Migration errors**:
- Ensure all models are imported
- Check database permissions

### Frontend Issues

**API connection errors**:
- Verify `VITE_API_URL` is correct
- Ensure backend is running
- Check CORS configuration

**Authentication not working**:
- Verify Supabase credentials
- Check Supabase Auth is enabled
- Ensure backend JWT secret matches

**Module not found**:
- Run `npm install` again
- Check Node.js version (18+)

## 📚 Documentation

- **Backend**: See `README.md`, `SETUP.md`, `API_REFERENCE.md`
- **Frontend**: See `frontend/README.md`, `frontend/SETUP.md`
- **Status**: See `STATUS.md`, `FRONTEND_STATUS.md`

## 🎉 You're All Set!

Both backend and frontend are complete and ready to use. Follow the setup steps above and you'll have a fully functional student expense management system!

## 💡 Tips

- Keep both servers running during development
- Use browser DevTools to debug frontend
- Use Swagger UI (http://localhost:8000/docs) to test backend
- Check console logs for errors
- Review Supabase dashboard for auth events

## 🚀 Next Steps

- Customize styling in `frontend/tailwind.config.js`
- Add more features as needed
- Set up production deployment
- Configure scheduled tasks (monthly interest)
- Add unit tests
