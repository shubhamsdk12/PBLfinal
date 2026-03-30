import { useState, useEffect } from 'react'
import { format } from 'date-fns'
import { api, ExpenseCategory, BudgetSetupItem } from '../lib/api'
import { Calendar, X, Plus, Minus } from 'lucide-react'

interface BudgetSetupModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  isFirstSetup?: boolean
}

export default function BudgetSetupModal({
  isOpen,
  onClose,
  onSuccess,
  isFirstSetup = false,
}: BudgetSetupModalProps) {
  const [, setCategories] = useState<ExpenseCategory[]>([])
  const [categoryBudgets, setCategoryBudgets] = useState<BudgetSetupItem[]>([])
  const [monthlyBudget, setMonthlyBudget] = useState('')
  const [budgetStartDate, setBudgetStartDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [loading, setLoading] = useState(false)
  const [loadingCategories, setLoadingCategories] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      loadCategories()
    }
  }, [isOpen])

  const loadCategories = async () => {
    setLoadingCategories(true)
    try {
      const cats = await api.get<ExpenseCategory[]>('/expenses/categories')
      setCategories(cats)

      // Initialize category budgets with default values
      const defaultBudgets: BudgetSetupItem[] = cats.map((cat) => ({
        category_id: cat.id,
        category_name: cat.name,
        daily_budget: 0,
        is_active: true,
      }))
      setCategoryBudgets(defaultBudgets)
    } catch (err) {
      console.error('Failed to load categories:', err)
      setError('Failed to load categories')
    } finally {
      setLoadingCategories(false)
    }
  }

  const updateCategoryBudget = (categoryId: number, value: number) => {
    setCategoryBudgets((prev) =>
      prev.map((item) =>
        item.category_id === categoryId
          ? { ...item, daily_budget: Math.max(0, value) }
          : item
      )
    )
  }

  const toggleCategoryActive = (categoryId: number) => {
    setCategoryBudgets((prev) =>
      prev.map((item) =>
        item.category_id === categoryId
          ? { ...item, is_active: !item.is_active }
          : item
      )
    )
  }

  // Calculate total daily budget
  const totalDailyBudget = categoryBudgets
    .filter((b) => b.is_active)
    .reduce((sum, b) => sum + b.daily_budget, 0)

  // Calculate estimated monthly (30 days)
  const estimatedMonthly = totalDailyBudget * 30

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    const budget = parseFloat(monthlyBudget)
    if (isNaN(budget) || budget <= 0) {
      setError('Please enter a valid monthly budget amount')
      return
    }

    const activeBudgets = categoryBudgets.filter((b) => b.is_active && b.daily_budget > 0)
    if (activeBudgets.length === 0) {
      setError('Please set at least one category with a daily budget')
      return
    }

    setLoading(true)
    try {
      await api.post('/students/me/budget-setup', {
        monthly_budget: budget,
        budget_start_date: budgetStartDate,
        category_budgets: categoryBudgets.filter((b) => b.is_active),
      })
      onSuccess()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save budget')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-hidden shadow-xl">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {isFirstSetup ? 'Set Up Your Budget' : 'Edit Budget'}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              Set your monthly budget and daily spending limits per category
            </p>
          </div>
          {!isFirstSetup && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        <form onSubmit={handleSubmit} className="overflow-auto max-h-[calc(90vh-180px)]">
          <div className="p-6 space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
                {error}
              </div>
            )}

            {/* Monthly Budget & Start Date */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Monthly Budget (Total)
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span className="text-gray-400">₹</span>
                  </div>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    value={monthlyBudget}
                    onChange={(e) => setMonthlyBudget(e.target.value)}
                    className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="5000"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Budget Start Date
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Calendar className="h-4 w-4 text-gray-400" />
                  </div>
                  <input
                    type="date"
                    value={budgetStartDate}
                    onChange={(e) => setBudgetStartDate(e.target.value)}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Category Daily Budgets */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium text-gray-700">
                  Daily Category Budgets
                </label>
                <div className="text-sm text-gray-500">
                  Total Daily: <span className="font-semibold text-gray-900">₹{totalDailyBudget.toFixed(0)}</span>
                  <span className="text-xs ml-2">(~₹{estimatedMonthly.toFixed(0)}/month)</span>
                </div>
              </div>

              {loadingCategories ? (
                <div className="animate-pulse space-y-2">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="h-12 bg-gray-100 rounded-lg"></div>
                  ))}
                </div>
              ) : (
                <div className="space-y-2">
                  {categoryBudgets.map((item) => (
                    <div
                      key={item.category_id}
                      className={`flex items-center space-x-4 p-3 border rounded-lg transition-colors ${
                        item.is_active
                          ? 'border-gray-200 bg-white'
                          : 'border-gray-100 bg-gray-50 opacity-60'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={item.is_active}
                        onChange={() => toggleCategoryActive(item.category_id)}
                        className="h-5 w-5 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <div className="flex-1">
                        <span className="text-sm font-medium text-gray-900">
                          {item.category_name}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          type="button"
                          onClick={() => updateCategoryBudget(item.category_id, item.daily_budget - 10)}
                          disabled={!item.is_active}
                          className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                        >
                          <Minus className="h-4 w-4" />
                        </button>
                        <div className="relative w-24">
                          <span className="absolute left-2 top-1/2 -translate-y-1/2 text-gray-400 text-sm">₹</span>
                          <input
                            type="number"
                            step="1"
                            min="0"
                            value={item.daily_budget || ''}
                            onChange={(e) =>
                              updateCategoryBudget(item.category_id, parseFloat(e.target.value) || 0)
                            }
                            disabled={!item.is_active}
                            className="w-full pl-6 pr-2 py-1 text-center border border-gray-300 rounded text-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
                            placeholder="0"
                          />
                        </div>
                        <button
                          type="button"
                          onClick={() => updateCategoryBudget(item.category_id, item.daily_budget + 10)}
                          disabled={!item.is_active}
                          className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                        >
                          <Plus className="h-4 w-4" />
                        </button>
                        <span className="text-xs text-gray-400 w-12">/day</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                <strong>How it works:</strong> Each day, you'll see a checklist with these categories.
                At the end of the day, tick the categories where you spent money and enter the amount.
                Unchecked categories mean you saved that amount for the day!
              </p>
            </div>
          </div>

          <div className="p-6 border-t border-gray-200 bg-gray-50">
            <button
              type="submit"
              disabled={loading || loadingCategories}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Saving...' : isFirstSetup ? 'Start Managing My Budget' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
