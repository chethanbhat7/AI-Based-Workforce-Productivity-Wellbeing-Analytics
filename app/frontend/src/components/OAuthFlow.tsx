import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Button,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  HourglassEmpty,
  Launch,
} from '@mui/icons-material';

interface OAuthFlowProps {
  selectedServices: string[];
  userId: string;
  onComplete: () => void;
}

interface ServiceStatus {
  id: string;
  name: string;
  status: 'pending' | 'authorizing' | 'success' | 'error';
  error?: string;
}

const API_URL = (import.meta as any).env?.VITE_API_URL || 'https://ai-based-workforce-productivity-wel-livid.vercel.app/api';

const SERVICE_OAUTH_URLS: Record<string, string> = {
  'microsoft365': `${API_URL}/auth/microsoft/login`,
  'slack': `${API_URL}/auth/slack/login`,
  'google-sheets': `${API_URL}/auth/google/login`,
  'jira': `${API_URL}/auth/jira/login`,
  'asana': `${API_URL}/auth/asana/login`,
  'github': `${API_URL}/auth/github/login`,
};

const SERVICE_NAMES: Record<string, string> = {
  'microsoft365': 'Microsoft 365',
  'slack': 'Slack',
  'google-sheets': 'Google Sheets',
  'jira': 'Jira',
  'asana': 'Asana',
  'github': 'GitHub',
  'cloudabis': 'CloudABIS',
};

