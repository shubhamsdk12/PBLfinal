# API Reference

Complete API endpoint reference for Smart Student Expense & Budget System.

**Base URL**: `http://localhost:8000` (development)

**Authentication**: All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <jwt-token>
```

## Students

### Create Student Account
```http
POST /students/
```
Create a new student account (typically after Supabase Auth registration).

**Request Body**:
```json
{
  "supabase_user_id": "uuid-from-supabase",
  "email": "student@example.com",
  "name": "John Doe",
  "monthly_budget": 1000.00,
  "budget_start_date": "2024-01-01"
}
```

### Get Current Student Info
```http
GET /students/me
```
Get authenticated student's information.

### Update Student Info
```http
PUT /students/me
```
Update student information.

**Request Body**:
```json
{
  "name": "Jane Doe",
  "monthly_budget": 1200.00,
  "budget_start_date": "2024-02-01"
}
```

### Get Budget Status
```http
GET /students/me/budget-status
```
Get comprehensive budget status including health metrics.

**Response**:
```json
{
  "student_id": 1,
  "monthly_budget": 1000.00,
  "remaining_budget": 750.00,
  "total_spent": 250.00,
  "budget_start_date": "2024-01-01",
  "days_elapsed": 10,
  "days_remaining": 21,
  "daily_budget_allowance": 35.71,
  "budget_health": "Healthy"
}
```

### Reset Monthly Budget
```http
POST /students/me/reset-budget
```
Reset budget for new month (creates snapshot of previous month).

## Expenses

### Get Expense Categories
```http
GET /expenses/categories
```
Get all available expense categories.

### Get Daily Checklist
```http
GET /expenses/daily-checklist?expense_date=2024-01-15
```
Get daily expense checklist template and expenses for a specific date.

**Response**:
```json
{
  "expense_date": "2024-01-15",
  "templates": [
    {
      "id": 1,
      "category_id": 1,
      "category_name": "Food",
      "display_order": 0,
      "is_active": true
    }
  ],
  "today_expenses": []
}
```

### Submit Daily Checklist
```http
POST /expenses/daily-checklist
```
Submit daily expense checklist. Only checked items are saved.

**Request Body**:
```json
{
  "expense_date": "2024-01-15",
  "items": [
    {
      "category_id": 1,
      "amount": 25.50,
      "is_checked": true
    },
    {
      "category_id": 2,
      "amount": 10.00,
      "is_checked": false
    }
  ],
  "additional_expenses": [
    {
      "category_id": 8,
      "amount": 15.00,
      "expense_date": "2024-01-15",
      "is_additional": true,
      "notes": "Unexpected expense"
    }
  ]
}
```

### Create Single Expense
```http
POST /expenses/
```
Create a single expense record (for additional/unplanned expenses).

**Request Body**:
```json
{
  "category_id": 1,
  "amount": 25.50,
  "expense_date": "2024-01-15",
  "is_additional": true,
  "notes": "Lunch with friends"
}
```

### Get Expenses
```http
GET /expenses/?start_date=2024-01-01&end_date=2024-01-31
```
Get expenses with optional date filtering.

### Get Today's Expenses
```http
GET /expenses/today?expense_date=2024-01-15
```
Get expenses for a specific date (defaults to today).

## Investments

### Create Investment Account
```http
POST /investments/
```
Create a new investment account.

**Request Body**:
```json
{
  "initial_balance": 500.00,
  "monthly_interest_rate": 5.00
}
```

### Get My Investment
```http
GET /investments/me
```
Get current student's investment account.

### Update Investment
```http
PUT /investments/me
```
Update investment settings (e.g., interest rate).

**Request Body**:
```json
{
  "monthly_interest_rate": 6.00
}
```

### Get Investment Summary
```http
GET /investments/me/summary
```
Get comprehensive investment summary with transaction history.

**Response**:
```json
{
  "investment": {
    "id": 1,
    "student_id": 1,
    "balance": 525.00,
    "monthly_interest_rate": 5.00
  },
  "transactions": [...],
  "total_invested": 500.00,
  "total_interest_earned": 25.00,
  "total_withdrawn": 0.00
}
```

### Deposit to Investment
```http
POST /investments/me/deposit
```
Deposit money into investment account.

**Request Body**:
```json
{
  "amount": 100.00,
  "notes": "Additional deposit"
}
```

### Withdraw from Investment
```http
POST /investments/me/withdraw
```
Withdraw money from investment account.

**Request Body**:
```json
{
  "amount": 50.00,
  "notes": "Emergency withdrawal"
}
```

## AI Alerts

### Evaluate AI Rules
```http
POST /ai/evaluate?current_date=2024-01-15
```
Trigger AI rule evaluation and generate alerts.

**Response**: List of created alerts.

### Get AI Alerts
```http
GET /ai/alerts?is_read=false&is_resolved=false
```
Get AI-generated alerts with optional filtering.

### Get Unread Alerts
```http
GET /ai/alerts/unread
```
Get unread AI alerts.

### Update Alert
```http
PUT /ai/alerts/{alert_id}
```
Update alert status (mark as read/resolved).

**Request Body**:
```json
{
  "is_read": true,
  "is_resolved": false
}
```

### Delete Alert
```http
DELETE /ai/alerts/{alert_id}
```
Delete an AI alert.

## Error Responses

All endpoints may return standard HTTP error codes:

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message description"
}
```

## Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both provide interactive API documentation where you can test endpoints directly.
