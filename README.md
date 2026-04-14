# Smart Student Expense & Budget System

A full-stack financial management application for students with expense tracking, budget monitoring, AI-powered alerts, live market news, and an intelligent chatbot assistant.

## Features

- **Budget Management**: Set monthly budgets with per-category daily limits
- **Daily Expense Checklist**: Track daily expenses with checkbox-based submission
- **Investment Tracking**: Manage investments with monthly interest calculations
- **Live Market News**: Real-time financial news via MarketAux API (TSLA, AMZN, MSFT, AAPL, GOOGL)
- **AI Advisory System**: Rule-based alerts for budget risks and spending patterns
- **Chatbot Assistant**: Ask questions about your budget, expenses, and financial status

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Frontend | React + TypeScript + Vite |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Styling | Tailwind CSS |
| Charts | Recharts |

## Quick Start

### 1. Clone & Install Dependencies

```bash
# Backend
cd pblinit
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Configure Environment

Create `.env` file in the root directory:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/spendwise
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168
APP_NAME=Smart Student Expense & Budget System
DEBUG=false

# AI Chatbot (Groq)
GROQ_API_KEY=your-groq-api-key

# Live Market News (MarketAux)
MARKETAUX_API_TOKEN=your-marketaux-api-token
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

### 3. Run the Application

```bash
# Terminal 1 - Backend
cd pblinit
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd pblinit/frontend
npm run dev
```

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173

## Demo Accounts

See [DEMO_ACCOUNTS.md](DEMO_ACCOUNTS.md) for 5 pre-configured test accounts showcasing different AI alert scenarios.

| Email | Password | Scenario |
|-------|----------|----------|
| healthy@demo.com | demo123 | Healthy budget |
| caution@demo.com | demo123 | Budget warning |
| critical@demo.com | demo123 | Overspent |
| investor@demo.com | demo123 | Active investor |
| unplanned@demo.com | demo123 | High unplanned expenses |

To create demo accounts:
```bash
python scripts/create_demo_accounts.py
```

## Project Structure

```
pblinit/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/routes/          # API endpoints
│   ├── services/            # Business logic
│   └── auth/                # Authentication
├── scripts/
│   ├── init_db.py           # Database initialization
│   └── create_demo_accounts.py  # Demo data generator
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages
│   │   ├── components/      # Reusable components
│   │   ├── contexts/        # React contexts
│   │   └── lib/             # API client
│   └── package.json
├── requirements.txt
└── README.md
```

## AI Alert Types

| Alert | Severity | Trigger |
|-------|----------|---------|
| Budget Exhausted | CRITICAL | Negative remaining budget |
| Budget Running Low | CRITICAL | Less than 20% remaining |
| Budget Caution | WARNING | 50-80% budget used |
| High Unplanned Expenses | WARNING | Unplanned > 30% of total |
| Investment Suggestion | INFO | Leftover budget near month-end |
| Withdrawal Suggestion | WARNING | Negative budget with investments |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register new user |
| POST | /auth/login | Login |
| GET | /students/me/budget-status | Get budget status |
| POST | /expenses/daily-checklist | Submit daily expenses |
| GET | /ai/alerts | Get AI alerts |
| POST | /ai/evaluate | Trigger AI evaluation |
| POST | /chatbot/ask | Ask chatbot |
| GET | /investments/me | Get investment info |
| GET | /investments/me/market-news | Get live market news |

## License

MIT License
