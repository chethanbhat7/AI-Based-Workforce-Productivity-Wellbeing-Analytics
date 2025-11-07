import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import { AuthProvider, useAuth } from './context/AuthContext'
import { Login } from './pages/Login'
import { SupervisorRegister } from './pages/SupervisorRegister'
import { MemberRegister } from './pages/MemberRegister'
import { SupervisorDashboard } from './pages/SupervisorDashboard'
import { MemberDashboard } from './pages/MemberDashboard'
import { IntegrationSetup } from './pages/IntegrationSetup'
import './App.css'

// Material UI Theme - Enhanced with Gradients and Better Color Psychology
const theme = createTheme({
  palette: {
    primary: {
      main: '#1e5f8c',      // Professional blue
      light: '#2980b9',
      dark: '#16425b',
    },
    secondary: {
      main: '#6c3483',      // Elegant purple
      light: '#8e44ad',
      dark: '#512e5f',
    },
    success: {
      main: '#27ae60',      // Positive green
      light: '#2ecc71',
      dark: '#1e8449',
    },
    warning: {
      main: '#f39c12',      // Attention orange
      light: '#f5b041',
      dark: '#d68910',
    },
    error: {
      main: '#e74c3c',      // Alert red
      light: '#ec7063',
      dark: '#c0392b',
    },
    info: {
      main: '#3498db',      // Informative blue
      light: '#5dade2',
      dark: '#2874a6',
    },
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
    h1: {
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontWeight: 700,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontWeight: 700,
      letterSpacing: '-0.01em',
    },
    h4: {
      fontWeight: 700,
      letterSpacing: '-0.01em',
    },
    h5: {
      fontWeight: 600,
      letterSpacing: '-0.005em',
    },
    h6: {
      fontWeight: 600,
      letterSpacing: '-0.005em',
    },
    subtitle1: {
      fontWeight: 500,
      letterSpacing: '0em',
    },
    subtitle2: {
      fontWeight: 500,
      letterSpacing: '0em',
    },
    body1: {
      fontWeight: 400,
      letterSpacing: '0em',
    },
    body2: {
      fontWeight: 400,
      letterSpacing: '0em',
    },
    button: {
      fontWeight: 600,
      letterSpacing: '0.02em',
      textTransform: 'none',
    },
    caption: {
      fontWeight: 400,
      letterSpacing: '0.01em',
    },
    overline: {
      fontWeight: 600,
      letterSpacing: '0.1em',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        rounded: {
          borderRadius: 12,
        },
      },
    },
  },
})

function AppContent() {
  const { user, loading } = useAuth();

  // Wait for auth context to load user from localStorage
  if (loading) {
    return null;
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register/supervisor" element={<SupervisorRegister />} />
      <Route path="/register/member" element={<MemberRegister />} />
      
      {/* Integration Setup Route */}
      <Route
        path="/integration-setup"
        element={user ? <IntegrationSetup /> : <Navigate to="/login" replace />}
      />
      
      {/* Protected Routes */}
      <Route
        path="/supervisor-dashboard"
        element={user && user.role === 'supervisor' ? <SupervisorDashboard /> : <Navigate to="/login" replace />}
      />
      <Route
        path="/member-dashboard"
        element={user && user.role === 'member' ? <MemberDashboard /> : <Navigate to="/login" replace />}
      />
      
      {/* Legacy Routes - Keep for backwards compatibility */}
      <Route
        path="/dashboard/supervisor"
        element={<Navigate to="/supervisor-dashboard" replace />}
      />
      <Route
        path="/dashboard/member"
        element={<Navigate to="/member-dashboard" replace />}
      />
      
      {/* Home Route - Redirect based on role */}
      <Route
        path="/"
        element={
          user ? (
            user.role === 'supervisor' ? (
              <Navigate to="/supervisor-dashboard" replace />
            ) : (
              <Navigate to="/member-dashboard" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
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
