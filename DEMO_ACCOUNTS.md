# Demo Accounts - Smart Student Expense & Budget System

This document contains login credentials and descriptions for 5 demo accounts that showcase various AI alert conditions and financial scenarios.

---

## Login Credentials

**Password for all accounts:** `demo123`

---

## Account Details

### 1. Healthy Budget Account

| Field | Value |
|-------|-------|
| **Email** | `healthy@demo.com` |
| **Password** | `demo123` |
| **Name** | Rahul Sharma |
| **Monthly Budget** | Rs. 5,000 |

**Description:**
This account demonstrates a student with good spending habits. The user spends within their daily limits and maintains a healthy budget balance throughout the month.

**Expected AI Alerts:**
- INFO: "Consider Investing Leftover Budget" (near month-end)

**Use Case:** Showcases how a well-managed budget appears in the system with minimal warnings.

---

### 2. Budget Caution Account

| Field | Value |
|-------|-------|
| **Email** | `caution@demo.com` |
| **Password** | `demo123` |
| **Name** | Priya Patel |
| **Monthly Budget** | Rs. 4,000 |

**Description:**
This account shows a student who is spending faster than their budget allows. They're not in critical danger yet, but need to be careful for the rest of the month.

**Expected AI Alerts:**
- CRITICAL: "Budget Running Critically Low"
- INFO: "Consider Investing Leftover Budget"

**Use Case:** Demonstrates the warning system when spending pace exceeds budget sustainability.

---

### 3. Budget Critical Account (Overspent)

| Field | Value |
|-------|-------|
| **Email** | `critical@demo.com` |
| **Password** | `demo123` |
| **Name** | Amit Kumar |
| **Monthly Budget** | Rs. 3,000 |
| **Investment Balance** | Rs. 1,000 |

**Description:**
This account shows a student who has exceeded their monthly budget. They have an investment account with funds that could be withdrawn to cover the deficit.

**Expected AI Alerts:**
- CRITICAL: "Budget Exhausted" - Budget exceeded by Rs. 2,000
- WARNING: "Consider Withdrawing from Investment" - Suggests using investment funds

**Use Case:** Demonstrates critical budget alerts and the AI suggestion to withdraw from investments to cover overspending.

---

### 4. Investor Account

| Field | Value |
|-------|-------|
| **Email** | `investor@demo.com` |
| **Password** | `demo123` |
| **Name** | Neha Singh |
| **Monthly Budget** | Rs. 6,000 |
| **Investment Balance** | Rs. 2,500 |
| **Interest Rate** | 4.5% per month |

**Description:**
This account represents a financially savvy student who regularly saves and invests leftover budget. They have a healthy investment portfolio with transaction history showing deposits and interest earned.

**Expected AI Alerts:**
- INFO: "Consider Investing Leftover Budget" (when near month-end with surplus)

**Use Case:** Showcases the investment feature, transaction history, and how the system encourages saving habits.

---

### 5. High Unplanned Expenses Account

| Field | Value |
|-------|-------|
| **Email** | `unplanned@demo.com` |
| **Password** | `demo123` |
| **Name** | Vikram Rao |
| **Monthly Budget** | Rs. 5,000 |

**Description:**
This account demonstrates a student with many unplanned/additional expenses such as:
- Movie & Dinner Out
- Online Shopping (impulse purchases)
- Cafe visits

The AI detects that unplanned expenses represent a high percentage of total spending.

**Expected AI Alerts:**
- CRITICAL: "Budget Running Critically Low"
- WARNING: "High Unplanned Expenses" - Identifies spending pattern issues
- INFO: "Consider Investing Leftover Budget"

**Use Case:** Demonstrates the spending pattern analysis feature that identifies when unplanned expenses are too high.

---

## Quick Reference Table

| # | Email | Password | Budget | Key Alert Type |
|---|-------|----------|--------|----------------|
| 1 | healthy@demo.com | demo123 | Rs. 5,000 | Healthy - No critical alerts |
| 2 | caution@demo.com | demo123 | Rs. 4,000 | Warning - Budget pace |
| 3 | critical@demo.com | demo123 | Rs. 3,000 | Critical - Overspent |
| 4 | investor@demo.com | demo123 | Rs. 6,000 | Healthy - Has investments |
| 5 | unplanned@demo.com | demo123 | Rs. 5,000 | Warning - Unplanned spending |

---

## How to Test

1. **Start the Backend Server:**
   ```bash
   cd pblinit
   python -m uvicorn app.main:app --reload
   ```

2. **Start the Frontend:**
   ```bash
   cd pblinit/frontend
   npm run dev
   ```

3. **Login** with any of the demo accounts above

4. **Navigate to:**
   - **Dashboard** - View budget status and daily checklist
   - **Alerts** - See AI-generated recommendations
   - **Chatbot** - Ask questions like "budget summary", "remaining budget", "help"
   - **Investments** - View investment portfolio (accounts 3 & 4)

---

## Regenerating Demo Accounts

If you need to reset the demo accounts to their original state:

```bash
cd pblinit
python scripts/create_demo_accounts.py
```

This will delete existing demo accounts and recreate them with fresh data.

---

## AI Alert Types Demonstrated

| Alert Type | Severity | Trigger Condition |
|------------|----------|-------------------|
| Budget Exhausted | CRITICAL | Remaining budget is negative |
| Budget Running Critically Low | CRITICAL | Less than 20% budget remaining |
| Budget Caution | WARNING | 50-80% budget used |
| Low Daily Allowance | WARNING | Daily allowance below 30% of normal |
| Consider Investing | INFO | Leftover budget near month-end |
| Consider Withdrawing | WARNING | Negative budget with investment balance |
| High Unplanned Expenses | WARNING | Unplanned expenses > 30% of total |
