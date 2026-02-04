# Smart Student Expense & Budget System - Frontend

A modern React.js frontend for student financial management with expense tracking, budget monitoring, and AI-powered advisory alerts.

## Features

- 🔐 **Authentication**: Supabase Auth integration
- 📊 **Dashboard**: Budget status, spending overview, and quick actions
- 📝 **Daily Expense Checklist**: Checkbox-based expense tracking
- 💰 **Investment Tracking**: Manage investments with interest calculations
- 🤖 **AI Alerts**: Smart recommendations and budget warnings
- 🎨 **Modern UI**: Clean, student-friendly design with Tailwind CSS

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **Auth**: Supabase Auth
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at http://localhost:3000

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable components
│   │   ├── Layout.tsx
│   │   └── ProtectedRoute.tsx
│   ├── contexts/         # React contexts
│   │   └── AuthContext.tsx
│   ├── lib/              # Utilities and API client
│   │   ├── api.ts
│   │   └── supabase.ts
│   ├── pages/            # Page components
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Expenses.tsx
│   │   ├── Investments.tsx
│   │   └── Alerts.tsx
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── config.ts         # Configuration
├── public/               # Static assets
├── index.html
├── package.json
└── vite.config.ts
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Features Overview

### Authentication
- User registration and login via Supabase Auth
- Protected routes with automatic redirect
- Session management

### Dashboard
- Budget status with health indicators
- Spending overview and progress
- Quick action buttons
- Daily budget allowance calculation

### Daily Expense Checklist
- Fixed expense categories
- Checkbox-based submission (only checked items saved)
- Additional/unplanned expenses
- Date selection for historical entries
- View today's expenses

### Investment Tracking
- Create investment account
- Deposit and withdraw funds
- Track interest earnings
- Transaction history
- Investment summary

### AI Alerts
- Budget risk warnings
- Spending pattern analysis
- Investment suggestions
- Alert filtering (all/unread/resolved)
- Mark as read/resolved

## API Integration

The frontend communicates with the FastAPI backend at `VITE_API_URL`. All API calls are authenticated using JWT tokens from Supabase Auth.

### API Endpoints Used

- `/students/me` - Get current student info
- `/students/me/budget-status` - Get budget status
- `/expenses/daily-checklist` - Get/submit daily checklist
- `/expenses/categories` - Get expense categories
- `/investments/me` - Investment operations
- `/ai/alerts` - AI alerts management
- `/ai/evaluate` - Trigger AI evaluation

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_URL` | Backend API URL | Yes |
| `VITE_SUPABASE_URL` | Supabase project URL | Yes |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key | Yes |

## Building for Production

```bash
npm run build
```

The production build will be in the `dist` directory.

## Deployment

The frontend can be deployed to:
- **Vercel**: Connect GitHub repo, auto-deploys
- **Netlify**: Drag & drop `dist` folder
- **AWS S3 + CloudFront**: Upload `dist` to S3 bucket
- **Any static hosting**: Serve `dist` folder

## Troubleshooting

### "Module not found" errors
- Run `npm install` to install dependencies
- Check Node.js version (requires 18+)

### API connection errors
- Verify `VITE_API_URL` is correct
- Ensure backend server is running
- Check CORS configuration in backend

### Authentication issues
- Verify Supabase credentials in `.env`
- Check Supabase Auth is enabled
- Ensure backend JWT secret matches Supabase

## Next Steps

1. Customize styling in `tailwind.config.js`
2. Add more features as needed
3. Set up CI/CD for automated deployments
4. Add unit tests with Vitest
5. Add E2E tests with Playwright

## Support

For issues or questions:
- Check backend API documentation
- Review Supabase documentation
- Check browser console for errors
