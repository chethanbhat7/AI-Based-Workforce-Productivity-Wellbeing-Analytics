import { CheckCircle, Heart, TrendingDown, Clock } from 'lucide-react';
import StatCard from '../components/StatCard';

export default function EmployeeView() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-serif font-bold text-primary">My Wellbeing</h1>
        <p className="text-secondary text-sm mt-1">Personal Health Dashboard</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <StatCard
          title="Wellbeing Score"
          value={7.5}
          icon={<Heart className="text-primary" size={24} />}
          bgColor="bg-cream-50"
          isScore
        />
        <StatCard
          title="Stress Level"
          value={4.2}
          icon={<TrendingDown className="text-primary" size={24} />}
          bgColor="bg-cream-50"
          isScore
        />
        <StatCard
          title="Work-Life Balance"
          value={6.8}
          icon={<Clock className="text-primary" size={24} />}
          bgColor="bg-cream-50"
          isScore
        />
        <StatCard
          title="Status"
          value="Healthy"
          icon={<CheckCircle className="text-primary" size={24} />}
          bgColor="bg-cream-50"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white border border-cream-200 rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-serif font-bold text-primary mb-4">Feedback</h2>
          <div className="space-y-3">
            <div className="p-3 border border-cream-200 rounded-lg bg-cream-50">
              <p className="text-sm text-primary">Keep maintaining good work-life balance</p>
            </div>
            <div className="p-3 border border-cream-200 rounded-lg bg-cream-50">
              <p className="text-sm text-primary">You're doing great! Continue with healthy habits.</p>
            </div>
          </div>
        </div>

        <div className="bg-white border border-cream-200 rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-serif font-bold text-primary mb-4">Wellness Tips</h2>
          <ul className="space-y-2 text-sm text-primary">
            <li className="flex gap-2">
              <CheckCircle size={16} className="text-primary flex-shrink-0 mt-0.5" />
              Take regular breaks
            </li>
            <li className="flex gap-2">
              <CheckCircle size={16} className="text-primary flex-shrink-0 mt-0.5" />
              Maintain sleep schedule
            </li>
            <li className="flex gap-2">
              <CheckCircle size={16} className="text-primary flex-shrink-0 mt-0.5" />
              Stay hydrated daily
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
