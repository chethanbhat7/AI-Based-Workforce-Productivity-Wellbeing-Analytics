import { useEffect, useState } from 'react';
import { Box, Button, Typography, Alert, Paper, CircularProgress, List, ListItem, ListItemText, Chip } from '@mui/material';
import { Email, CheckCircle, Error, Warning } from '@mui/icons-material';
import { collection, query, getDocs, orderBy, limit } from 'firebase/firestore';
import { db } from '../firebase/config';
import { useAuth } from '../context/AuthContext';

/**
 * EMAIL NOTIFICATION TEST COMPONENT
 * 
 * This component helps test:
 * 1. If BurnoutMonitoringService is queuing email notifications
 * 2. View pending/sent/failed email notifications
 * 3. Manually trigger a test monitoring check
 */

interface EmailNotification {
  id: string;
  type: 'burnout_threshold' | 'overtime_alert';
  to_email: string;
  subject: string;
  status: 'pending' | 'sent' | 'failed';
  created_at: string;
  sent_at?: string;
  error?: string;
  member_name?: string;
  burnout_risk?: number;
  overtime_count?: number;
}

export const EmailNotificationTest = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<EmailNotification[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({ pending: 0, sent: 0, failed: 0 });

  const loadNotifications = async () => {
    setLoading(true);
    setError('');

    try {
      const notificationsRef = collection(db, 'email_notifications');
      
      // Get recent notifications (last 50)
      const q = query(
        notificationsRef,
        orderBy('created_at', 'desc'),
        limit(50)
      );

      const querySnapshot = await getDocs(q);
      const notifData: EmailNotification[] = [];
      
      let pendingCount = 0;
      let sentCount = 0;
      let failedCount = 0;

      querySnapshot.forEach((doc) => {
        const data = doc.data() as Omit<EmailNotification, 'id'>;
        notifData.push({
          ...data,
          id: doc.id,
        });

        if (data.status === 'pending') pendingCount++;
        else if (data.status === 'sent') sentCount++;
        else if (data.status === 'failed') failedCount++;
      });

      setNotifications(notifData);
      setStats({ pending: pendingCount, sent: sentCount, failed: failedCount });
    } catch (err: any) {
      setError(`Error loading notifications: ${err.message}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const triggerManualCheck = async () => {
    setError('');
    
    if (!user || user.role !== 'supervisor') {
      setError('Only supervisors can trigger monitoring checks');
      return;
    }

    try {
      // Clear today's monitoring check flag to allow re-run
      const today = new Date().toISOString().split('T')[0];
      const monitoringCheckKey = `burnout_monitoring_${user.id}_${today}`;
      localStorage.removeItem(monitoringCheckKey);

      // Show alert
      alert('Monitoring check flag cleared. Refresh the page to trigger a new monitoring run.');
      
    } catch (err: any) {
      setError(`Error: ${err.message}`);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'sent':
        return <CheckCircle sx={{ color: 'success.main' }} />;
      case 'failed':
        return <Error sx={{ color: 'error.main' }} />;
      case 'pending':
        return <Warning sx={{ color: 'warning.main' }} />;
      default:
        return <Email />;
    }
  };

  const getStatusColor = (status: string): 'success' | 'error' | 'warning' | 'default' => {
    switch (status) {
      case 'sent':
        return 'success';
      case 'failed':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700 }}>
        📧 Email Notification Testing
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Statistics */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Notification Statistics
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Chip 
            label={`Pending: ${stats.pending}`} 
            color="warning" 
            variant="outlined"
            icon={<Warning />}
          />
          <Chip 
            label={`Sent: ${stats.sent}`} 
            color="success" 
            variant="outlined"
            icon={<CheckCircle />}
          />
          <Chip 
            label={`Failed: ${stats.failed}`} 
            color="error" 
            variant="outlined"
            icon={<Error />}
          />
        </Box>
      </Paper>

      {/* Actions */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Test Actions
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button 
            variant="contained" 
            onClick={loadNotifications}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Refresh Notifications'}
          </Button>

          {user?.role === 'supervisor' && (
            <Button 
              variant="outlined" 
              onClick={triggerManualCheck}
              color="warning"
            >
              Clear Today's Monitoring Check
            </Button>
          )}
        </Box>

        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>How to test:</strong><br />
            1. BurnoutMonitoringService runs automatically when a supervisor logs in<br />
            2. It checks once per day for each supervisor<br />
            3. Click "Clear Today's Monitoring Check" to allow a re-run<br />
            4. Refresh this dashboard or reload the page to trigger monitoring<br />
            5. Check the notification queue below to see if emails were queued
          </Typography>
        </Alert>
      </Paper>

      {/* Notification List */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Recent Notifications ({notifications.length})
        </Typography>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : notifications.length === 0 ? (
          <Alert severity="info">
            No notifications found. Trigger the monitoring service to create test notifications.
          </Alert>
        ) : (
          <List>
            {notifications.map((notif) => (
              <ListItem 
                key={notif.id}
                sx={{
                  border: '1px solid #e0e0e0',
                  borderRadius: 1,
                  mb: 1,
                  bgcolor: notif.status === 'failed' ? '#fff3f3' : 'background.paper',
                }}
              >
                <Box sx={{ mr: 2 }}>
                  {getStatusIcon(notif.status)}
                </Box>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {notif.subject}
                      </Typography>
                      <Chip 
                        label={notif.status.toUpperCase()} 
                        size="small" 
                        color={getStatusColor(notif.status)}
                      />
                      <Chip 
                        label={notif.type === 'burnout_threshold' ? 'Burnout Alert' : 'Overtime Alert'}
                        size="small"
                        variant="outlined"
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        To: {notif.to_email}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Created: {new Date(notif.created_at).toLocaleString()}
                        {notif.sent_at && ` | Sent: ${new Date(notif.sent_at).toLocaleString()}`}
                      </Typography>
                      {notif.member_name && (
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                          Member: {notif.member_name}
                          {notif.burnout_risk && ` | Burnout: ${notif.burnout_risk}%`}
                          {notif.overtime_count && ` | Overtime: ${notif.overtime_count}x this week`}
                        </Typography>
                      )}
                      {notif.error && (
                        <Typography variant="caption" color="error.main" sx={{ display: 'block' }}>
                          Error: {notif.error}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        )}
      </Paper>

      {/* Backend Email Processor Info */}
      <Paper sx={{ p: 3, mt: 3, bgcolor: '#f5f5f5' }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          ⚙️ Backend Email Processor
        </Typography>
        <Alert severity="warning">
          <Typography variant="body2">
            <strong>Note:</strong> Notifications are queued in Firestore but need a backend service to actually send them.<br /><br />
            
            <strong>To send emails:</strong><br />
            1. Configure SMTP settings in <code>api/.env</code>:<br />
            &nbsp;&nbsp;&nbsp;- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD<br />
            &nbsp;&nbsp;&nbsp;- FROM_EMAIL (e.g., hr-wellbeing@yourcompany.com)<br />
            2. Run the email processor: <code>python api/process_email_queue.py</code><br />
            3. Or set up a cron job to process emails periodically<br /><br />
            
            <strong>Test the email service:</strong><br />
            Run: <code>python test_email_notifications.py</code>
          </Typography>
        </Alert>
      </Paper>
    </Box>
  );
};
