import { AlertCircle, TrendingUp, Users, CheckCircle } from 'lucide-react';
import StatCard from '../components/StatCard';
import BurnoutChart from '../components/BurnoutChart';

export default function SupervisorView() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-serif font-bold text-primary">Dashboard</h1>
        <p className="text-secondary text-sm mt-1">Team Overview & Analytics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Team Members"
          value={24}
          icon={<Users className="text-primary" size={24} />}
          bgColor="bg-cream-50"
        />
        <StatCard
          title="High Risk"
          value={3}
          icon={<AlertCircle className="text-primary" size={24} />}
          bgColor="bg-cream-50"
        />
        <StatCard
          title="Medium Risk"
          value={5}
          icon={<TrendingUp className="text-primary" size={24} />}
          bgColor="bg-cream-50"
        />
        <StatCard
          title="Wellbeing"
          value={7.8}
          icon={<CheckCircle className="text-primary" size={24} />}
          bgColor="bg-cream-50"
          isScore
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white border border-cream-200 rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-serif font-bold text-primary mb-4">Burnout Trend</h2>
          <BurnoutChart />
        </div>
        <div className="bg-white border border-cream-200 rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-serif font-bold text-primary mb-4">At Risk</h2>
          <div className="space-y-3">
            <div className="p-4 border border-cream-200 rounded-lg hover:bg-cream-50 transition">
              <p className="font-medium text-primary text-sm">John Smith</p>
              <p className="text-xs text-secondary mt-1">High risk • Immediate attention needed</p>
            </div>
            <div className="p-4 border border-cream-200 rounded-lg hover:bg-cream-50 transition">
              <p className="font-medium text-primary text-sm">Sarah Johnson</p>
              <p className="text-xs text-secondary mt-1">Medium risk • Monitor closely</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
