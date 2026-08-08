import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

const ROLE_LABELS = { 1: 'Recruiter', 2: 'Customer' }

export default function Home() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  function handleSignOut() {
    signOut()
    navigate('/login', { replace: true })
  }

  return (
    <div className="home">
      <header className="topbar">
        <span className="brand">ElderCare</span>
        <div className="topbar-right">
          <span className="welcome">
            {user?.full_name} ({ROLE_LABELS[user?.role] ?? 'User'})
          </span>
          <button className="ghost" onClick={handleSignOut}>
            Sign out
          </button>
        </div>
      </header>
      <main className="home-body">
        <h1>Welcome, {user?.full_name}</h1>
        <p>Your dashboard is ready.</p>
      </main>
    </div>
  )
}