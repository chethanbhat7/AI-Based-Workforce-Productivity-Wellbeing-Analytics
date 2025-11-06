import React from 'react'
import { AlertCircle, TrendingUp, Users, CheckCircle } from 'lucide-react'
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
      <div className="p-8 flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome to Workforce Wellbeing Analysis</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Employees Monitored"
          value={dashboardData?.employees_monitored || 0}
          icon={<Users className="text-blue-600" />}
          bgColor="bg-blue-50"
        />
        <StatCard
          title="High Risk"
          value={dashboardData?.burnout_risk_high || 0}
          icon={<AlertCircle className="text-red-600" />}
          bgColor="bg-red-50"
        />
        <StatCard
          title="Medium Risk"
          value={dashboardData?.burnout_risk_medium || 0}
          icon={<TrendingUp className="text-yellow-600" />}
          bgColor="bg-yellow-50"
        />
        <StatCard
          title="Wellbeing Score"
          value={dashboardData?.average_wellbeing_score || 0}
          icon={<CheckCircle className="text-green-600" />}
          bgColor="bg-green-50"
          isScore
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <BurnoutChart />
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Recent Alerts</h2>
          <div className="text-gray-600 text-center py-12">
            <p>No critical alerts at the moment</p>
          </div>
        </div>
      </div>
    </div>
  )
}
