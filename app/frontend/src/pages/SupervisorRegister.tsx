import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Stack,
} from '@mui/material';
import { Work } from '@mui/icons-material';
import { registerWithEmail } from '../firebase/auth';
import { doc, setDoc } from 'firebase/firestore';
import { db } from '../firebase/config';

// ==================== VALIDATION UTILITIES ====================

const validateEmail = (email: string): { valid: boolean; error?: string } => {
  const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!pattern.test(email)) {
    return { valid: false, error: 'Invalid email format' };
  }
  return { valid: true };
};

const validatePassword = (password: string): { valid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  if (!password || password.length === 0) {
    errors.push('Password is required');
  }
  
  return { valid: errors.length === 0, errors };
};

const validateName = (name: string): { valid: boolean; error?: string } => {
  if (!name || name.trim().length === 0) {
    return { valid: false, error: 'Name cannot be empty' };
  }
  if (name.length > 120) {
    return { valid: false, error: 'Name cannot exceed 120 characters' };
  }
  // Must start with a letter
  if (!/^[a-zA-Z]/.test(name)) {
    return { valid: false, error: 'Name must start with a letter' };
  }
  // Can't be all numbers
  if (/^\d+$/.test(name.trim())) {
    return { valid: false, error: 'Name cannot be only numbers' };
  }
  // Can contain letters, numbers, spaces, hyphens, and apostrophes
  if (!/^[a-zA-Z][a-zA-Z0-9\s\-']*$/.test(name)) {
    return { valid: false, error: 'Name can only contain letters, numbers, spaces, hyphens, and apostrophes' };
  }
  return { valid: true };
};

const validatePhone = (phone: string): { valid: boolean; error?: string } => {
  if (!phone || phone.trim().length === 0) {
    return { valid: true }; // Optional field
  }
  if (!/^[\d\s\-\+\(\)]{10,}$/.test(phone)) {
    return { valid: false, error: 'Invalid phone number format' };
  }
  if (phone.length > 20) {
    return { valid: false, error: 'Phone number cannot exceed 20 characters' };
  }
  return { valid: true };
};

export const SupervisorRegister = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    teamNumber: '',
    phone: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    let isValid = true;

    // Validate name
    const nameValidation = validateName(formData.name);
    if (!nameValidation.valid) {
      newErrors['name'] = nameValidation.error || '';
      isValid = false;
    }

    // Validate email
    const emailValidation = validateEmail(formData.email);
    if (!emailValidation.valid) {
      newErrors['email'] = emailValidation.error || '';
      isValid = false;
    }

    // Validate password
    const passwordValidation = validatePassword(formData.password);
    if (!passwordValidation.valid) {
      newErrors['password'] = passwordValidation.errors.join(', ');
      isValid = false;
    }

    // Validate password match
    if (formData.password !== formData.confirmPassword) {
      newErrors['confirmPassword'] = 'Passwords do not match';
      isValid = false;
    }

    // Validate phone (optional but if provided, must be valid)
    if (formData.phone) {
      const phoneValidation = validatePhone(formData.phone);
      if (!phoneValidation.valid) {
        newErrors['phone'] = phoneValidation.error || '';
        isValid = false;
      }
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError('');

    // Validate form before submitting
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Register user with Firebase Authentication
      const firebaseUser = await registerWithEmail(
        formData.email.trim(),
        formData.password
      );

      // Store additional user data in Firestore
      await setDoc(doc(db, 'users', firebaseUser.uid), {
        name: formData.name.trim(),
        email: formData.email.trim(),
        role: 'supervisor',
        teamNumber: formData.teamNumber.trim() || '1',
        phone: formData.phone.trim(),
        createdAt: new Date().toISOString(),
        integrationsSetupAt: null, // Will be set after integration setup
      });

      // Registration successful, navigate to integration setup
      navigate('/integration-setup');
    } catch (err: any) {
      // Provide user-friendly error messages
      if (err.message?.includes('auth/email-already-in-use')) {
        setGeneralError('This email is already registered. Please login instead.');
      } else if (err.message?.includes('auth/weak-password')) {
        setGeneralError('Password is too weak. Please use a stronger password.');
      } else if (err.message?.includes('auth/invalid-email')) {
        setGeneralError('Invalid email address format.');
      } else {
        setGeneralError(err.message || 'Registration failed. Please try again.');
      }
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
            Lead your team with data-driven insights. Monitor productivity, track wellbeing, and create a healthier workplace environment.
          </Typography>
        </Box>

        {/* Right Side - Registration Form */}
        <Box
          sx={{
            flex: 1,
            p: { xs: 4, md: 6 },
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            bgcolor: 'white',
            overflowY: 'auto',
          }}
        >
          {/* Mobile - Show logo on top */}
          <Box sx={{ display: { xs: 'block', md: 'none' }, textAlign: 'center', mb: 3 }}>
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
            Supervisor Registration
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: 'text.secondary',
              mb: 3,
            }}
          >
            Create your supervisor account
          </Typography>

          <form onSubmit={handleSubmit}>
            <Stack spacing={2.5}>
                <TextField
                  label="Full Name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Enter your name"
                  fullWidth
                  required
                  disabled={loading}
                  variant="outlined"
                  error={!!errors['name']}
                  helperText={errors['name']}
                />

                <TextField
                  label="Email Address"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="you@example.com"
                  fullWidth
                  required
                  disabled={loading}
                  variant="outlined"
                  error={!!errors['email']}
                  helperText={errors['email']}
                />

                <TextField
                  label="Team Number"
                  name="teamNumber"
                  value={formData.teamNumber}
                  onChange={handleChange}
                  placeholder="e.g., 1, 2, 3, 4"
                  fullWidth
                  disabled={loading}
                  variant="outlined"
                />

                <TextField
                  label="Phone Number"
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="Your phone number"
                  fullWidth
                  disabled={loading}
                  variant="outlined"
                  error={!!errors['phone']}
                  helperText={errors['phone']}
                />

                <TextField
                  label="Password"
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Enter your password"
                  fullWidth
                  required
                  disabled={loading}
                  variant="outlined"
                  error={!!errors['password']}
                  helperText={errors['password']}
                />

                <TextField
                  label="Confirm Password"
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Confirm your password"
                  fullWidth
                  required
                  disabled={loading}
                  variant="outlined"
                  error={!!errors['confirmPassword']}
                  helperText={errors['confirmPassword']}
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
                      Creating Account...
                    </Box>
                  ) : (
                    'Create Account'
                  )}
                </Button>

                <Button
                  variant="text"
                  fullWidth
                  onClick={() => navigate('/login')}
                  disabled={loading}
                  sx={{
                    py: 1.5,
                    fontSize: '1rem',
                    textTransform: 'none',
                  }}
                >
                  Back to Login
                </Button>
              </Stack>
            </form>
          </Box>
        </Box>
      </Box>
    );
  };
