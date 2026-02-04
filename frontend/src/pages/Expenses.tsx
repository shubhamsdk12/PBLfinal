import { useEffect, useState } from 'react'
import { api, DailyExpenseTemplate, Expense, DailyChecklistItem } from '../lib/api'
import { format } from 'date-fns'
import { Calendar, Plus, Check, X } from 'lucide-react'

export default function Expenses() {
  const [templates, setTemplates] = useState<DailyExpenseTemplate[]>([])
  const [todayExpenses, setTodayExpenses] = useState<Expense[]>([])
  const [checklistItems, setChecklistItems] = useState<Record<number, DailyChecklistItem>>({})
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [showAdditional, setShowAdditional] = useState(false)
  const [additionalAmount, setAdditionalAmount] = useState('')
  const [additionalCategory, setAdditionalCategory] = useState('')
  const [additionalNotes, setAdditionalNotes] = useState('')

  useEffect(() => {
    loadChecklist()
  }, [selectedDate])

  const loadChecklist = async () => {
    setLoading(true)
    try {
      const data = await api.get<{
        expense_date: string
        templates: DailyExpenseTemplate[]
        today_expenses: Expense[]
      }>(`/expenses/daily-checklist?expense_date=${selectedDate}`)
      
      setTemplates(data.templates)
      setTodayExpenses(data.today_expenses)
      
      // Initialize checklist items from templates
      const items: Record<number, DailyChecklistItem> = {}
      data.templates.forEach((template) => {
        items[template.category_id] = {
          category_id: template.category_id,
          amount: 0,
          is_checked: false,
        }
      })
      setChecklistItems(items)
    } catch (error) {
      console.error('Failed to load checklist:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateChecklistItem = (categoryId: number, field: 'amount' | 'is_checked', value: number | boolean) => {
    setChecklistItems((prev) => ({
      ...prev,
      [categoryId]: {
        ...prev[categoryId],
        [field]: value,
      },
    }))
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const items = Object.values(checklistItems).filter((item) => item.is_checked && item.amount > 0)
      
      const submitData = {
        expense_date: selectedDate,
        items,
        additional_expenses: showAdditional && additionalAmount
          ? [{
              category_id: parseInt(additionalCategory),
              amount: parseFloat(additionalAmount),
              expense_date: selectedDate,
              is_additional: true,
              notes: additionalNotes,
            }]
          : undefined,
      }

      await api.post('/expenses/daily-checklist', submitData)
      
      // Reset form
      setChecklistItems((prev) => {
        const newItems = { ...prev }
        Object.keys(newItems).forEach((key) => {
          newItems[parseInt(key)] = {
            ...newItems[parseInt(key)],
            is_checked: false,
            amount: 0,
          }
        })
        return newItems
      })
      setShowAdditional(false)
      setAdditionalAmount('')
      setAdditionalCategory('')
      setAdditionalNotes('')
      
      // Reload expenses
      await loadChecklist()
    } catch (error) {
      console.error('Failed to submit expenses:', error)
      alert('Failed to submit expenses. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return <div className="animate-pulse">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Daily Expenses</h1>
        <p className="mt-1 text-sm text-gray-500">
          Record your daily expenses using the checklist
        </p>
      </div>

      {/* Date Selector */}
      <div className="bg-white rounded-lg shadow p-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Date
        </label>
        <div className="flex items-center">
          <Calendar className="h-5 w-5 text-gray-400 mr-2" />
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>

      {/* Daily Checklist */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Expense Checklist - {format(new Date(selectedDate), 'MMMM d, yyyy')}
        </h2>

        <div className="space-y-3">
          {templates.map((template) => {
            const item = checklistItems[template.category_id]
            return (
              <div
                key={template.id}
                className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                <input
                  type="checkbox"
                  checked={item?.is_checked || false}
                  onChange={(e) =>
                    updateChecklistItem(template.category_id, 'is_checked', e.target.checked)
                  }
                  className="h-5 w-5 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <div className="flex-1">
                  <label className="text-sm font-medium text-gray-900">
                    {template.category_name}
                  </label>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">$</span>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={item?.amount || ''}
                    onChange={(e) =>
                      updateChecklistItem(
                        template.category_id,
                        'amount',
                        parseFloat(e.target.value) || 0
                      )
                    }
                    disabled={!item?.is_checked}
                    className="w-24 border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                    placeholder="0.00"
                  />
                </div>
              </div>
            )
          })}
        </div>

        {/* Additional Expense */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <button
            onClick={() => setShowAdditional(!showAdditional)}
            className="flex items-center text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Additional Expense
          </button>

          {showAdditional && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={additionalCategory}
                  onChange={(e) => setAdditionalCategory(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">Select category</option>
                  {templates.map((template) => (
                    <option key={template.id} value={template.category_id}>
                      {template.category_name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Amount
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={additionalAmount}
                  onChange={(e) => setAdditionalAmount(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes (optional)
                </label>
                <textarea
                  value={additionalNotes}
                  onChange={(e) => setAdditionalNotes(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  rows={2}
                  placeholder="Add notes..."
                />
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="mt-6">
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Submitting...' : 'Submit Expenses'}
          </button>
        </div>
      </div>

      {/* Today's Expenses */}
      {todayExpenses.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Expenses for {format(new Date(selectedDate), 'MMMM d, yyyy')}
          </h2>
          <div className="space-y-2">
            {todayExpenses.map((expense) => (
              <div
                key={expense.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <p className="font-medium text-gray-900">{expense.category_name}</p>
                  {expense.notes && (
                    <p className="text-sm text-gray-500">{expense.notes}</p>
                  )}
                  {expense.is_additional && (
                    <span className="text-xs text-primary-600">Additional</span>
                  )}
                </div>
                <p className="font-semibold text-gray-900">${expense.amount.toFixed(2)}</p>
              </div>
            ))}
            <div className="pt-2 border-t border-gray-200">
              <div className="flex justify-between font-semibold text-gray-900">
                <span>Total</span>
                <span>
                  ${todayExpenses.reduce((sum, e) => sum + e.amount, 0).toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
