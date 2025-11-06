import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import { AuthProvider, useAuth } from './context/AuthContext'
import { Login } from './pages/Login'
import { SupervisorRegister } from './pages/SupervisorRegister'
import { MemberRegister } from './pages/MemberRegister'
import { SupervisorDashboard } from './pages/SupervisorDashboard'
import { MemberDashboard } from './pages/MemberDashboard'
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
      
      {/* Protected Routes */}
      <Route
        path="/dashboard/supervisor"
        element={user && user.role === 'supervisor' ? <SupervisorDashboard /> : <Navigate to="/login" replace />}
      />
      <Route
        path="/dashboard/member"
        element={user && user.role === 'member' ? <MemberDashboard /> : <Navigate to="/login" replace />}
      />
      
      {/* Home Route - Redirect based on role */}
      <Route
        path="/"
        element={
          user ? (
            user.role === 'supervisor' ? (
              <Navigate to="/dashboard/supervisor" replace />
            ) : (
              <Navigate to="/dashboard/member" replace />
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
