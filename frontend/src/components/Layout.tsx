import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { usePrivy } from '@privy-io/react-auth'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  ArrowDownToLine,
  ArrowUpFromLine,
  Briefcase,
  BarChart3,
  Wallet,
  LogOut,
} from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/deposit', label: 'Deposit', icon: ArrowDownToLine },
  { path: '/withdraw', label: 'Withdraw', icon: ArrowUpFromLine },
  { path: '/portfolio', label: 'Portfolio', icon: Briefcase },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { login, logout, authenticated, user } = usePrivy()

  const shortAddress = user?.wallet?.address
    ? `${user.wallet.address.slice(0, 6)}...${user.wallet.address.slice(-4)}`
    : null

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-zerova-border bg-zerova-dark/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-zerova-teal to-emerald-500 flex items-center justify-center">
                <span className="font-bold text-zerova-dark">Z</span>
              </div>
              <span className="text-xl font-semibold">Zerova</span>
            </Link>

            <nav className="hidden md:flex items-center gap-1">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`relative px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'text-zerova-teal'
                        : 'text-zerova-muted hover:text-white'
                    }`}
                  >
                    {isActive && (
                      <motion.div
                        layoutId="nav-indicator"
                        className="absolute inset-0 bg-zerova-teal/10 rounded-lg"
                        transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                      />
                    )}
                    <span className="relative flex items-center gap-2">
                      <item.icon size={16} />
                      {item.label}
                    </span>
                  </Link>
                )
              })}
            </nav>

            <div className="flex items-center gap-3">
              {authenticated ? (
                <div className="flex items-center gap-2">
                  <div className="px-3 py-1.5 bg-zerova-card rounded-lg border border-zerova-border flex items-center gap-2">
                    <Wallet size={14} className="text-zerova-teal" />
                    <span className="text-sm font-mono">{shortAddress}</span>
                  </div>
                  <button
                    onClick={() => logout()}
                    className="p-2 text-zerova-muted hover:text-white transition-colors"
                    title="Disconnect"
                  >
                    <LogOut size={18} />
                  </button>
                </div>
              ) : (
                <button onClick={() => login()} className="btn-primary">
                  Connect Wallet
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {children}
      </main>

      <footer className="border-t border-zerova-border py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-zerova-muted">
              Zerova Protocol — Delta-Neutral Yield on Pacifica
            </p>
            <div className="flex items-center gap-4 text-sm text-zerova-muted">
              <a href="#" className="hover:text-white transition-colors">Docs</a>
              <a href="#" className="hover:text-white transition-colors">Discord</a>
              <a href="#" className="hover:text-white transition-colors">Twitter</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
