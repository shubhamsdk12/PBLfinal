import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import {
  api,
  BudgetStatus,
  Expense,
  InvestmentSummary,
  DailyChecklistResponse,
  DailyChecklistItem,
  AdditionalExpense,
} from '../lib/api'
import {
  TrendingUp,
  TrendingDown,
  Calendar,
  IndianRupee,
  AlertTriangle,
  Receipt,
  Settings,
  Plus,
} from 'lucide-react'
import { format, subDays, eachDayOfInterval, startOfMonth } from 'date-fns'
import { Link } from 'react-router-dom'
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import BudgetSetupModal from '../components/BudgetSetupModal'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

export default function Dashboard() {
  const { student, refreshStudent } = useAuth()
  const [budgetStatus, setBudgetStatus] = useState<BudgetStatus | null>(null)
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [, setInvestmentSummary] = useState<InvestmentSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [showBudgetModal, setShowBudgetModal] = useState(false)

  // Daily checklist state
  const [checklist, setChecklist] = useState<DailyChecklistResponse | null>(null)
  const [checklistItems, setChecklistItems] = useState<Record<number, DailyChecklistItem>>({})
  const [submittingChecklist, setSubmittingChecklist] = useState(false)

  // Additional expense state
  const [showAddExpense, setShowAddExpense] = useState(false)
  const [additionalCategory, setAdditionalCategory] = useState('')
  const [additionalAmount, setAdditionalAmount] = useState('')
  const [additionalNotes, setAdditionalNotes] = useState('')

  useEffect(() => {
    if (student) {
      loadAllData()
    }
  }, [student])

  useEffect(() => {
    // Show budget setup modal if budget setup is not complete
    if (student && !student.budget_setup_complete) {
      setShowBudgetModal(true)
    }
  }, [student])

  const loadAllData = async () => {
    try {
      const [statusResult, expenseResult, checklistResult] = await Promise.allSettled([
        api.get<BudgetStatus>('/students/me/budget-status'),
        api.get<Expense[]>(
          `/expenses/?start_date=${format(startOfMonth(new Date()), 'yyyy-MM-dd')}&end_date=${format(new Date(), 'yyyy-MM-dd')}`
        ),
        api.get<DailyChecklistResponse>('/expenses/daily-checklist'),
      ])

      if (statusResult.status === 'fulfilled') {
        setBudgetStatus(statusResult.value)
      }

      if (expenseResult.status === 'fulfilled') {
        setExpenses(expenseResult.value)
      }

      if (checklistResult.status === 'fulfilled') {
        const checklistData = checklistResult.value
        setChecklist(checklistData)

        // Initialize checklist items
        const items: Record<number, DailyChecklistItem> = {}
        checklistData.templates.forEach((template) => {
          // Check if expense already exists for today
          const existingExpense = checklistData.today_expenses.find(
            (e) => e.category_id === template.category_id && !e.is_additional
          )
          items[template.category_id] = {
            category_id: template.category_id,
            amount: existingExpense ? existingExpense.amount : template.daily_budget,
            is_checked: !!existingExpense,
          }
        })
        setChecklistItems(items)
      }

      // Try to load investment data
      try {
        const invSummary = await api.get<InvestmentSummary>('/investments/me/summary')
        setInvestmentSummary(invSummary)
      } catch {
        setInvestmentSummary(null)
      }
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleBudgetSuccess = async () => {
    await refreshStudent()
    await loadAllData()
  }

  const updateChecklistItem = (
    categoryId: number,
    field: 'amount' | 'is_checked',
    value: number | boolean
  ) => {
    setChecklistItems((prev) => ({
      ...prev,
      [categoryId]: {
        ...prev[categoryId],
        [field]: value,
      },
    }))
  }

  const handleSubmitChecklist = async () => {
    setSubmittingChecklist(true)
    try {
      const items = Object.values(checklistItems).filter((item) => item.is_checked && item.amount > 0)

      const additionalExpenses: AdditionalExpense[] = []
      if (showAddExpense && additionalCategory && additionalAmount) {
        additionalExpenses.push({
          amount: parseFloat(additionalAmount),
          expense_date: format(new Date(), 'yyyy-MM-dd'),
          custom_category: additionalCategory,
          notes: additionalNotes || undefined,
        })
      }

      await api.post('/expenses/daily-checklist', {
        expense_date: format(new Date(), 'yyyy-MM-dd'),
        items,
        additional_expenses: additionalExpenses.length > 0 ? additionalExpenses : undefined,
      })

      // Reset additional expense form
      setShowAddExpense(false)
      setAdditionalCategory('')
      setAdditionalAmount('')
      setAdditionalNotes('')

      // Reload data
      await loadAllData()
    } catch (error) {
      console.error('Failed to submit checklist:', error)
      alert('Failed to submit expenses. Please try again.')
    } finally {
      setSubmittingChecklist(false)
    }
  }

  // Calculate today's spending
  const todaySpent = checklist?.today_expenses.reduce((sum, e) => sum + e.amount, 0) || 0

  // Prepare chart data
  const getDailySpendingData = () => {
    const last14Days = eachDayOfInterval({
      start: subDays(new Date(), 13),
      end: new Date(),
    })

    return last14Days.map((day) => {
      const dayStr = format(day, 'yyyy-MM-dd')
      const dayExpenses = expenses.filter((e) => e.expense_date === dayStr)
      const total = dayExpenses.reduce((sum, e) => sum + e.amount, 0)
      return {
        date: format(day, 'MMM d'),
        amount: total,
      }
    })
  }

  const getCategoryData = () => {
    const categoryTotals: Record<string, number> = {}
    expenses.forEach((expense) => {
      const category = expense.category_name || expense.custom_category || 'Other'
      categoryTotals[category] = (categoryTotals[category] || 0) + expense.amount
    })

    return Object.entries(categoryTotals).map(([name, value]) => ({
      name,
      value: parseFloat(value.toFixed(2)),
    }))
  }

  // budgetVsSpendingData can be used for a Budget vs Spending bar chart
  // const getBudgetVsSpendingData = () => {
  //   if (!budgetStatus) return []
  //   return [{ name: 'Budget', budget: budgetStatus.monthly_budget, spent: budgetStatus.total_spent }]
  // }

  if (loading) {
    return <div className="animate-pulse">Loading...</div>
  }

  const budgetPercentage =
    budgetStatus && budgetStatus.monthly_budget > 0
      ? ((budgetStatus.total_spent / budgetStatus.monthly_budget) * 100).toFixed(1)
      : '0'

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'Healthy':
        return 'text-green-600 bg-green-50'
      case 'Caution':
        return 'text-yellow-600 bg-yellow-50'
      case 'Critical':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const dailySpendingData = getDailySpendingData()
  const categoryData = getCategoryData()

  return (
    <div className="space-y-6">
      {/* Budget Setup Modal */}
      <BudgetSetupModal
        isOpen={showBudgetModal}
        onClose={() => setShowBudgetModal(false)}
        onSuccess={handleBudgetSuccess}
        isFirstSetup={!student?.budget_setup_complete}
      />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">Welcome back, {student?.name || 'Student'}!</p>
        </div>
        <button
          onClick={() => setShowBudgetModal(true)}
          className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          <Settings className="h-4 w-4 mr-2" />
          Edit Budget
        </button>
      </div>

      {/* Budget Status Cards */}
      {budgetStatus && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Budget Status</h2>
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${getHealthColor(budgetStatus.budget_health)}`}
            >
              {budgetStatus.budget_health}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center">
                <IndianRupee className="h-5 w-5 text-gray-400 mr-2" />
                <div>
                  <p className="text-sm text-gray-500">Monthly Budget</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ₹{budgetStatus.monthly_budget.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center">
                <TrendingDown className="h-5 w-5 text-red-400 mr-2" />
                <div>
                  <p className="text-sm text-gray-500">Total Spent</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ₹{budgetStatus.total_spent.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center">
                <TrendingUp className="h-5 w-5 text-green-400 mr-2" />
                <div>
                  <p className="text-sm text-gray-500">Remaining</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ₹{budgetStatus.remaining_budget.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-blue-400 mr-2" />
                <div>
                  <p className="text-sm text-gray-500">Days Remaining</p>
                  <p className="text-2xl font-bold text-gray-900">{budgetStatus.days_remaining}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Budget Usage: {budgetPercentage}%</span>
              <span>Safe Daily Spend: ₹{budgetStatus.daily_budget_allowance.toFixed(2)}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${
                  budgetStatus.budget_health === 'Critical'
                    ? 'bg-red-500'
                    : budgetStatus.budget_health === 'Caution'
                      ? 'bg-yellow-500'
                      : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(parseFloat(budgetPercentage), 100)}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Daily Expense Checklist */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Today's Expenses</h2>
            <p className="text-sm text-gray-500">
              {format(new Date(), 'EEEE, MMMM d, yyyy')} - Daily Budget: ₹
              {checklist?.total_daily_budget.toFixed(2) || '0.00'}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Today's Spending</p>
            <p className="text-2xl font-bold text-gray-900">₹{todaySpent.toFixed(2)}</p>
          </div>
        </div>

        {/* Checklist Items */}
        <div className="space-y-2 mb-4">
          {checklist?.templates.map((template) => {
            const item = checklistItems[template.category_id]
            const isChecked = item?.is_checked || false
            return (
              <div
                key={template.id}
                className={`flex items-center space-x-4 p-3 border rounded-lg transition-colors ${
                  isChecked ? 'border-primary-200 bg-primary-50' : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={(e) =>
                    updateChecklistItem(template.category_id, 'is_checked', e.target.checked)
                  }
                  className="h-5 w-5 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <div className="flex-1">
                  <label className="text-sm font-medium text-gray-900">{template.category_name}</label>
                  <p className="text-xs text-gray-500">Budget: ₹{template.daily_budget.toFixed(2)}/day</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">₹</span>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    value={item?.amount || ''}
                    onChange={(e) =>
                      updateChecklistItem(template.category_id, 'amount', parseFloat(e.target.value) || 0)
                    }
                    disabled={!isChecked}
                    className="w-24 border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                    placeholder={template.daily_budget.toFixed(0)}
                  />
                </div>
              </div>
            )
          })}
        </div>

        {/* Additional Expense Section */}
        <div className="border-t border-gray-200 pt-4 mt-4">
          <button
            onClick={() => setShowAddExpense(!showAddExpense)}
            className="flex items-center text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Additional Expense
          </button>

          {showAddExpense && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category Name (e.g., "Movie", "Coffee", etc.)
                </label>
                <input
                  type="text"
                  value={additionalCategory}
                  onChange={(e) => setAdditionalCategory(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Enter category name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Amount (₹)</label>
                <input
                  type="number"
                  step="1"
                  min="0"
                  value={additionalAmount}
                  onChange={(e) => setAdditionalAmount(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
                <input
                  type="text"
                  value={additionalNotes}
                  onChange={(e) => setAdditionalNotes(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Add notes..."
                />
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="mt-6">
          <button
            onClick={handleSubmitChecklist}
            disabled={submittingChecklist}
            className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submittingChecklist ? 'Saving...' : "Save Today's Expenses"}
          </button>
        </div>

        {/* Today's Expenses List */}
        {checklist && checklist.today_expenses.length > 0 && (
          <div className="mt-6 pt-4 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Recorded Expenses</h3>
            <div className="space-y-2">
              {checklist.today_expenses.map((expense) => (
                <div key={expense.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div>
                    <span className="text-sm font-medium text-gray-900">
                      {expense.category_name || expense.custom_category}
                    </span>
                    {expense.is_additional && (
                      <span className="ml-2 text-xs text-primary-600">(Additional)</span>
                    )}
                  </div>
                  <span className="text-sm font-semibold text-gray-900">₹{expense.amount.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Spending Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Spending Trend</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={dailySpendingData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip formatter={(value: number) => [`₹${value.toFixed(2)}`, 'Amount']} />
              <Line type="monotone" dataKey="amount" stroke="#6366f1" strokeWidth={2} dot={{ fill: '#6366f1' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Category-wise Spending */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Spending by Category</h3>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => [`₹${value.toFixed(2)}`, 'Amount']} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-gray-500">
              No expense data available
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Link to="/expenses" className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center">
            <Receipt className="h-8 w-8 text-primary-600 mr-4" />
            <div>
              <h3 className="font-semibold text-gray-900">Expenses</h3>
              <p className="text-sm text-gray-500">View all expenses</p>
            </div>
          </div>
        </Link>

        <Link to="/investments" className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-primary-600 mr-4" />
            <div>
              <h3 className="font-semibold text-gray-900">Investments</h3>
              <p className="text-sm text-gray-500">Manage investments</p>
            </div>
          </div>
        </Link>

        <Link to="/history" className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center">
            <Calendar className="h-8 w-8 text-primary-600 mr-4" />
            <div>
              <h3 className="font-semibold text-gray-900">History</h3>
              <p className="text-sm text-gray-500">View expense history</p>
            </div>
          </div>
        </Link>

        <Link to="/alerts" className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center">
            <AlertTriangle className="h-8 w-8 text-primary-600 mr-4" />
            <div>
              <h3 className="font-semibold text-gray-900">AI Alerts</h3>
              <p className="text-sm text-gray-500">View recommendations</p>
            </div>
          </div>
        </Link>
      </div>
    </div>
  )
}
