import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Checkbox,
  FormGroup,
  Chip,
  Card,
  CardContent,
  Alert,
  Divider,
} from '@mui/material';
import {
  Microsoft,
  ChatBubble,
  TableChart,
  GitHub,
  AssignmentTurnedIn,
  CheckCircle,
} from '@mui/icons-material';

interface Service {
  id: string;
  name: string;
  icon: JSX.Element;
  description: string;
  category: 'communication' | 'project' | 'attendance' | 'auth';
  oauthRequired: boolean;
  mandatory?: boolean; // Marks if service is required
}

interface IntegrationSelectorProps {
  open: boolean;
  onClose: () => void;
  onComplete: (selectedServices: string[]) => void;
  userRole: 'member' | 'supervisor';
}

const AVAILABLE_SERVICES: Service[] = [
  {
    id: 'microsoft365',
    name: 'Microsoft 365',
    icon: <Microsoft sx={{ fontSize: 40, color: '#0078D4' }} />,
    description: 'Email, Teams, Calendar - Communication and collaboration',
    category: 'communication',
    oauthRequired: true,
  },
  {
    id: 'slack',
    name: 'Slack',
    icon: <ChatBubble sx={{ fontSize: 40, color: '#4A154B' }} />,
    description: 'Team messaging and communication',
    category: 'communication',
    oauthRequired: true,
  },
  {
    id: 'google-sheets',
    name: 'Google Sheets',
    icon: <TableChart sx={{ fontSize: 40, color: '#0F9D58' }} />,
    description: 'Attendance tracking and data storage (Required)',
    category: 'attendance',
    oauthRequired: true,
    mandatory: true,
  },
  {
    id: 'jira',
    name: 'Jira',
    icon: <AssignmentTurnedIn sx={{ fontSize: 40, color: '#0052CC' }} />,
    description: 'Project management and issue tracking',
    category: 'project',
    oauthRequired: true,
  },
  {
    id: 'asana',
    name: 'Asana',
    icon: <CheckCircle sx={{ fontSize: 40, color: '#F06A6A' }} />,
    description: 'Task and project management',
    category: 'project',
    oauthRequired: true,
  },
  {
    id: 'github',
    name: 'GitHub',
    icon: <GitHub sx={{ fontSize: 40, color: '#181717' }} />,
    description: 'Code repository and collaboration',
    category: 'project',
    oauthRequired: true,
  },
  {
    id: 'cloudabis',
    name: 'CloudABIS',
    icon: <CheckCircle sx={{ fontSize: 40, color: '#667eea' }} />,
    description: 'Biometric authentication (one-time login, no OAuth)',
    category: 'auth',
    oauthRequired: false,
  },
];

