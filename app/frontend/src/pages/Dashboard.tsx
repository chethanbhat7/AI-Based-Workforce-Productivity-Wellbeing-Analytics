import React from 'react'
import { AlertCircle, TrendingUp, Users, CheckCircle, RefreshCw } from 'lucide-react'
import StatCard from '../components/StatCard'
import BurnoutChart from '../components/BurnoutChart'

export default function Dashboard() {
  const [dashboardData, setDashboardData] = React.useState<any>(null)
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await fetch('/api/v1/dashboard')
        const data = await response.json()
        setDashboardData(data)
      } catch (error) {
        console.error('Error fetching dashboard:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [])

  if (loading) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="text-gray-600 text-sm">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto bg-gray-50">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 px-8 py-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-display font-bold text-gradient">Dashboard</h1>
            <p className="text-gray-600 text-sm mt-1">Welcome to Workforce Wellbeing Analysis</p>
          </div>
          <button className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition">
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Employees Monitored"
            value={dashboardData?.employees_monitored || 0}
            icon={<Users className="text-blue-600" size={24} />}
            bgColor="bg-blue-100"
            trend={dashboardData?.employee_trend || 0}
          />
          <StatCard
            title="High Risk"
            value={dashboardData?.burnout_risk_high || 0}
            icon={<AlertCircle className="text-red-600" size={24} />}
            bgColor="bg-red-100"
            trend={dashboardData?.high_risk_trend || 0}
          />
          <StatCard
            title="Medium Risk"
            value={dashboardData?.burnout_risk_medium || 0}
            icon={<TrendingUp className="text-yellow-600" size={24} />}
            bgColor="bg-yellow-100"
            trend={dashboardData?.medium_risk_trend || 0}
          />
          <StatCard
            title="Wellbeing Score"
            value={dashboardData?.average_wellbeing_score || 0}
            icon={<CheckCircle className="text-green-600" size={24} />}
            bgColor="bg-green-100"
            isScore
            trend={dashboardData?.wellbeing_trend || 0}
          />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 card-modern p-6">
            <div className="mb-6">
              <h2 className="text-lg font-display font-bold text-gray-900">Burnout Trend</h2>
              <p className="text-xs text-gray-500 mt-1">Last 30 days analysis</p>
            </div>
            <BurnoutChart />
          </div>
          <div className="card-modern p-6">
            <h2 className="text-lg font-display font-bold text-gray-900 mb-6">Recent Alerts</h2>
            <div className="space-y-4">
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-xs font-medium text-red-900">Critical Alert</p>
                <p className="text-xs text-red-700 mt-1">3 employees at high risk</p>
              </div>
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-xs font-medium text-yellow-900">Warning</p>
                <p className="text-xs text-yellow-700 mt-1">5 employees at medium risk</p>
              </div>
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-xs font-medium text-green-900">Good News</p>
                <p className="text-xs text-green-700 mt-1">16 employees in good shape</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
