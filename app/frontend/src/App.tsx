import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline, Box, AppBar, Toolbar, Typography } from '@mui/material'
import { AuthProvider } from './context/AuthContext'
import { useAuth } from './context/AuthContext'
import Navigation from './components/Navigation'
import SupervisorView from './pages/SupervisorView'
import EmployeeView from './pages/EmployeeView'
import Employees from './pages/Employees'
import { Login } from './pages/Login'
import './App.css'

// Material UI Theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
      light: '#f73378',
      dark: '#9a0036',
    },
    success: {
      main: '#4caf50',
    },
    warning: {
      main: '#ff9800',
    },
    error: {
      main: '#f44336',
    },
    info: {
      main: '#2196f3',
    },
    background: {
      default: '#fafafa',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
})

function AppContent() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <Box display="flex" alignItems="center" justifyContent="center" height="100vh" bgcolor="white">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </Box>
    )
  }

  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden', flexDirection: 'column' }}>
      {/* Top Header - Desktop */}
      <AppBar position="static" sx={{ display: { xs: 'none', sm: 'flex' } }}>
        <Toolbar sx={{ bgcolor: 'primary.main' }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
              Analytics Platform
            </Typography>
            <Typography variant="caption" sx={{ lineHeight: 1.2 }}>
              Wellbeing
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>
      
      <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden', mt: { xs: 7, sm: 0 } }}>
        <Navigation />
        <Box component="main" sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <Routes>
            {user.role === 'supervisor' ? (
              <>
                <Route path="/" element={<SupervisorView />} />
                <Route path="/employees" element={<Employees />} />
              </>
            ) : (
              <Route path="/" element={<EmployeeView />} />
            )}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Box>
      </Box>
    </Box>
  )
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </Router>
    </ThemeProvider>
  )
}

export default App
