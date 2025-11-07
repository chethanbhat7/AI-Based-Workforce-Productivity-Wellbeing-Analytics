import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { TeamOverview } from '../components/TeamOverview';
import { SupervisorProfile } from '../components/SupervisorProfile';
import { MemberDetail } from '../components/MemberDetail';
import { NotificationBar } from '../components/NotificationBar';
import { BurnoutMonitoringService } from '../components/BurnoutMonitoringService';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  Tabs,
  Tab,
  Card,
  CardContent,
  Button,
} from '@mui/material';
import { Work, Logout, AccountCircle, ArrowBack } from '@mui/icons-material';

export const SupervisorDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [tabValue, setTabValue] = useState(0);
  const [selectedMemberId, setSelectedMemberId] = useState<number | null>(null);
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

  const handleViewAccount = () => {
    setShowAccount(true);
    handleMenuClose();
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) {
    return null;
  }

  // Account Details View
  if (showAccount) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', bgcolor: '#fafafa' }}>
        {/* Header */}
        <AppBar position="static" sx={{ boxShadow: 2, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
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
                Workforce Wellbeing - Supervisor
              </Typography>
            </Box>

            {/* User Avatar */}
            <Avatar
              sx={{
                width: 36,
                height: 36,
                bgcolor: 'rgba(255, 255, 255, 0.2)',
              }}
            >
              {user.name.charAt(0).toUpperCase()}
            </Avatar>
          </Toolbar>
        </AppBar>

        {/* Account Details Content */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
          <Box sx={{ maxWidth: 600, mx: 'auto' }}>
            <Button
              startIcon={<ArrowBack />}
              onClick={() => setShowAccount(false)}
              sx={{ mb: 3 }}
            >
              Back to Dashboard
            </Button>

            <Card sx={{ boxShadow: 3 }}>
              <CardContent sx={{ p: 4 }}>
                <Typography variant="h5" sx={{ fontWeight: 700, mb: 3 }}>
                  Account Details
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  <Box>
                    <Typography variant="caption" sx={{ color: '#7f8c8d', textTransform: 'uppercase' }}>
                      Name
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 600 }}>
                      {user.name}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="caption" sx={{ color: '#7f8c8d', textTransform: 'uppercase' }}>
                      Email
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 600 }}>
                      {user.email}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="caption" sx={{ color: '#7f8c8d', textTransform: 'uppercase' }}>
                      User ID
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 600 }}>
                      {user.id}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="caption" sx={{ color: '#7f8c8d', textTransform: 'uppercase' }}>
                      Role
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 600, textTransform: 'capitalize' }}>
                      {user.role}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="caption" sx={{ color: '#7f8c8d', textTransform: 'uppercase' }}>
                      Team Number
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 600 }}>
                      {(user as any).teamNumber || '1'}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', bgcolor: '#fafafa' }}>
      {/* Burnout Monitoring Service - runs in background */}
      <BurnoutMonitoringService />
      
      {/* Header */}
      <AppBar position="static" sx={{ boxShadow: 2, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
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
              Workforce Wellbeing - Supervisor
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
              <MenuItem onClick={handleViewAccount}>
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
        {selectedMemberId ? (
          <MemberDetail
            memberId={selectedMemberId}
            onBack={() => setSelectedMemberId(null)}
          />
        ) : (
          <>
            {/* Tabs */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'white' }}>
              <Tabs
                value={tabValue}
                onChange={(_, newValue) => setTabValue(newValue)}
                sx={{ px: 3 }}
              >
                <Tab label="My Profile" />
                <Tab label="Team Overview" />
              </Tabs>
            </Box>

            {/* Tab Content */}
            <Box>
              {tabValue === 0 && <SupervisorProfile />}
              {tabValue === 1 && <TeamOverview onViewMember={(id) => setSelectedMemberId(id)} />}
            </Box>
          </>
        )}
      </Box>
    </Box>
  );
};
