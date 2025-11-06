import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Card,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Stack,
} from '@mui/material';
import { Work } from '@mui/icons-material';

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
  if (!/^[a-zA-Z\s\-']+$/.test(name)) {
    return { valid: false, error: 'Name can only contain letters, spaces, hyphens, and apostrophes' };
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

export const MemberRegister = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
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
      const response = await fetch('http://localhost:5000/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name.trim(),
          email: formData.email.trim(),
          password: formData.password,
          role: 'member',
          phone: formData.phone.trim(),
        }),
      });

      let data;
      try {
        data = await response.json();
      } catch (e) {
        throw new Error('Server is not responding. Make sure backend is running on port 5000.');
      }

      if (!response.ok) {
        throw new Error(data.error || 'Registration failed');
      }

      navigate('/login');
    } catch (err: any) {
      setGeneralError(err.message || 'Registration failed. Please try again.');
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
      <Box
        sx={{
          border: '2px solid',
          borderColor: 'primary.main',
          borderRadius: 3,
          p: 4,
          bgcolor: 'background.paper',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
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
                Member Registration
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

            {/* Registration Form Card */}
            <Card sx={{ p: 4, boxShadow: 2 }}>
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
            </Card>
          </Stack>
        </Container>
      </Box>
    </Box>
  );
};
