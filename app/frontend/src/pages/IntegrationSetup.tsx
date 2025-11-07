import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, CircularProgress } from '@mui/material';
import { Work } from '@mui/icons-material';
import { IntegrationSelector } from '../components/IntegrationSelector';
import { OAuthFlow } from '../components/OAuthFlow';
import { useAuth } from '../context/AuthContext';
import { doc, updateDoc, getDoc } from 'firebase/firestore';
import { db } from '../firebase/config';

export const IntegrationSetup = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState<'selection' | 'oauth' | 'complete'>('selection');
  const [selectedServices, setSelectedServices] = useState<string[]>([]);
  const [showDialog, setShowDialog] = useState(true);
  const [checking, setChecking] = useState(true);

  const handleComplete = () => {
    // Redirect to appropriate dashboard based on role
    if (user?.role === 'supervisor') {
      navigate('/supervisor-dashboard');
    } else {
      navigate('/member-dashboard');
    }
  };

  useEffect(() => {
    const checkSetupStatus = async () => {
      // Redirect if no user
      if (!user) {
        navigate('/login');
        return;
      }

      try {
        // Check Firestore to see if user has already completed setup
        const userDoc = await getDoc(doc(db, 'users', user.id));
        const userData = userDoc.data();

        if (userData?.integrationsSetupAt) {
          // User already completed setup, redirect to dashboard
          handleComplete();
        } else {
          // Show integration setup dialog
          setChecking(false);
        }
      } catch (error) {
        console.error('Error checking setup status:', error);
        // On error, allow user to proceed with setup
        setChecking(false);
      }
    };

    checkSetupStatus();
  }, [user, navigate]);

  const handleSelectionComplete = async (services: string[]) => {
    setSelectedServices(services);
    setShowDialog(false);

    if (services.length === 0) {
      // User skipped, save and redirect
      await saveIntegrations([]);
      handleComplete();
    } else {
      // Move to OAuth flow
      setStep('oauth');
    }
  };

  const handleOAuthComplete = async () => {
    await saveIntegrations(selectedServices);
    handleComplete();
  };

  const saveIntegrations = async (services: string[]) => {
    if (!user) return;

    try {
      // Save selected integrations to Firestore
      await updateDoc(doc(db, 'users', user.id), {
        integrations: services,
        integrationsSetupAt: new Date().toISOString(),
      });

      // Mark setup as complete in localStorage
      localStorage.setItem(`integrations_setup_${user.id}`, 'true');
    } catch (error) {
      console.error('Error saving integrations:', error);
    }
  };

  if (!user || checking) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: '#fafafa',
        p: 3,
      }}
    >
      {/* Header */}
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Box
          sx={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 80,
            height: 80,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: 3,
            mb: 2,
          }}
        >
          <Work sx={{ color: 'white', fontSize: 48 }} />
        </Box>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Setup Your Integrations
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary', maxWidth: 600 }}>
          Connect your work tools to enable comprehensive productivity tracking and wellbeing analytics
        </Typography>
      </Box>

      {/* Integration Selection Dialog */}
      {step === 'selection' && (
        <IntegrationSelector
          open={showDialog}
          onClose={() => {}} // Prevent closing without selection
          onComplete={handleSelectionComplete}
          userRole={user.role as 'member' | 'supervisor'}
        />
      )}

      {/* OAuth Flow */}
      {step === 'oauth' && (
        <OAuthFlow
          selectedServices={selectedServices}
          userId={user.id}
          onComplete={handleOAuthComplete}
        />
      )}
    </Box>
  );
};
