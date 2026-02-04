/**
 * Authentication context for managing user session
 */
import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'
import { api, Student } from '../lib/api'

interface AuthContextType {
  user: User | null
  student: Student | null
  session: Session | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, name: string) => Promise<void>
  signOut: () => Promise<void>
  refreshStudent: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [student, setStudent] = useState<Student | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshStudent = async () => {
    if (!user) {
      setStudent(null)
      return
    }

    try {
      const studentData = await api.get<Student>('/students/me')
      setStudent(studentData)
    } catch (error) {
      console.error('Failed to fetch student data:', error)
      setStudent(null)
    }
  }

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      setSession(session)
      setUser(session?.user ?? null)
      
      if (session?.user) {
        await refreshStudent()
      } else {
        setStudent(null)
      }
      
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  const signIn = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (error) throw error
    
    // Check if student account exists, create if not
    try {
      await api.get<Student>('/students/me')
    } catch (error: any) {
      if (error.response?.status === 404) {
        // Student account doesn't exist, create it
        await api.post<Student>('/students/', {
          supabase_user_id: data.user.id,
          email: data.user.email!,
          name: data.user.email!.split('@')[0],
          monthly_budget: 0,
          budget_start_date: new Date().toISOString().split('T')[0],
        })
      }
    }
    
    await refreshStudent()
  }

  const signUp = async (email: string, password: string, name: string) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    })
    if (error) throw error

    // Create student account
    await api.post<Student>('/students/', {
      supabase_user_id: data.user!.id,
      email: data.user!.email!,
      name,
      monthly_budget: 0,
      budget_start_date: new Date().toISOString().split('T')[0],
    })

    await refreshStudent()
  }

  const signOut = async () => {
    await supabase.auth.signOut()
    setStudent(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        student,
        session,
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
