import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Alert, 
  CircularProgress,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
} from '@mui/material';
import { Work } from '@mui/icons-material';
import { loginWithEmail } from '../firebase/auth';
import { doc, getDoc } from 'firebase/firestore';
import { db } from '../firebase/config';

// ==================== VALIDATION UTILITIES ====================

const validateEmail = (email: string): { valid: boolean; error?: string } => {
  if (!email || email.trim().length === 0) {
    return { valid: false, error: 'Email is required' };
  }
  const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!pattern.test(email)) {
    return { valid: false, error: 'Invalid email format' };
  }
  return { valid: true };
};

const validatePassword = (password: string): { valid: boolean; error?: string } => {
  if (!password || password.trim().length === 0) {
    return { valid: false, error: 'Password is required' };
  }
  return { valid: true };
};

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState('');
  const [loading, setLoading] = useState(false);
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    // Clear error for this field when user starts typing
    if (errors['email']) {
      setErrors(prev => ({
        ...prev,
        email: '',
      }));
    }
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    // Clear error for this field when user starts typing
    if (errors['password']) {
      setErrors(prev => ({
        ...prev,
        password: '',
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    let isValid = true;

    // Validate email
    const emailValidation = validateEmail(email);
    if (!emailValidation.valid) {
      newErrors['email'] = emailValidation.error || '';
      isValid = false;
    }

    // Validate password
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.valid) {
      newErrors['password'] = passwordValidation.error || '';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError('');

    // Validate form before submitting
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // First, authenticate and get the user
      const firebaseUser = await loginWithEmail(email.trim(), password);
      
      // Check if user has already completed integration setup
      const userDoc = await getDoc(doc(db, 'users', firebaseUser.uid));
      const userData = userDoc.data();
      
      // Now complete the login through AuthContext
      await login(email.trim(), password);
      
      // Wait a moment for auth context to update
      setTimeout(() => {
        if (userData?.integrationsSetupAt) {
          // User has already completed setup, go directly to dashboard
          if (userData.role === 'supervisor') {
            navigate('/supervisor-dashboard');
          } else {
            navigate('/member-dashboard');
          }
        } else {
          // First-time login, redirect to integration setup
          navigate('/integration-setup');
        }
      }, 100);
    } catch (err: any) {
      setGeneralError(err.message || 'Login failed.');
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
        background: 'linear-gradient(135deg, #424242 0%, #212121 100%)',
        p: 2,
      }}
    >
      <Box
        sx={{
          border: '2px solid',
          borderColor: 'primary.main',
          borderRadius: 3,
          background: 'linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%)',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
          maxWidth: 1100,
          width: '100%',
          minHeight: 600,
          display: 'flex',
          overflow: 'hidden',
        }}
      >
        {/* Left Side - Branding */}
        <Box
          sx={{
            flex: 1,
            p: 6,
            display: { xs: 'none', md: 'flex' },
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'flex-start',
            background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
            color: 'white',
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 80,
              height: 80,
              bgcolor: 'rgba(255, 255, 255, 0.2)',
              borderRadius: 2,
              mb: 3,
            }}
          >
            <Work sx={{ color: 'white', fontSize: 48 }} />
          </Box>
          <Typography
            variant="h3"
            sx={{
              fontWeight: 700,
              mb: 2,
            }}
          >
            Workforce
          </Typography>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 400,
              opacity: 0.9,
              mb: 4,
            }}
          >
            Wellbeing Analytics Platform
          </Typography>
          <Typography
            variant="body1"
            sx={{
              opacity: 0.8,
              lineHeight: 1.8,
            }}
          >
            Monitor team productivity, track wellbeing metrics, and make data-driven decisions to improve workplace health.
          </Typography>
        </Box>

        {/* Right Side - Login Form */}
        <Box
          sx={{
            flex: 1,
            p: { xs: 4, md: 6 },
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            bgcolor: 'white',
          }}
        >
          {/* Mobile - Show logo on top */}
          <Box sx={{ display: { xs: 'block', md: 'none' }, textAlign: 'center', mb: 4 }}>
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
              variant="h5"
              sx={{
                fontWeight: 700,
                color: 'primary.main',
              }}
            >
              Workforce
            </Typography>
          </Box>

          <Typography
            variant="h4"
            sx={{
              fontWeight: 700,
              mb: 1,
              color: 'text.primary',
            }}
          >
            Sign in
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: 'text.secondary',
              mb: 4,
            }}
          >
            to continue to Workforce Analytics
          </Typography>

          <form onSubmit={handleLogin}>
            <Stack spacing={2.5}>
              <TextField
                label="Email Address"
                type="email"
                value={email}
                onChange={handleEmailChange}
                placeholder="you@example.com"
                fullWidth
                required
                disabled={loading}
                variant="outlined"
                error={!!errors['email']}
                helperText={errors['email']}
              />

              <TextField
                label="Password"
                type="password"
                value={password}
                onChange={handlePasswordChange}
                placeholder="Enter your password"
                fullWidth
                required
                disabled={loading}
                variant="outlined"
                error={!!errors['password']}
                helperText={errors['password']}
              />

              {generalError && (
                <Alert severity="error">{generalError}</Alert>
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

              <Box sx={{ textAlign: 'center', pt: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Don't have an account?{' '}
                  <Button
                    variant="text"
                    size="small"
                    onClick={() => setOpenCreateDialog(true)}
                    disabled={loading}
                    sx={{
                      textTransform: 'none',
                      fontWeight: 600,
                      p: 0,
                      ml: 0.5,
                    }}
                  >
                    Create Account
                  </Button>
                </Typography>
              </Box>
            </Stack>
          </form>
        </Box>
      </Box>

      {/* Create Account Dialog */}
      <Dialog 
        open={openCreateDialog} 
        onClose={() => setOpenCreateDialog(false)}
        maxWidth="sm"
        fullWidth
        TransitionProps={{
          timeout: 400,
        }}
        sx={{
          '& .MuiDialog-paper': {
            borderRadius: 3,
            animation: 'slideIn 0.4s ease-out',
          },
          '@keyframes slideIn': {
            '0%': {
              opacity: 0,
              transform: 'translateY(-30px) scale(0.95)',
            },
            '100%': {
              opacity: 1,
              transform: 'translateY(0) scale(1)',
            },
          },
        }}
      >
        <DialogTitle sx={{ fontWeight: 700, fontSize: '1.5rem', pb: 1 }}>
          Create Account
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 2, py: 2 }}>
            <Typography variant="body1" color="text.secondary">
              Select the type of account you want to create:
            </Typography>
            <Stack spacing={2}>
              <Button
                variant="contained"
                fullWidth
                onClick={() => {
                  setOpenCreateDialog(false);
                  navigate('/register/member');
                }}
                sx={{ py: 1.8, textTransform: 'none', fontSize: '1.1rem', fontWeight: 600 }}
              >
                Member Login
              </Button>
              <Button
                variant="contained"
                fullWidth
                onClick={() => {
                  setOpenCreateDialog(false);
                  navigate('/register/supervisor');
                }}
                sx={{ py: 1.8, textTransform: 'none', fontSize: '1.1rem', fontWeight: 600 }}
              >
                Supervisor Login
              </Button>
            </Stack>
          </Stack>
        </DialogContent>
      </Dialog>
    </Box>
  );
};
