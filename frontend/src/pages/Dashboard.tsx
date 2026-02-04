import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { api, BudgetStatus } from '../lib/api'
import { TrendingUp, TrendingDown, Calendar, DollarSign, AlertTriangle } from 'lucide-react'
import { format } from 'date-fns'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const { student, refreshStudent } = useAuth()
  const [budgetStatus, setBudgetStatus] = useState<BudgetStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadBudgetStatus()
  }, [student])

  const loadBudgetStatus = async () => {
    try {
      const status = await api.get<BudgetStatus>('/students/me/budget-status')
      setBudgetStatus(status)
    } catch (error) {
      console.error('Failed to load budget status:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="animate-pulse">Loading...</div>
  }

  if (!budgetStatus) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No budget data available</p>
        <Link to="/expenses" className="mt-4 text-primary-600 hover:text-primary-700">
          Set up your budget
        </Link>
      </div>
    )
  }

  const budgetPercentage = budgetStatus.monthly_budget > 0
    ? ((budgetStatus.total_spent / budgetStatus.monthly_budget) * 100).toFixed(1)
    : 0

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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome back, {student?.name || 'Student'}!
        </p>
      </div>

      {/* Budget Status Card */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Budget Status</h2>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getHealthColor(budgetStatus.budget_health)}`}>
            {budgetStatus.budget_health}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center">
              <DollarSign className="h-5 w-5 text-gray-400 mr-2" />
              <div>
                <p className="text-sm text-gray-500">Monthly Budget</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${budgetStatus.monthly_budget.toFixed(2)}
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
                  ${budgetStatus.total_spent.toFixed(2)}
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
                  ${budgetStatus.remaining_budget.toFixed(2)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Budget Usage: {budgetPercentage}%</span>
            <span>{budgetStatus.days_remaining} days remaining</span>
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

        {/* Budget Details */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
          <div>
            <p className="text-sm text-gray-500">Daily Allowance</p>
            <p className="text-lg font-semibold text-gray-900">
              ${budgetStatus.daily_budget_allowance.toFixed(2)}/day
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Budget Cycle</p>
            <p className="text-lg font-semibold text-gray-900">
              {format(new Date(budgetStatus.budget_start_date), 'MMM d')} - {budgetStatus.days_elapsed + budgetStatus.days_remaining} days
            </p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link
          to="/expenses"
          className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center">
            <Receipt className="h-8 w-8 text-primary-600 mr-4" />
            <div>
              <h3 className="font-semibold text-gray-900">Add Expense</h3>
              <p className="text-sm text-gray-500">Record today's expenses</p>
            </div>
          </div>
        </Link>

        <Link
          to="/investments"
          className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-primary-600 mr-4" />
            <div>
              <h3 className="font-semibold text-gray-900">Investments</h3>
              <p className="text-sm text-gray-500">Manage your investments</p>
            </div>
          </div>
        </Link>

        <Link
          to="/alerts"
          className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
        >
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
