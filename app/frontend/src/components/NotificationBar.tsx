import { 
  Box, 
  IconButton, 
  Badge, 
  Menu, 
  MenuItem,
  Typography, 
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
} from '@mui/material';
import { 
  Notifications, 
  Info, 
  Warning, 
  Error as ErrorIcon,
  CheckCircle,
  Delete,
  VolunteerActivism,
} from '@mui/icons-material';
import { useState, useEffect } from 'react';
import { collection, query, where, getDocs, deleteDoc, doc, updateDoc, addDoc } from 'firebase/firestore';
import { db } from '../firebase/config';
import { useAuth } from '../context/AuthContext';

interface Notification {
  id: string;
  message: string;
  severity: 'error' | 'warning' | 'info' | 'success';
  timestamp: string;
  read: boolean;
  type?: string;
  actionable?: boolean;
  burnoutMemberId?: string;
  burnoutMemberName?: string;
  burnoutMemberEmail?: string;
}

export const NotificationBar = () => {
  const { user } = useAuth();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // Fetch notifications from Firestore
  useEffect(() => {
    const fetchNotifications = async () => {
      if (!user) return;

      try {
        const notificationsRef = collection(db, 'notifications');
        const q = query(notificationsRef, where('userId', '==', user.id));
        const querySnapshot = await getDocs(q);
        
        const fetchedNotifications: Notification[] = [];
        querySnapshot.forEach((docSnap) => {
          const data = docSnap.data();
          fetchedNotifications.push({
            id: docSnap.id,
            message: data.message || '',
            severity: data.severity || 'info',
            timestamp: data.timestamp ? new Date(data.timestamp).toLocaleString() : 'Just now',
            read: data.read || false,
            type: data.type,
            actionable: data.actionable,
            burnoutMemberId: data.burnoutMemberId,
            burnoutMemberName: data.burnoutMemberName,
            burnoutMemberEmail: data.burnoutMemberEmail,
          });
        });
        
        // Sort by timestamp (newest first)
        fetchedNotifications.sort((a, b) => 
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );
        
        setNotifications(fetchedNotifications);
      } catch (error) {
        console.error('Error fetching notifications:', error);
      }
    };

    fetchNotifications();
    
    // Poll for new notifications every 30 seconds
    const interval = setInterval(fetchNotifications, 30000);
    
    return () => clearInterval(interval);
  }, [user]);

  const unreadCount = notifications.filter(n => !n.read).length;

  const handleClick = async (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
    
    // Mark all as read in Firestore
    try {
      const unreadNotifications = notifications.filter(n => !n.read);
      for (const notification of unreadNotifications) {
        await updateDoc(doc(db, 'notifications', notification.id), {
          read: true,
        });
      }
      // Update local state
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    } catch (error) {
      console.error('Error marking notifications as read:', error);
    }
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteDoc(doc(db, 'notifications', id));
      setNotifications(prev => prev.filter(n => n.id !== id));
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  const handleClearAll = async () => {
    try {
      for (const notification of notifications) {
        await deleteDoc(doc(db, 'notifications', notification.id));
      }
      setNotifications([]);
      handleClose();
    } catch (error) {
      console.error('Error clearing notifications:', error);
    }
  };

  const handleVolunteer = async (notification: Notification) => {
    if (!user || !notification.burnoutMemberId) return;

    try {
      // Get supervisor info to send notification
      const supervisorsRef = collection(db, 'users');
      const supervisorQuery = query(
        supervisorsRef,
        where('role', '==', 'supervisor'),
        where('teamNumber', '==', (user as any).teamNumber || '1')
      );
      
      const supervisorSnapshot = await getDocs(supervisorQuery);
      
      if (!supervisorSnapshot.empty) {
        const supervisorDoc = supervisorSnapshot.docs[0];
        const supervisorId = supervisorDoc.id;
        
        // Create notification for supervisor
        await addDoc(collection(db, 'notifications'), {
          userId: supervisorId,
          message: `${user.name} has volunteered to help ${notification.burnoutMemberName} who is experiencing high stress/burnout.`,
          severity: 'info',
          timestamp: new Date().toISOString(),
          read: false,
          volunteerId: user.id,
          volunteerName: user.name,
          volunteerEmail: user.email,
          burnoutMemberId: notification.burnoutMemberId,
          burnoutMemberName: notification.burnoutMemberName,
          burnoutMemberEmail: notification.burnoutMemberEmail,
          type: 'volunteer_offer',
        });

        // Create notification for the burnt-out member
        await addDoc(collection(db, 'notifications'), {
          userId: notification.burnoutMemberId,
          message: `${user.name} has offered to help you with some tasks. Your supervisor has been notified.`,
          severity: 'success',
          timestamp: new Date().toISOString(),
          read: false,
          volunteerId: user.id,
          volunteerName: user.name,
          type: 'help_offered',
        });

        // Delete the original burnout alert notification
        await deleteDoc(doc(db, 'notifications', notification.id));
        setNotifications(prev => prev.filter(n => n.id !== notification.id));
      }
    } catch (error) {
      console.error('Error volunteering:', error);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'error':
        return <ErrorIcon sx={{ color: '#a93226', fontSize: 20 }} />;
      case 'warning':
        return <Warning sx={{ color: '#c77c11', fontSize: 20 }} />;
      case 'success':
        return <CheckCircle sx={{ color: '#1e7e45', fontSize: 20 }} />;
      default:
        return <Info sx={{ color: '#1e5f8c', fontSize: 20 }} />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error':
        return '#a93226';
      case 'warning':
        return '#c77c11';
      case 'success':
        return '#1e7e45';
      default:
        return '#1e5f8c';
    }
  };

  return (
    <>
      <IconButton
        onClick={handleClick}
        sx={{
          color: 'white',
          '&:hover': {
            bgcolor: 'rgba(255, 255, 255, 0.1)',
          },
        }}
      >
        <Badge badgeContent={unreadCount} color="error">
          <Notifications />
        </Badge>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        TransitionProps={{
          timeout: 300,
        }}
        PaperProps={{
          sx: {
            width: 400,
            maxHeight: 500,
            mt: 1,
            animation: 'fadeSlideIn 0.3s ease-out',
            '@keyframes fadeSlideIn': {
              '0%': {
                opacity: 0,
                transform: 'translateY(-10px)',
              },
              '100%': {
                opacity: 1,
                transform: 'translateY(0)',
              },
            },
          },
        }}
      >
        <Box sx={{ px: 2, py: 1.5, borderBottom: '1px solid #ecf0f1' }}>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            Notifications
          </Typography>
          <Typography variant="caption" sx={{ color: '#7f8c8d' }}>
            {notifications.length === 0 
              ? 'No notifications' 
              : `${notifications.length} notification${notifications.length > 1 ? 's' : ''}`}
          </Typography>
        </Box>

        {notifications.length === 0 ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Notifications sx={{ fontSize: 48, color: '#bdc3c7', mb: 1 }} />
            <Typography variant="body2" sx={{ color: '#7f8c8d' }}>
              No notifications yet
            </Typography>
          </Box>
        ) : (
          <List sx={{ p: 0, maxHeight: 400, overflow: 'auto' }}>
            {notifications.map((notification, index) => (
              <Box key={notification.id}>
                <ListItem
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'flex-start',
                    gap: 1,
                    py: 2,
                    px: 2,
                    bgcolor: notification.read ? 'transparent' : '#f8f9fa',
                    borderLeft: `3px solid ${getSeverityColor(notification.severity)}`,
                    '&:hover': {
                      bgcolor: '#f8f9fa',
                    },
                  }}
                >
                  <Box sx={{ display: 'flex', width: '100%', gap: 1 }}>
                    <ListItemIcon sx={{ minWidth: 'auto', mt: 0.5 }}>
                      {getSeverityIcon(notification.severity)}
                    </ListItemIcon>
                    <ListItemText
                      primary={notification.message}
                      secondary={notification.timestamp}
                      primaryTypographyProps={{
                        variant: 'body2',
                        sx: { fontWeight: notification.read ? 400 : 600 },
                      }}
                      secondaryTypographyProps={{
                        variant: 'caption',
                        sx: { color: '#7f8c8d' },
                      }}
                    />
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(notification.id)}
                      sx={{
                        color: '#a93226',
                        '&:hover': {
                          color: '#a93226',
                          bgcolor: '#a9322615',
                        },
                      }}
                    >
                      <Delete sx={{ fontSize: 18 }} />
                    </IconButton>
                  </Box>
                  
                  {/* Show volunteer button for burnout alerts */}
                  {notification.actionable && notification.type === 'burnout_alert' && (
                    <Button
                      size="small"
                      variant="contained"
                      startIcon={<VolunteerActivism />}
                      onClick={() => handleVolunteer(notification)}
                      sx={{
                        ml: 4,
                        bgcolor: '#1e5f8c',
                        '&:hover': {
                          bgcolor: '#16425b',
                        },
                      }}
                    >
                      Volunteer to Help
                    </Button>
                  )}
                </ListItem>
                {index < notifications.length - 1 && <Divider />}
              </Box>
            ))}
          </List>
        )}

        {notifications.length > 0 && (
          <>
            <Divider />
            <MenuItem
              onClick={handleClearAll}
              sx={{
                justifyContent: 'center',
                color: '#a93226',
                fontWeight: 600,
                py: 1.5,
              }}
            >
              Clear All
            </MenuItem>
          </>
        )}
      </Menu>
    </>
  );
};
