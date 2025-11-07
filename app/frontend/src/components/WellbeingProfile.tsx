import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Paper,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  VideoCall,
  Chat,
  Assignment,
  AccessTime,
  TrendingUp,
  Speed,
  Login,
  Logout,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { generateConsistentValue, getTestScenarioValues } from '../utils/consistentValues';

interface UserAnalytics {
  taskCompletionRate?: number;
  loggedHours?: number;
  wellbeingScore?: number;
  meetingHours?: number;
  meetingCount?: number;
  messagesSent?: number;
  messagesReceived?: number;
  earlyStarts?: number;
  lateExits?: number;
  lateStarts?: number;
  earlyExits?: number;
  burnoutRisk?: number;
  efficiency?: number;
  stressLevel?: 'low' | 'medium' | 'high';
  trend?: 'up' | 'down' | 'stable';
  lastActive?: string;
}

export const WellbeingProfile = () => {
  const { user } = useAuth();
  
  const email = user?.email || '';
  
  // Check for test scenario values first
  const testScenario = getTestScenarioValues(email);
  
  // Generate consistent dummy values based on email hash (same as TeamOverview)
  const generateValue = (seed: number, min: number, max: number): number => {
    return generateConsistentValue(email, seed, min, max);
  };

  // TODO: Fetch real analytics data from Firestore
  // For now, use consistent dummy values based on email
  const getUserAnalytics = (): UserAnalytics | null => {
    // In the future, this would fetch from Firestore: doc(db, 'analytics', user.id)
    // For now, return null to use dummy values
    return null;
  };
  
  const analytics = getUserAnalytics();
  
  // Use test scenario if available, otherwise real data, otherwise generate consistent dummy values
  const taskCompletionRate = testScenario?.taskCompletionRate ?? analytics?.taskCompletionRate ?? generateValue(1, 60, 100);
  const loggedHours = analytics?.loggedHours ?? generateValue(2, 30, 45);
  const wellbeingScore = testScenario?.wellbeingScore ?? analytics?.wellbeingScore ?? generateValue(3, 50, 90);
  const meetingHours = analytics?.meetingHours ?? generateValue(5, 8, 18);
  const meetingCount = analytics?.meetingCount ?? generateValue(6, 12, 25);
  const messagesSent = analytics?.messagesSent ?? generateValue(7, 150, 300);
  const messagesReceived = analytics?.messagesReceived ?? generateValue(8, 120, 250);
  const earlyStarts = analytics?.earlyStarts ?? generateValue(9, 0, 4);
  const lateExits = analytics?.lateExits ?? generateValue(10, 0, 3);
  const lateStarts = analytics?.lateStarts ?? generateValue(11, 0, 2);
  const earlyExits = analytics?.earlyExits ?? generateValue(12, 0, 1);
  
  // Calculate burnout risk and efficiency based on other metrics
 const burnoutRisk = analytics?.burnoutRisk ?? Math.min(100, Math.max(0, 100 - wellbeingScore + (meetingHours > 15 ? 20 : 0)));

  const efficiency = analytics?.efficiency ?? Math.round((taskCompletionRate + Math.min(100, (loggedHours / 40) * 100)) / 2);

  return (
    <Box sx={{ width: '100%', p: 3 }}>
      {/* Score Cards - Square boxes with circular progress */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr', lg: 'repeat(3, 1fr)' },
          gap: 4,
          mb: 4,
        }}
      >
        {/* Wellbeing Score Card */}
        <Card sx={{ boxShadow: 2, borderRadius: 2, border: '1px solid #e0e0e0' }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
                <CircularProgress
                  variant="determinate"
                  value={100}
                  size={120}
                  thickness={4}
                  sx={{
                    color: '#e0e0e0',
                  }}
                />
                <CircularProgress
                  variant="determinate"
                  value={wellbeingScore}
                  size={120}
                  thickness={4}
                  sx={{
                    color: wellbeingScore >= 80 ? '#4caf50' : wellbeingScore >= 60 ? '#ff9800' : '#f44336',
                    position: 'absolute',
                    left: 0,
                    '& .MuiCircularProgress-circle': {
                      strokeLinecap: 'round',
                    },
                  }}
                />
                <Box
                  sx={{
                    top: 0,
                    left: 0,
                    bottom: 0,
                    right: 0,
                    position: 'absolute',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#2c3e50' }}>
                    {wellbeingScore}
                  </Typography>
                </Box>
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1, textAlign: 'center', color: '#2c3e50' }}>
                Wellbeing Score
              </Typography>
              <Typography variant="body2" sx={{ color: '#7f8c8d', textAlign: 'center' }}>
                Overall wellness based on work-life balance
              </Typography>
            </Box>
          </CardContent>
        </Card>

        {/* Burnout Risk Score Card */}
        <Card sx={{ boxShadow: 2, borderRadius: 2, border: '1px solid #e0e0e0' }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
                <CircularProgress
                  variant="determinate"
                  value={100}
                  size={120}
                  thickness={4}
                  sx={{
                    color: '#e0e0e0',
                  }}
                />
                <CircularProgress
                  variant="determinate"
                  value={burnoutRisk}
                  size={120}
                  thickness={4}
                  sx={{
                    color: burnoutRisk > 70 ? '#f44336' : burnoutRisk > 40 ? '#ff9800' : '#4caf50',
                    position: 'absolute',
                    left: 0,
                    '& .MuiCircularProgress-circle': {
                      strokeLinecap: 'round',
                    },
                  }}
                />
                <Box
                  sx={{
                    top: 0,
                    left: 0,
                    bottom: 0,
                    right: 0,
                    position: 'absolute',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#2c3e50' }}>
                    {burnoutRisk}
                  </Typography>
                </Box>
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1, textAlign: 'center', color: '#2c3e50' }}>
                Burnout Risk
              </Typography>
              <Chip 
                label={burnoutRisk < 40 ? 'Low Risk' : burnoutRisk < 70 ? 'Moderate Risk' : 'High Risk'}
                size="small"
                sx={{ 
                  bgcolor: burnoutRisk < 40 ? '#e8f5e9' : burnoutRisk < 70 ? '#fff3e0' : '#ffebee',
                  color: burnoutRisk < 40 ? '#2e7d32' : burnoutRisk < 70 ? '#e65100' : '#c62828',
                  fontWeight: 600,
                }}
              />
            </Box>
          </CardContent>
        </Card>

        {/* Efficiency Score Card */}
        <Card sx={{ boxShadow: 2, borderRadius: 2, border: '1px solid #e0e0e0' }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
                <CircularProgress
                  variant="determinate"
                  value={100}
                  size={120}
                  thickness={4}
                  sx={{
                    color: '#e0e0e0',
                  }}
                />
                <CircularProgress
                  variant="determinate"
                  value={efficiency}
                  size={120}
                  thickness={4}
                  sx={{
                    color: efficiency >= 80 ? '#4caf50' : efficiency >= 60 ? '#ff9800' : '#f44336',
                    position: 'absolute',
                    left: 0,
                    '& .MuiCircularProgress-circle': {
                      strokeLinecap: 'round',
                    },
                  }}
                />
                <Box
                  sx={{
                    top: 0,
                    left: 0,
                    bottom: 0,
                    right: 0,
                    position: 'absolute',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#2c3e50' }}>
                    {efficiency}
                  </Typography>
                </Box>
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1, textAlign: 'center', color: '#2c3e50' }}>
                Efficiency Score
              </Typography>
              <Typography variant="body2" sx={{ color: '#7f8c8d', textAlign: 'center' }}>
                Based on task completion and hours
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Productivity Metrics Grid */}
      <Typography variant="h6" sx={{ fontWeight: 700, mb: 3 }}>
        Weekly Breakdown
      </Typography>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)', lg: 'repeat(5, 1fr)' },
          gap: 3,
          mb: 4,
        }}
      >
          {[
            {
              title: 'Meeting Hours',
              value: meetingHours,
              unit: 'hrs/week',
              icon: <VideoCall />,
              color: '#1976d2',
              bgColor: '#e3f2fd',
              description: 'Time in meetings',
            },
            {
              title: 'Meeting Count',
              value: meetingCount,
              unit: 'meetings/week',
              icon: <VideoCall />,
              color: '#1976d2',
              bgColor: '#e3f2fd',
              description: 'Meetings attended',
            },
            {
              title: 'Messages Sent',
              value: messagesSent,
              unit: 'msgs/week',
              icon: <Chat />,
              color: '#388e3c',
              bgColor: '#e8f5e9',
              description: 'Messages sent',
            },
            {
              title: 'Messages Received',
              value: messagesReceived,
              unit: 'msgs/week',
              icon: <Chat />,
              color: '#388e3c',
              bgColor: '#e8f5e9',
              description: 'Messages received',
            },
            {
              title: 'Task Completion',
              value: taskCompletionRate,
              unit: '%',
              icon: <Assignment />,
              color: taskCompletionRate >= 80 ? '#388e3c' : taskCompletionRate >= 60 ? '#f57c00' : '#d32f2f',
              bgColor: taskCompletionRate >= 80 ? '#e8f5e9' : taskCompletionRate >= 60 ? '#fff3e0' : '#ffebee',
              description: 'Completion rate',
            },
            {
              title: 'Logged Hours',
              value: loggedHours,
              unit: 'hrs/week',
              icon: <AccessTime />,
              color: '#7b1fa2',
              bgColor: '#f3e5f5',
              description: 'Hours logged',
            },
            {
              title: 'Early Starts',
              value: earlyStarts,
              unit: 'days/week',
              icon: <Login />,
              color: '#388e3c',
              bgColor: '#e8f5e9',
              description: 'Started early',
            },
            {
              title: 'Late Exits',
              value: lateExits,
              unit: 'days/week',
              icon: <Logout />,
              color: '#7b1fa2',
              bgColor: '#f3e5f5',
              description: 'Left late',
            },
            {
              title: 'Late Starts',
              value: lateStarts,
              unit: 'days/week',
              icon: <TrendingUp />,
              color: '#e67e22',
              bgColor: '#e67e2215',
              description: 'Started late',
            },
            {
              title: 'Early Exits',
              value: earlyExits,
              unit: 'days/week',
              icon: <Speed />,
              color: '#c0392b',
              bgColor: '#c0392b15',
              description: 'Left early',
            },
            {
              title: 'Performance Score',
              value: 85,
              unit: '/100',
              icon: <TrendingUp />,
              color: '#8e44ad',
              bgColor: '#8e44ad15',
              description: 'Overall performance',
            },
          ].map((metric, index) => (
            <Paper
              key={index}
              sx={{
                p: 2.5,
                borderRadius: 3,
                boxShadow: 2,
                background: metric.bgColor,
                transition: 'all 0.3s ease',
                '&:hover': {
                  boxShadow: 6,
                  transform: 'translateY(-6px)',
                },
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                <Avatar
                  sx={{
                    width: 56,
                    height: 56,
                    bgcolor: 'rgba(255,255,255,0.9)',
                    color: metric.color,
                    boxShadow: 2,
                  }}
                >
                  {metric.icon}
                </Avatar>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="caption" sx={{ color: '#7f8c8d' }}>
                    {metric.title}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.5, mt: 0.5 }}>
                    <Typography
                      variant="h5"
                      sx={{
                        fontWeight: 700,
                        color: metric.color,
                      }}
                    >
                      {metric.value}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#7f8c8d' }}>
                      {metric.unit}
                    </Typography>
                  </Box>
                  <Typography variant="caption" sx={{ color: '#95a5a6', display: 'block', mt: 0.5 }}>
                    {metric.description}
                  </Typography>
                </Box>
              </Box>
            </Paper>
        ))}
      </Box>

      {/* Summary Cards */}
      <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
        Summary & Insights
      </Typography>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' },
          gap: 2,
        }}
      >
          <Card sx={{ boxShadow: 1 }}>
            <CardContent>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2 }}>
                Communication Activity
              </Typography>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                  <Typography variant="body2">Messages Sent</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    245
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                  <Typography variant="body2">Messages Received</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    187
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Net Ratio</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#1976d2' }}>
                    1.31x
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ boxShadow: 1, border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2 }}>
                Time Management
              </Typography>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                  <Typography variant="body2">Logged Hours</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    38.5h
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                  <Typography variant="body2">Meeting Hours</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    12.5h (32%)
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Deep Work Time</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#4caf50' }}>
                    26h (68%)
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ boxShadow: 1, border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2 }}>
                Attendance Patterns
              </Typography>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                  <Typography variant="body2">Early Starts</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#4caf50' }}>
                    3 days
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                  <Typography variant="body2">Late Starts</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#ff9800' }}>
                    1 day
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">On-Time %</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#4caf50' }}>
                    80%
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
      </Box>

      {/* Insights */}
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
          Key Insights
        </Typography>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' },
            gap: 3,
          }}
        >
            <Paper
              sx={{
                p: 2,
                borderLeft: '4px solid #4caf50',
                bgcolor: '#e8f5e9',
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                Strong Performance
              </Typography>
              <Typography variant="caption" sx={{ color: '#616161' }}>
                92% task completion rate shows excellent productivity
              </Typography>
            </Paper>

            <Paper
              sx={{
                p: 2,
                borderLeft: '4px solid #1976d2',
                bgcolor: '#e3f2fd',
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                Meeting Load
              </Typography>
              <Typography variant="caption" sx={{ color: '#616161' }}>
                32% of time in meetings - consider batching for deep work
              </Typography>
            </Paper>

            <Paper
              sx={{
                p: 2,
                borderLeft: '4px solid #ff9800',
                bgcolor: '#fff3e0',
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                Communicative
              </Typography>
              <Typography variant="caption" sx={{ color: '#7f8c8d' }}>
          245 messages sent - actively engaging with your team
        </Typography>
      </Paper>
    </Box>
  </Box>
</Box>
  );
};