import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (demoEmail: string, demoPassword: string) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError('');
    setLoading(true);

    try {
      await login(demoEmail, demoPassword);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ backgroundColor: '#fefcf3' }} className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-block mb-4 p-3 rounded-2xl" style={{ backgroundColor: '#8b7355' }}>
            <span className="text-white font-serif text-2xl font-bold">W</span>
          </div>
          <h1 style={{ color: '#8b7355' }} className="text-4xl font-serif font-bold mb-2">Workforce</h1>
          <p style={{ color: '#d4a574' }} className="text-sm tracking-widest uppercase font-medium">Wellbeing Platform</p>
          <div className="w-12 h-1 mx-auto mt-4" style={{ background: 'linear-gradient(to right, #8b7355, #d4a574)' }}></div>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-2xl border p-8 mb-6 shadow-lg" style={{ borderColor: '#fef9e7' }}>
          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label style={{ color: '#8b7355' }} className="block text-sm font-semibold mb-2">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 transition"
                style={{ borderColor: '#fef9e7', backgroundColor: '#fefcf3', color: '#8b7355' }}
                required
                disabled={loading}
              />
            </div>

            <div>
              <label style={{ color: '#8b7355' }} className="block text-sm font-semibold mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 transition"
                style={{ borderColor: '#fef9e7', backgroundColor: '#fefcf3', color: '#8b7355' }}
                required
                disabled={loading}
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full text-white py-2.5 rounded-lg font-semibold transition transform hover:scale-105 disabled:scale-100 mt-6"
              style={{ 
                background: `linear-gradient(to right, #8b7355, #d4a574)`,
              }}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Signing in...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>
        </div>

        {/* Demo Accounts */}
        <div className="space-y-3">
          <p style={{ color: '#8b7355' }} className="text-xs font-bold uppercase tracking-widest text-center">Quick Access</p>
          
          <button
            onClick={() => handleDemoLogin('supervisor@example.com', 'password123')}
            disabled={loading}
            className="w-full p-4 bg-white border-2 rounded-xl hover:shadow-md transition disabled:opacity-50 group"
            style={{ borderColor: '#fef9e7' }}
          >
            <p style={{ color: '#8b7355' }} className="font-semibold text-sm">👥 Supervisor Account</p>
            <p className="text-xs text-gray-500 mt-1">supervisor@example.com</p>
          </button>

          <button
            onClick={() => handleDemoLogin('employee@example.com', 'password123')}
            disabled={loading}
            className="w-full p-4 bg-white border-2 rounded-xl hover:shadow-md transition disabled:opacity-50 group"
            style={{ borderColor: '#fef9e7' }}
          >
            <p style={{ color: '#8b7355' }} className="font-semibold text-sm">👤 Employee Account</p>
            <p className="text-xs text-gray-500 mt-1">employee@example.com</p>
          </button>
        </div>

        {/* Footer */}
        <p style={{ color: '#d4a574' }} className="text-center text-xs mt-8 font-medium">© 2025 Workforce Wellbeing</p>
      </div>
    </div>
  );
};
