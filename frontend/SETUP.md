# Frontend Setup Guide

Complete setup instructions for the React.js frontend.

## Prerequisites

- Node.js 18+ and npm
- Backend API running (see backend README)
- Supabase account with project created

## Step 1: Install Dependencies

```bash
cd frontend
npm install
```

## Step 2: Get Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **API**
3. Copy:
   - **Project URL** → `VITE_SUPABASE_URL`
   - **anon/public key** → `VITE_SUPABASE_ANON_KEY`

## Step 3: Create Environment File

Create a `.env` file in the `frontend` directory:

```env
# Backend API URL (default: http://localhost:8000)
VITE_API_URL=http://localhost:8000

# Supabase Configuration
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

## Step 4: Start Development Server

```bash
npm run dev
```

The app will open at http://localhost:3000

## Step 5: Test the Application

1. **Register**: Create a new account
2. **Login**: Sign in with your credentials
3. **Dashboard**: View budget status
4. **Expenses**: Add daily expenses
5. **Investments**: Create investment account
6. **Alerts**: View AI-generated alerts

## Common Issues

### Port 3000 already in use
Change the port in `vite.config.ts`:
```typescript
server: {
  port: 3001, // Change to available port
}
```

### CORS errors
Ensure backend CORS is configured to allow `http://localhost:3000`

### Authentication not working
- Verify Supabase credentials
- Check Supabase Auth is enabled
- Ensure backend JWT secret matches

### API connection failed
- Verify backend is running
- Check `VITE_API_URL` is correct
- Test backend health endpoint: `curl http://localhost:8000/health`

## Production Build

```bash
npm run build
```

Output will be in `dist/` directory. Deploy this folder to your hosting service.

## Development Tips

- Use React DevTools browser extension
- Check browser console for errors
- Use Network tab to debug API calls
- Hot reload is enabled by default
