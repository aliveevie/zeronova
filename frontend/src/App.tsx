import { Routes, Route } from 'react-router-dom'
import { usePrivy } from '@privy-io/react-auth'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Deposit from './pages/Deposit'
import Withdraw from './pages/Withdraw'
import Portfolio from './pages/Portfolio'
import Analytics from './pages/Analytics'

export default function App() {
  const { ready } = usePrivy()

  if (!ready) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse">
          <div className="w-12 h-12 border-2 border-zerova-teal border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    )
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/deposit" element={<Deposit />} />
        <Route path="/withdraw" element={<Withdraw />} />
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Layout>
  )
}
