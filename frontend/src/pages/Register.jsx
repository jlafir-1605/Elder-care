import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register } from '../api'
import { useAuth } from '../auth/AuthContext'

const ROLE_RECRUITER = 1
const ROLE_CUSTOMER = 2

export default function Register() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState(ROLE_CUSTOMER)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { signIn } = useAuth()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await register({ full_name: fullName, email, password, role })
      signIn(data)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Create Account</h1>
        <p className="subtitle">Join ElderCare</p>

        {error && <div className="alert error">{error}</div>}

        <label htmlFor="fullName">Full Name</label>
        <input
          id="fullName"
          type="text"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          placeholder="Jane Wright"
          required
        />

        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          required
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="At least 6 characters"
          minLength={6}
          required
        />

        <label>I am a</label>
        <div className="role-row">
          <label className="role-option">
            <input
              type="radio"
              name="role"
              value={ROLE_RECRUITER}
              checked={role === ROLE_RECRUITER}
              onChange={() => setRole(ROLE_RECRUITER)}
            />
            Recruiter
          </label>
          <label className="role-option">
            <input
              type="radio"
              name="role"
              value={ROLE_CUSTOMER}
              checked={role === ROLE_CUSTOMER}
              onChange={() => setRole(ROLE_CUSTOMER)}
            />
            Customer
          </label>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Creating account…' : 'Register'}
        </button>

        <p className="switch">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </form>
    </div>
  )
}