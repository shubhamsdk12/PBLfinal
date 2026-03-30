/**
 * Authentication context for managing user session with local JWT auth.
 */
import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react'
import { api, Student, AuthResponse } from '../lib/api'

interface AuthContextType {
  student: Student | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, name: string) => Promise<void>
  signOut: () => void
  refreshStudent: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [student, setStudent] = useState<Student | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshStudent = useCallback(async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      setStudent(null)
      setLoading(false)
      return
    }

    try {
      const data = await api.get<Student>('/auth/me')
      setStudent(data)
    } catch (error) {
      console.error('Failed to fetch student data:', error)
      localStorage.removeItem('token')
      setStudent(null)
    } finally {
      setLoading(false)
    }
  }, [])

  // Check for existing token on mount
  useEffect(() => {
    refreshStudent()
  }, [refreshStudent])

  const signIn = async (email: string, password: string) => {
    const data = await api.post<AuthResponse>('/auth/login', { email, password })
    localStorage.setItem('token', data.token)
    setStudent(data.student)
  }

  const signUp = async (email: string, password: string, name: string) => {
    const data = await api.post<AuthResponse>('/auth/register', { email, password, name })
    localStorage.setItem('token', data.token)
    setStudent(data.student)
  }

  const signOut = () => {
    localStorage.removeItem('token')
    setStudent(null)
  }

  return (
    <AuthContext.Provider
      value={{
        student,
        loading,
        signIn,
        signUp,
        signOut,
        refreshStudent,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