export const OAuthFlow = ({ selectedServices, userId, onComplete }: OAuthFlowProps) => {
  const [serviceStatuses, setServiceStatuses] = useState<ServiceStatus[]>([]);
  const [currentServiceIndex, setCurrentServiceIndex] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    // Initialize service statuses
    const statuses: ServiceStatus[] = selectedServices.map((serviceId) => ({
      id: serviceId,
      name: SERVICE_NAMES[serviceId] || serviceId,
      status: 'pending',
    }));
    setServiceStatuses(statuses);
  }, [selectedServices]);

  useEffect(() => {
    // Auto-start OAuth flow for services that need it
    if (serviceStatuses.length > 0 && currentServiceIndex < serviceStatuses.length) {
      const currentService = serviceStatuses[currentServiceIndex];
      
      // Skip non-OAuth services (like CloudABIS)
      if (currentService.id === 'cloudabis') {
        handleServiceSuccess(currentServiceIndex);
        return;
      }

      // Start OAuth flow automatically
      setTimeout(() => {
        handleAuthorize(currentServiceIndex);
      }, 1000);
    }
  }, [currentServiceIndex, serviceStatuses]);

  const handleAuthorize = (index: number) => {
    const service = serviceStatuses[index];
    
    // Update status to authorizing
    setServiceStatuses((prev) =>
      prev.map((s, i) => (i === index ? { ...s, status: 'authorizing' } : s))
    );

    // Get OAuth URL
    const oauthUrl = SERVICE_OAUTH_URLS[service.id];
    
    if (!oauthUrl) {
      handleServiceError(index, 'OAuth URL not configured');
      return;
    }

    // Open OAuth popup
    const width = 600;
    const height = 700;
    const left = window.screen.width / 2 - width / 2;
    const top = window.screen.height / 2 - height / 2;

    const popup = window.open(
      `${oauthUrl}?user_id=${userId}&state=${service.id}`,
      `oauth_${service.id}`,
      `width=${width},height=${height},left=${left},top=${top}`
    );

    // Listen for OAuth callback
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'oauth_success' && event.data.service === service.id) {
        window.removeEventListener('message', handleMessage);
        handleServiceSuccess(index);
      } else if (event.data.type === 'oauth_error' && event.data.service === service.id) {
        window.removeEventListener('message', handleMessage);
        handleServiceError(index, event.data.error || 'Authorization failed');
      }
    };

    window.addEventListener('message', handleMessage);

    // Check if popup was closed without completing auth
    const checkPopup = setInterval(() => {
      if (popup && popup.closed) {
        clearInterval(checkPopup);
        window.removeEventListener('message', handleMessage);
        
        // Check if status is still authorizing (not completed)
        const currentStatus = serviceStatuses[index].status;
        if (currentStatus === 'authorizing') {
          handleServiceError(index, 'Authorization window was closed');
        }
      }
    }, 500);
  };

  const handleServiceSuccess = (index: number) => {
    setServiceStatuses((prev) =>
      prev.map((s, i) => (i === index ? { ...s, status: 'success' } : s))
    );

    // Move to next service after a short delay
    setTimeout(() => {
      if (index + 1 < serviceStatuses.length) {
        setCurrentServiceIndex(index + 1);
      } else {
        setIsComplete(true);
      }
    }, 1000);
  };

  const handleServiceError = (index: number, error: string) => {
    setServiceStatuses((prev) =>
      prev.map((s, i) => (i === index ? { ...s, status: 'error', error } : s))
    );
  };

  const handleRetry = (index: number) => {
    setServiceStatuses((prev) =>
      prev.map((s, i) => (i === index ? { ...s, status: 'pending', error: undefined } : s))
    );
    setCurrentServiceIndex(index);
  };

  const handleSkip = (index: number) => {
    if (index + 1 < serviceStatuses.length) {
      setCurrentServiceIndex(index + 1);
    } else {
      setIsComplete(true);
    }
  };

  const handleFinish = () => {
    onComplete();
  };

  const completedCount = serviceStatuses.filter((s) => s.status === 'success').length;
  const progress = (completedCount / serviceStatuses.length) * 100;

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
      <Card sx={{ boxShadow: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
            {isComplete ? 'Integration Complete!' : 'Connecting Services'}
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary', mb: 3 }}>
            {isComplete
              ? `Successfully connected ${completedCount} of ${serviceStatuses.length} services`
              : 'Please authorize each service in the popup window'}
          </Typography>

          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{ mb: 3, height: 8, borderRadius: 1 }}
          />

          {isComplete && (
            <Alert severity="success" sx={{ mb: 3 }}>
              <Typography variant="body2">
                Your integrations are ready! You can now track productivity and wellbeing across all connected services.
              </Typography>
            </Alert>
          )}

          <List>
            {serviceStatuses.map((service, index) => (
              <ListItem
                key={service.id}
                sx={{
                  border: '1px solid #e0e0e0',
                  borderRadius: 1,
                  mb: 2,
                  bgcolor: service.status === 'authorizing' ? '#f5f5f5' : 'white',
                }}
              >
                <ListItemIcon>
                  {service.status === 'pending' && <HourglassEmpty sx={{ color: '#9e9e9e' }} />}
                  {service.status === 'authorizing' && <HourglassEmpty sx={{ color: '#2196f3' }} />}
                  {service.status === 'success' && <CheckCircle sx={{ color: '#4caf50' }} />}
                  {service.status === 'error' && <Error sx={{ color: '#f44336' }} />}
                </ListItemIcon>
                <ListItemText
                  primary={service.name}
                  secondary={
                    service.status === 'pending'
                      ? 'Waiting...'
                      : service.status === 'authorizing'
                      ? 'Please authorize in popup window'
                      : service.status === 'success'
                      ? 'Successfully connected'
                      : service.error || 'Failed to connect'
                  }
                />
                {service.status === 'error' && (
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button size="small" onClick={() => handleRetry(index)}>
                      Retry
                    </Button>
                    <Button size="small" color="inherit" onClick={() => handleSkip(index)}>
                      Skip
                    </Button>
                  </Box>
                )}
                {service.status === 'authorizing' && (
                  <Chip label="Authorizing..." size="small" color="primary" />
                )}
              </ListItem>
            ))}
          </List>

          {isComplete && (
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleFinish}
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  px: 5,
                }}
              >
                Go to Dashboard
              </Button>
            </Box>
          )}

          {!isComplete && (
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                {completedCount} of {serviceStatuses.length} completed
              </Typography>
              <Button
                onClick={() => setIsComplete(true)}
                color="inherit"
                size="small"
              >
                Skip Remaining
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      <Box sx={{ mt: 3, textAlign: 'center' }}>
        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
          <Launch sx={{ fontSize: 12, mr: 0.5, verticalAlign: 'middle' }} />
          If popup is blocked, please enable popups for this site
        </Typography>
      </Box>
    </Box>
  );
};
