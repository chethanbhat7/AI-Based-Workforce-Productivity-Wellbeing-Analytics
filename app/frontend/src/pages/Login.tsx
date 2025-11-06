import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Box, 
  Container, 
  Card, 
  TextField, 
  Button, 
  Typography, 
  Alert, 
  CircularProgress, 
  Paper,
  Stack,
  Divider
} from '@mui/material';
import { Work } from '@mui/icons-material';

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
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        p: 2,
      }}
    >
      <Container maxWidth="xs">
        <Stack spacing={4}>
          {/* Header */}
          <Box sx={{ textAlign: 'center' }}>
            <Box
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 60,
                height: 60,
                bgcolor: 'primary.main',
                borderRadius: 2,
                mb: 2,
              }}
            >
              <Work sx={{ color: 'white', fontSize: 32 }} />
            </Box>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                mb: 1,
                color: 'primary.main',
              }}
            >
              Workforce
            </Typography>
            <Typography
              variant="subtitle2"
              sx={{
                textTransform: 'uppercase',
                letterSpacing: 0.5,
                color: 'text.secondary',
                fontWeight: 600,
              }}
            >
              Wellbeing Analytics Platform
            </Typography>
          </Box>

          {/* Login Form Card */}
          <Card sx={{ p: 4, boxShadow: 2 }}>
            <form onSubmit={handleLogin}>
              <Stack spacing={2.5}>
                <TextField
                  label="Email Address"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  fullWidth
                  required
                  disabled={loading}
                  variant="outlined"
                />

                <TextField
                  label="Password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  fullWidth
                  required
                  disabled={loading}
                  variant="outlined"
                />

                {error && (
                  <Alert severity="error">{error}</Alert>
                )}

                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  fullWidth
                  disabled={loading}
                  sx={{
                    py: 1.5,
                    fontSize: '1rem',
                    fontWeight: 600,
                    textTransform: 'none',
                  }}
                >
                  {loading ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CircularProgress size={20} color="inherit" />
                      Signing in...
                    </Box>
                  ) : (
                    'Sign In'
                  )}
                </Button>
              </Stack>
            </form>
          </Card>

          {/* Divider */}
          <Divider sx={{ my: 1 }}>
            <Typography variant="caption" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
              Quick Access
            </Typography>
          </Divider>

          {/* Demo Accounts */}
          <Stack spacing={2}>
            <Paper
              onClick={() => handleDemoLogin('supervisor@example.com', 'password123')}
              disabled={loading}
              component="button"
              sx={{
                p: 2,
                border: '2px solid',
                borderColor: 'divider',
                background: 'white',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.5 : 1,
                transition: 'all 0.2s',
                '&:hover': {
                  boxShadow: 3,
                  borderColor: 'primary.main',
                  transform: 'translateY(-2px)',
                },
                textAlign: 'left',
              }}
            >
              <Typography sx={{ fontWeight: 600, fontSize: '0.95rem' }}>
                👥 Supervisor Account
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary', mt: 0.5, display: 'block' }}>
                supervisor@example.com
              </Typography>
            </Paper>

            <Paper
              onClick={() => handleDemoLogin('employee@example.com', 'password123')}
              disabled={loading}
              component="button"
              sx={{
                p: 2,
                border: '2px solid',
                borderColor: 'divider',
                background: 'white',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.5 : 1,
                transition: 'all 0.2s',
                '&:hover': {
                  boxShadow: 3,
                  borderColor: 'primary.main',
                  transform: 'translateY(-2px)',
                },
                textAlign: 'left',
              }}
            >
              <Typography sx={{ fontWeight: 600, fontSize: '0.95rem' }}>
                👤 Employee Account
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary', mt: 0.5, display: 'block' }}>
                employee@example.com
              </Typography>
            </Paper>
          </Stack>

          {/* Footer */}
          <Typography
            variant="caption"
            sx={{
              textAlign: 'center',
              color: 'text.secondary',
              fontWeight: 500,
              mt: 2,
            }}
          >
            © 2025 Workforce Wellbeing Analytics
          </Typography>
        </Stack>
      </Container>
    </Box>
  );
};
