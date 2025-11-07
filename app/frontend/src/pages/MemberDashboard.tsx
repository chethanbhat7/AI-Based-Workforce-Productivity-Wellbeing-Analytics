import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { WellbeingProfile } from '../components/WellbeingProfile';
import { NotificationBar } from '../components/NotificationBar';
import { BurnoutNotificationService } from '../components/BurnoutNotificationService';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  Card,
  CardContent,
  Divider,
  Button,
} from '@mui/material';
import { Work, Logout, AccountCircle, ArrowBack, Email, Badge, Person } from '@mui/icons-material';

export const MemberDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [showAccount, setShowAccount] = useState(false);

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!user) {
      navigate('/login');
    }
  }, [user, navigate]);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleAccountClick = () => {
    setShowAccount(true);
    setAnchorEl(null);
  };

  const handleBackToDashboard = () => {
    setShowAccount(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) {
    return null;
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', bgcolor: '#fafafa' }}>
      {/* Background service to check for burnout and create notifications */}
      <BurnoutNotificationService />
      
      {/* Header */}
      <AppBar position="static" sx={{ boxShadow: 2 }}>
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
            <Box
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 40,
                height: 40,
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                borderRadius: 1,
              }}
            >
              <Work sx={{ color: 'white', fontSize: 24 }} />
            </Box>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              Workforce Wellbeing - Member
            </Typography>
          </Box>

          {/* User Menu */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <NotificationBar />
            
            <Avatar
              sx={{
                width: 36,
                height: 36,
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                cursor: 'pointer',
              }}
              onClick={handleMenuOpen}
            >
              {user.name.charAt(0).toUpperCase()}
            </Avatar>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
            >
              <MenuItem onClick={handleAccountClick}>
                <AccountCircle sx={{ mr: 1, fontSize: 20 }} />
                <Typography variant="body2">Account</Typography>
              </MenuItem>
              <MenuItem onClick={handleLogout}>
                <Logout sx={{ mr: 1, fontSize: 20 }} />
                <Typography variant="body2">Logout</Typography>
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {showAccount ? (
          // Account Details View
          <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
            <Button
              startIcon={<ArrowBack />}
              onClick={handleBackToDashboard}
              sx={{ mb: 3 }}
            >
              Back to Dashboard
            </Button>

            <Typography variant="h4" sx={{ fontWeight: 700, mb: 4 }}>
              Account Details
            </Typography>

            {/* Profile Card */}
            <Card sx={{ mb: 3, boxShadow: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, mb: 3 }}>
                  <Avatar
                    sx={{
                      width: 80,
                      height: 80,
                      bgcolor: 'primary.main',
                      fontSize: '2rem',
                      fontWeight: 700,
                    }}
                  >
                    {user.name.charAt(0).toUpperCase()}
                  </Avatar>
                  <Box>
                    <Typography variant="h5" sx={{ fontWeight: 700 }}>
                      {user.name}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                      Member Account
                    </Typography>
                  </Box>
                </Box>

                <Divider sx={{ my: 2 }} />

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Person sx={{ color: 'text.secondary' }} />
                    <Box>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        Full Name
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 600 }}>
                        {user.name}
                      </Typography>
                    </Box>
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Email sx={{ color: 'text.secondary' }} />
                    <Box>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        Email Address
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 600 }}>
                        {user.email}
                      </Typography>
                    </Box>
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Badge sx={{ color: 'text.secondary' }} />
                    <Box>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        User ID
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 600 }}>
                        {user.id}
                      </Typography>
                    </Box>
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <AccountCircle sx={{ color: 'text.secondary' }} />
                    <Box>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        Role
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 600, textTransform: 'capitalize' }}>
                        {user.role}
                      </Typography>
                    </Box>
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Work sx={{ color: 'text.secondary' }} />
                    <Box>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        Team Number
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 600 }}>
                        {(user as any).teamNumber || '1'}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
        ) : (
          <WellbeingProfile />
        )}
      </Box>
    </Box>
  );
};