export const IntegrationSelector = ({
  open,
  onClose,
  onComplete,
}: IntegrationSelectorProps) => {
  // Initialize with Google Sheets as mandatory
  const [selectedServices, setSelectedServices] = useState<string[]>(['google-sheets']);
  const [step, setStep] = useState<'selection' | 'confirmation'>('selection');

  const handleToggleService = (serviceId: string) => {
    // Prevent deselection of mandatory services
    const service = AVAILABLE_SERVICES.find(s => s.id === serviceId);
    if (service?.mandatory) {
      return; // Don't allow toggling mandatory services
    }
    
    setSelectedServices((prev) =>
      prev.includes(serviceId)
        ? prev.filter((id) => id !== serviceId)
        : [...prev, serviceId]
    );
  };

  const handleContinue = () => {
    // Google Sheets is mandatory, so there's always at least one service
    setStep('confirmation');
  };

  const handleConfirm = () => {
    // Ensure Google Sheets is always included
    const finalServices = selectedServices.includes('google-sheets') 
      ? selectedServices 
      : ['google-sheets', ...selectedServices];
    onComplete(finalServices);
  };

  const handleBack = () => {
    setStep('selection');
  };

  const handleSkipAll = () => {
    // Even when skipping, Google Sheets is mandatory
    onComplete(['google-sheets']);
  };

  const selectedServicesData = AVAILABLE_SERVICES.filter((s) =>
    selectedServices.includes(s.id)
  );

  const oauthServices = selectedServicesData.filter((s) => s.oauthRequired);
  const nonOauthServices = selectedServicesData.filter((s) => !s.oauthRequired);

  const groupedServices = {
    communication: AVAILABLE_SERVICES.filter((s) => s.category === 'communication'),
    project: AVAILABLE_SERVICES.filter((s) => s.category === 'project'),
    attendance: AVAILABLE_SERVICES.filter((s) => s.category === 'attendance'),
    auth: AVAILABLE_SERVICES.filter((s) => s.category === 'auth'),
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      TransitionProps={{
        timeout: 400,
      }}
      PaperProps={{
        sx: {
          borderRadius: 2,
          maxHeight: '90vh',
          animation: 'slideIn 0.4s ease-out',
        },
      }}
      sx={{
        '@keyframes slideIn': {
          '0%': {
            opacity: 0,
            transform: 'translateY(-30px) scale(0.95)',
          },
          '100%': {
            opacity: 1,
            transform: 'translateY(0) scale(1)',
          },
        },
      }}
    >
      {step === 'selection' ? (
        <>
          <DialogTitle sx={{ pb: 1 }}>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
                Connect Your Work Tools
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                Select the services you use to enable productivity tracking and wellbeing analytics
              </Typography>
            </Box>
          </DialogTitle>

          <DialogContent>
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Why we need access:</strong> We analyze your work patterns (meetings, messages, tasks) 
                to calculate wellbeing scores and detect burnout risks. Your data is encrypted and never shared.
              </Typography>
            </Alert>

            <Alert severity="warning" sx={{ mb: 3 }}>
              <Typography variant="body2">
                <strong>Note:</strong> Google Sheets integration is required for attendance tracking and cannot be disabled.
              </Typography>
            </Alert>

            {/* Communication Tools */}
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, mt: 2 }}>
              📞 Communication Tools
            </Typography>
            <FormGroup>
              {groupedServices.communication.map((service) => (
                <Card
                  key={service.id}
                  sx={{
                    mb: 2,
                    cursor: 'pointer',
                    border: selectedServices.includes(service.id)
                      ? '2px solid #667eea'
                      : '2px solid transparent',
                    transition: 'all 0.2s',
                    '&:hover': {
                      boxShadow: 3,
                    },
                  }}
                  onClick={() => handleToggleService(service.id)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Checkbox
                        checked={selectedServices.includes(service.id)}
                        onChange={(e) => {
                          e.stopPropagation();
                          handleToggleService(service.id);
                        }}
                        onClick={(e) => e.stopPropagation()}
                      />
                      {service.icon}
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          {service.name}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {service.description}
                        </Typography>
                      </Box>
                      {service.oauthRequired && (
                        <Chip label="OAuth" size="small" color="primary" variant="outlined" />
                      )}
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </FormGroup>

            {/* Project Management */}
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, mt: 3 }}>
              📋 Project Management
            </Typography>
            <FormGroup>
              {groupedServices.project.map((service) => (
                <Card
                  key={service.id}
                  sx={{
                    mb: 2,
                    cursor: 'pointer',
                    border: selectedServices.includes(service.id)
                      ? '2px solid #667eea'
                      : '2px solid transparent',
                    transition: 'all 0.2s',
                    '&:hover': {
                      boxShadow: 3,
                    },
                  }}
                  onClick={() => handleToggleService(service.id)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Checkbox
                        checked={selectedServices.includes(service.id)}
                        onChange={(e) => {
                          e.stopPropagation();
                          handleToggleService(service.id);
                        }}
                        onClick={(e) => e.stopPropagation()}
                      />
                      {service.icon}
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          {service.name}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {service.description}
                        </Typography>
                      </Box>
                      {service.oauthRequired && (
                        <Chip label="OAuth" size="small" color="primary" variant="outlined" />
                      )}
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </FormGroup>

            {/* Attendance Tracking */}
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, mt: 3 }}>
              📊 Attendance & Data
            </Typography>
            <FormGroup>
              {groupedServices.attendance.map((service) => (
                <Card
                  key={service.id}
                  sx={{
                    mb: 2,
                    cursor: service.mandatory ? 'not-allowed' : 'pointer',
                    border: selectedServices.includes(service.id)
                      ? '2px solid #667eea'
                      : '2px solid transparent',
                    transition: 'all 0.2s',
                    '&:hover': {
                      boxShadow: service.mandatory ? 1 : 3,
                    },
                    bgcolor: service.mandatory ? '#f5f5f5' : 'background.paper',
                    opacity: service.mandatory ? 0.9 : 1,
                  }}
                  onClick={() => handleToggleService(service.id)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Checkbox
                        checked={selectedServices.includes(service.id)}
                        disabled={service.mandatory}
                        onChange={(e) => {
                          e.stopPropagation();
                          handleToggleService(service.id);
                        }}
                        onClick={(e) => e.stopPropagation()}
                      />
                      {service.icon}
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                            {service.name}
                          </Typography>
                          {service.mandatory && (
                            <Chip 
                              label="Required" 
                              size="small" 
                              color="error" 
                              sx={{ fontWeight: 600 }}
                            />
                          )}
                        </Box>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {service.description}
                        </Typography>
                      </Box>
                      {service.oauthRequired && (
                        <Chip label="OAuth" size="small" color="primary" variant="outlined" />
                      )}
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </FormGroup>

            {/* Authentication */}
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, mt: 3 }}>
              🔐 Authentication
            </Typography>
            <FormGroup>
              {groupedServices.auth.map((service) => (
                <Card
                  key={service.id}
                  sx={{
                    mb: 2,
                    cursor: 'pointer',
                    border: selectedServices.includes(service.id)
                      ? '2px solid #667eea'
                      : '2px solid transparent',
                    transition: 'all 0.2s',
                    '&:hover': {
                      boxShadow: 3,
                    },
                  }}
                  onClick={() => handleToggleService(service.id)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Checkbox
                        checked={selectedServices.includes(service.id)}
                        onChange={(e) => {
                          e.stopPropagation();
                          handleToggleService(service.id);
                        }}
                        onClick={(e) => e.stopPropagation()}
                      />
                      {service.icon}
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          {service.name}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {service.description}
                        </Typography>
                      </Box>
                      {service.oauthRequired ? (
                        <Chip label="OAuth" size="small" color="primary" variant="outlined" />
                      ) : (
                        <Chip label="One-time" size="small" color="success" variant="outlined" />
                      )}
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </FormGroup>
          </DialogContent>

          <Divider />

          <DialogActions sx={{ p: 3 }}>
            <Button onClick={handleSkipAll} color="inherit">
              Skip Optional Services
            </Button>
            <Box sx={{ flex: 1 }} />
            <Typography variant="body2" sx={{ color: 'text.secondary', mr: 2 }}>
              {selectedServices.length} service{selectedServices.length !== 1 ? 's' : ''} selected
            </Typography>
            <Button
              onClick={handleContinue}
              variant="contained"
              sx={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                px: 4,
              }}
            >
              Continue
            </Button>
          </DialogActions>
        </>
      ) : (
        <>
          <DialogTitle>
            <Typography variant="h5" sx={{ fontWeight: 700 }}>
              Confirm Integrations
            </Typography>
          </DialogTitle>

          <DialogContent>
            <Alert severity="warning" sx={{ mb: 3 }}>
              <Typography variant="body2">
                <strong>Next Step:</strong> You will be redirected to authorize access for the selected services. 
                This is secure and you can revoke access anytime from your account settings.
              </Typography>
            </Alert>

            {oauthServices.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                  Services Requiring OAuth Authorization ({oauthServices.length})
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {oauthServices.map((service) => (
                    <Card key={service.id} sx={{ bgcolor: '#f5f5f5' }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          {service.icon}
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                              {service.name}
                            </Typography>
                            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                              {service.description}
                            </Typography>
                          </Box>
                          <Chip label="OAuth Required" size="small" color="primary" />
                        </Box>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              </Box>
            )}

            {nonOauthServices.length > 0 && (
              <Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                  Services Without OAuth ({nonOauthServices.length})
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {nonOauthServices.map((service) => (
                    <Card key={service.id} sx={{ bgcolor: '#e8f5e9' }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          {service.icon}
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                              {service.name}
                            </Typography>
                            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                              {service.description}
                            </Typography>
                          </Box>
                          <Chip label="One-time Setup" size="small" color="success" />
                        </Box>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              </Box>
            )}

            <Box sx={{ mt: 3, p: 2, bgcolor: '#f9f9f9', borderRadius: 1 }}>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                <strong>Privacy Note:</strong> We only access work-related data (meetings, messages, tasks) 
                for analytics purposes. Personal messages and private data are never accessed or stored. 
                All data is encrypted and you can disconnect services anytime.
              </Typography>
            </Box>
          </DialogContent>

          <Divider />

          <DialogActions sx={{ p: 3 }}>
            <Button onClick={handleBack} color="inherit">
              Back
            </Button>
            <Box sx={{ flex: 1 }} />
            <Button
              onClick={handleConfirm}
              variant="contained"
              sx={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                px: 4,
              }}
            >
              Authorize Services
            </Button>
          </DialogActions>
        </>
      )}
    </Dialog>
  );
};
