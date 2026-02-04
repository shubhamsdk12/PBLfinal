import { useEffect, useState } from 'react'
import { api, Investment, InvestmentSummary, InvestmentTransaction } from '../lib/api'
import { TrendingUp, TrendingDown, Plus, Minus, DollarSign } from 'lucide-react'
import { format } from 'date-fns'

export default function Investments() {
  const [investment, setInvestment] = useState<Investment | null>(null)
  const [summary, setSummary] = useState<InvestmentSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [showDeposit, setShowDeposit] = useState(false)
  const [showWithdraw, setShowWithdraw] = useState(false)
  const [showCreate, setShowCreate] = useState(false)
  const [depositAmount, setDepositAmount] = useState('')
  const [withdrawAmount, setWithdrawAmount] = useState('')
  const [interestRate, setInterestRate] = useState('')
  const [initialBalance, setInitialBalance] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadInvestment()
  }, [])

  const loadInvestment = async () => {
    setLoading(true)
    try {
      const inv = await api.get<Investment>('/investments/me')
      setInvestment(inv)
      const sum = await api.get<InvestmentSummary>('/investments/me/summary')
      setSummary(sum)
    } catch (error: any) {
      if (error.response?.status === 404) {
        setInvestment(null)
      } else {
        console.error('Failed to load investment:', error)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    if (!initialBalance || !interestRate) return
    
    setSubmitting(true)
    try {
      await api.post('/investments/', {
        initial_balance: parseFloat(initialBalance),
        monthly_interest_rate: parseFloat(interestRate),
      })
      setShowCreate(false)
      setInitialBalance('')
      setInterestRate('')
      await loadInvestment()
    } catch (error) {
      console.error('Failed to create investment:', error)
      alert('Failed to create investment account')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeposit = async () => {
    if (!depositAmount || !investment) return
    
    setSubmitting(true)
    try {
      await api.post('/investments/me/deposit', {
        amount: parseFloat(depositAmount),
      })
      setShowDeposit(false)
      setDepositAmount('')
      await loadInvestment()
    } catch (error) {
      console.error('Failed to deposit:', error)
      alert('Failed to deposit funds')
    } finally {
      setSubmitting(false)
    }
  }

  const handleWithdraw = async () => {
    if (!withdrawAmount || !investment) return
    
    setSubmitting(true)
    try {
      await api.post('/investments/me/withdraw', {
        amount: parseFloat(withdrawAmount),
      })
      setShowWithdraw(false)
      setWithdrawAmount('')
      await loadInvestment()
    } catch (error: any) {
      console.error('Failed to withdraw:', error)
      alert(error.response?.data?.detail || 'Failed to withdraw funds')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return <div className="animate-pulse">Loading...</div>
  }

  if (!investment) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Investments</h1>
          <p className="mt-1 text-sm text-gray-500">
            Create an investment account to start earning interest
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Create Investment Account
          </h2>
          
          {!showCreate ? (
            <button
              onClick={() => setShowCreate(true)}
              className="bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700"
            >
              Create Account
            </button>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Initial Balance ($)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={initialBalance}
                  onChange={(e) => setInitialBalance(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Monthly Interest Rate (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="100"
                  value={interestRate}
                  onChange={(e) => setInterestRate(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="5.00"
                />
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={handleCreate}
                  disabled={submitting || !initialBalance || !interestRate}
                  className="bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:opacity-50"
                >
                  {submitting ? 'Creating...' : 'Create'}
                </button>
                <button
                  onClick={() => {
                    setShowCreate(false)
                    setInitialBalance('')
                    setInterestRate('')
                  }}
                  className="bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Investments</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your investments and track interest
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setShowDeposit(true)}
            className="flex items-center bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Deposit
          </button>
          <button
            onClick={() => setShowWithdraw(true)}
            className="flex items-center bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700"
          >
            <Minus className="h-4 w-4 mr-2" />
            Withdraw
          </button>
        </div>
      </div>

      {/* Investment Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <DollarSign className="h-5 w-5 text-gray-400 mr-2" />
            <div>
              <p className="text-sm text-gray-500">Current Balance</p>
              <p className="text-2xl font-bold text-gray-900">
                ${investment.balance.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-green-400 mr-2" />
            <div>
              <p className="text-sm text-gray-500">Interest Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {investment.monthly_interest_rate.toFixed(2)}%
              </p>
            </div>
          </div>
        </div>

        {summary && (
          <>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <TrendingUp className="h-5 w-5 text-blue-400 mr-2" />
                <div>
                  <p className="text-sm text-gray-500">Total Invested</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ${summary.total_invested.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <TrendingUp className="h-5 w-5 text-purple-400 mr-2" />
                <div>
                  <p className="text-sm text-gray-500">Interest Earned</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ${summary.total_interest_earned.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Deposit Modal */}
      {showDeposit && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-semibold mb-4">Deposit Funds</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Amount ($)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={depositAmount}
                  onChange={(e) => setDepositAmount(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="0.00"
                />
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={handleDeposit}
                  disabled={submitting || !depositAmount}
                  className="flex-1 bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:opacity-50"
                >
                  {submitting ? 'Depositing...' : 'Deposit'}
                </button>
                <button
                  onClick={() => {
                    setShowDeposit(false)
                    setDepositAmount('')
                  }}
                  className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Withdraw Modal */}
      {showWithdraw && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-semibold mb-4">Withdraw Funds</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Amount ($)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max={investment.balance}
                  value={withdrawAmount}
                  onChange={(e) => setWithdrawAmount(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="0.00"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Available: ${investment.balance.toFixed(2)}
                </p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={handleWithdraw}
                  disabled={submitting || !withdrawAmount}
                  className="flex-1 bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 disabled:opacity-50"
                >
                  {submitting ? 'Withdrawing...' : 'Withdraw'}
                </button>
                <button
                  onClick={() => {
                    setShowWithdraw(false)
                    setWithdrawAmount('')
                  }}
                  className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Transaction History */}
      {summary && summary.transactions.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Transaction History
          </h2>
          <div className="space-y-2">
            {summary.transactions.map((transaction) => (
              <div
                key={transaction.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <p className="font-medium text-gray-900">
                    {transaction.transaction_type}
                  </p>
                  <p className="text-sm text-gray-500">
                    {format(new Date(transaction.created_at), 'MMM d, yyyy h:mm a')}
                  </p>
                  {transaction.notes && (
                    <p className="text-xs text-gray-400">{transaction.notes}</p>
                  )}
                </div>
                <div className="text-right">
                  <p
                    className={`font-semibold ${
                      transaction.transaction_type === 'WITHDRAW'
                        ? 'text-red-600'
                        : transaction.transaction_type === 'INTEREST'
                        ? 'text-green-600'
                        : 'text-gray-900'
                    }`}
                  >
                    {transaction.transaction_type === 'WITHDRAW' ? '-' : '+'}
                    ${transaction.amount.toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-500">
                    Balance: ${transaction.balance_after.toFixed(2)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
