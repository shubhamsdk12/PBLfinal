# Fix Environment Configuration

## ⚠️ Current Issue

The frontend is trying to connect to `placeholder.supabase.co` which doesn't exist. You need to update the `.env` files with your real Supabase credentials.

## 🔧 Quick Fix

### Step 1: Get Your Supabase Credentials

1. Go to https://supabase.com and sign in
2. Open your project (or create a new one if you don't have one)
3. Navigate to **Settings** → **API**
4. Copy these values:
   - **Project URL** (e.g., `https://abcdefgh.supabase.co`)
   - **anon public** key (long string starting with `eyJ...`)

### Step 2: Update Frontend `.env`

Edit `frontend/.env` and replace the placeholder values:

```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://YOUR-PROJECT-REF.supabase.co
VITE_SUPABASE_ANON_KEY=YOUR-ANON-KEY-HERE
```

**Important**: After updating `.env`, restart the frontend server (stop and start again).

### Step 3: Update Backend `.env`

Edit `.env` in the project root and replace with real values:

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_KEY=YOUR-ANON-KEY-HERE
SUPABASE_JWT_SECRET=YOUR-JWT-SECRET-HERE
APP_NAME=Smart Student Expense & Budget System
DEBUG=True
ENVIRONMENT=development
```

To get the JWT Secret:
- Go to **Settings** → **API** in Supabase
- Scroll down to find **JWT Secret**

To get Database URL:
- Go to **Settings** → **Database**
- Copy the connection string
- Replace `[YOUR-PASSWORD]` with your database password

### Step 4: Restart Servers

After updating both `.env` files:

1. **Stop both servers** (close the PowerShell windows or press Ctrl+C)
2. **Restart them** using:
   ```powershell
   .\start_servers.ps1
   ```

Or manually:
- Backend: `python run_server.py`
- Frontend: `cd frontend && npm run dev`

## ✅ Verification

After updating and restarting:

1. **Frontend**: http://localhost:3000 should load without errors
2. **Try registering**: The signup should work now
3. **Check console**: No more "Failed to fetch" errors

## 🆘 Don't Have a Supabase Project?

If you don't have a Supabase account yet:

1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up (free tier available)
4. Create a new project
5. Wait for project to initialize (2-3 minutes)
6. Follow Step 1 above to get credentials

## 📝 Note About React Router Warnings

The React Router warnings are just future compatibility notices. They don't affect functionality. You can ignore them for now, or add this to your router config later:

```typescript
// In App.tsx, add future flags to BrowserRouter
<BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
```
