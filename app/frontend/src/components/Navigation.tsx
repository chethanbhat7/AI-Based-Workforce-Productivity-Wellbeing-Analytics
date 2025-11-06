import React from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Drawer,
  AppBar,
  Toolbar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  Divider,
  IconButton,
  Avatar,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Close as CloseIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material'
import { useAuth } from '../context/AuthContext'

const DRAWER_WIDTH = 280

export default function Navigation() {
  const [mobileOpen, setMobileOpen] = React.useState(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // Build menu items based on user role
  const getMenuItems = () => {
    const baseItems = [
      { label: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    ]
    
    // Add Employees menu only for supervisors
    if (user?.role === 'supervisor') {
      baseItems.push({ label: 'Team Members', icon: <PeopleIcon />, path: '/employees' })
    }
    
    baseItems.push({ label: 'Settings', icon: <SettingsIcon />, path: '/settings' })
    
    return baseItems
  }

  const menuItems = getMenuItems()

  const drawer = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
          Wellbeing
        </Typography>
        <Typography variant="caption" color="textSecondary">
          Analytics Platform
        </Typography>
      </Box>

      {user && (
        <>
          <Divider />
          <Box sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Avatar sx={{ width: 40, height: 40, bgcolor: 'primary.main' }}>
                {user.name.charAt(0)}
              </Avatar>
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {user.name}
                </Typography>
                <Typography variant="caption" color="textSecondary" sx={{ textTransform: 'capitalize' }}>
                  {user.role}
                </Typography>
              </Box>
            </Box>
          </Box>
          <Divider />
        </>
      )}

      <List sx={{ flex: 1, pt: 2 }}>
        {menuItems.map((item) => (
          <ListItem
            component="button"
            key={item.label}
            onClick={() => {
              navigate(item.path)
              setMobileOpen(false)
            }}
            sx={{
              mb: 1,
              mx: 1,
              borderRadius: 1,
              display: 'flex',
              cursor: 'pointer',
              border: 'none',
              background: 'none',
              padding: '8px 16px',
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40, color: 'primary.main' }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItem>
        ))}
      </List>

      <Divider />
      <Box sx={{ p: 1 }}>
        <ListItem
          component="button"
          onClick={handleLogout}
          sx={{
            borderRadius: 1,
            color: 'error.main',
            display: 'flex',
            cursor: 'pointer',
            border: 'none',
            background: 'none',
            padding: '8px 16px',
            '&:hover': {
              bgcolor: 'error.lighter',
            },
          }}
        >
          <ListItemIcon sx={{ minWidth: 40, color: 'error.main' }}>
            <LogoutIcon />
          </ListItemIcon>
          <ListItemText primary="Logout" />
        </ListItem>
      </Box>
    </Box>
  )

  return (
    <>
      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: DRAWER_WIDTH,
          },
        }}
      >
        {drawer}
      </Drawer>

      {/* Desktop Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: DRAWER_WIDTH,
            border: 'none',
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
          },
        }}
        open
      >
        {drawer}
      </Drawer>

      {/* Mobile AppBar */}
      <AppBar
        position="fixed"
        sx={{
          display: { xs: 'flex', sm: 'none' },
          width: '100%',
          zIndex: (theme) => theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar>
          <IconButton color="inherit" edge="start" onClick={() => setMobileOpen(true)} sx={{ mr: 2 }}>
            {mobileOpen ? <CloseIcon /> : <MenuIcon />}
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Wellbeing Analytics
          </Typography>
        </Toolbar>
      </AppBar>
    </>
  )
}
