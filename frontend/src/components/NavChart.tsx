import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { motion } from 'framer-motion'
import type { NavHistoryPoint } from '@/types'

interface NavChartProps {
  data: NavHistoryPoint[]
  isLoading: boolean
  window: '7d' | '30d' | 'all'
  onWindowChange: (window: '7d' | '30d' | 'all') => void
}

const windows = ['7d', '30d', 'all'] as const

export default function NavChart({ data, isLoading, window, onWindowChange }: NavChartProps) {
  const chartData = data.map((point) => ({
    ...point,
    nav: parseFloat(point.nav_per_share),
    date: new Date(point.timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    }),
  }))

  const minNav = Math.min(...chartData.map((d) => d.nav)) * 0.999
  const maxNav = Math.max(...chartData.map((d) => d.nav)) * 1.001

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="card"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">NAV Performance</h3>
        <div className="flex items-center gap-1 bg-zerova-dark rounded-lg p-1">
          {windows.map((w) => (
            <button
              key={w}
              onClick={() => onWindowChange(w)}
              className={`px-3 py-1 text-sm rounded-md transition-colors ${
                window === w
                  ? 'bg-zerova-card text-zerova-teal'
                  : 'text-zerova-muted hover:text-white'
              }`}
            >
              {w === 'all' ? 'All' : w.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="h-64 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-zerova-teal border-t-transparent rounded-full animate-spin" />
        </div>
      ) : chartData.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-zerova-muted">
          No data available
        </div>
      ) : (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="navGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00E5CC" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#00E5CC" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="date"
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#6B7280', fontSize: 12 }}
                dy={10}
              />
              <YAxis
                domain={[minNav, maxNav]}
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#6B7280', fontSize: 12 }}
                tickFormatter={(v) => `$${v.toFixed(3)}`}
                dx={-10}
                width={70}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#111827',
                  border: '1px solid #1F2937',
                  borderRadius: '8px',
                  fontSize: 14,
                }}
                labelStyle={{ color: '#6B7280' }}
                formatter={(value: number) => [`$${value.toFixed(4)}`, 'NAV/Share']}
              />
              <Area
                type="monotone"
                dataKey="nav"
                stroke="#00E5CC"
                strokeWidth={2}
                fill="url(#navGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </motion.div>
  )
}
