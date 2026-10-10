import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'

function ProtectedRoute({ role }) {
  const { token, user } = useAuth()

  if (!token) return <Navigate to="/login" replace />
  if (user && user.role !== role) {
    return <Navigate to={user.role === 1 ? '/recruiter' : '/customer'} replace />
  }

  return <Dashboard />
}

function PublicOnlyRoute({ children }) {
  const { token, user } = useAuth()

  if (token) {
    return <Navigate to={user?.role === 2 ? '/customer' : '/recruiter'} replace />
  }

  return children
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicOnlyRoute>
            <Login />
          </PublicOnlyRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicOnlyRoute>
            <Register />
          </PublicOnlyRoute>
        }
      />
      <Route path="/" element={<Navigate to="/recruiter" replace />} />
      <Route path="/recruiter" element={<ProtectedRoute role={1} />} />
      <Route path="/customer" element={<ProtectedRoute role={2} />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
