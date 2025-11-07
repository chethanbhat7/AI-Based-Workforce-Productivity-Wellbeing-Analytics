import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Paper,
  CircularProgress,
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
    <Box sx={{ maxWidth: 1400, mx: 'auto', p: 3 }}>
      {/* Score Cards - Square boxes with circular progress */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' },
          gap: 3,
          mb: 4,
        }}
      >
        {/* Wellbeing Score Card */}
        <Card sx={{ boxShadow: 3, borderRadius: 2 }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
                <CircularProgress
                  variant="determinate"
                  value={wellbeingScore}
                  size={120}
                  thickness={4}
                  sx={{
                    color: '#f093fb',
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
                                    <Typography variant="h4" sx={{ fontWeight: 700, color: '#f093fb' }}>
                    {wellbeingScore}
                  </Typography>
                </Box>
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 1, textAlign: 'center' }}>
                Wellbeing Score
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary', textAlign: 'center' }}>
                Overall wellness based on workload, stress indicators, and work-life balance
              </Typography>
            </Box>
          </CardContent>
        </Card>

        {/* Burnout Risk Score Card */}
        <Card sx={{ boxShadow: 3, borderRadius: 2 }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
                <CircularProgress
                  variant="determinate"
                  value={burnoutRisk}
                  size={120}
                  thickness={4}
                  sx={{
                    color: '#fa709a',
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
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#fa709a' }}>
                    {burnoutRisk}
                  </Typography>
                </Box>
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 1, textAlign: 'center' }}>
                Burnout Risk Score
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary', textAlign: 'center' }}>
                {burnoutRisk < 40 ? 'Low risk - Your current workload and stress levels are manageable' : burnoutRisk < 70 ? 'Moderate risk - Consider balancing your workload' : 'High risk - Please take care of your wellbeing'}
              </Typography>
            </Box>
          </CardContent>
        </Card>

        {/* Efficiency Score Card */}
        <Card sx={{ boxShadow: 3, borderRadius: 2 }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
                <CircularProgress
                  variant="determinate"
                  value={efficiency}
                  size={120}
                  thickness={4}
                  sx={{
                    color: '#667eea',
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
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#667eea' }}>
                    {efficiency}
                  </Typography>
                </Box>
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 1, textAlign: 'center' }}>
                Overall Efficiency Score
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary', textAlign: 'center' }}>
                Based on task completion and logged hours
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
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: 'repeat(5, 1fr)' },
          gap: 2,
          mb: 4,
        }}
      >
          {[
            {
              title: 'Meeting Hours',
              value: meetingHours,
              unit: 'hrs/week',
              icon: <VideoCall />,
              color: '#3498db',
              bgColor: '#3498db15',
              description: 'Time in meetings',
            },
            {
              title: 'Meeting Count',
              value: meetingCount,
              unit: 'meetings/week',
              icon: <VideoCall />,
              color: '#e74c3c',
              bgColor: '#e74c3c15',
              description: 'Meetings attended',
            },
            {
              title: 'Messages Sent',
              value: messagesSent,
              unit: 'msgs/week',
              icon: <Chat />,
              color: '#2ecc71',
              bgColor: '#2ecc7115',
              description: 'Messages sent',
            },
            {
              title: 'Messages Received',
              value: messagesReceived,
              unit: 'msgs/week',
              icon: <Chat />,
              color: '#f39c12',
              bgColor: '#f39c1215',
              description: 'Messages received',
            },
            {
              title: 'Task Completion',
              value: taskCompletionRate,
              unit: '%',
              icon: <Assignment />,
              color: '#9b59b6',
              bgColor: '#9b59b615',
              description: 'Completion rate',
            },
            {
              title: 'Logged Hours',
              value: loggedHours,
              unit: 'hrs/week',
              icon: <AccessTime />,
              color: '#1abc9c',
              bgColor: '#1abc9c15',
              description: 'Hours logged',
            },
            {
              title: 'Early Starts',
              value: earlyStarts,
              unit: 'days/week',
              icon: <Login />,
              color: '#27ae60',
              bgColor: '#27ae6015',
              description: 'Started early',
            },
            {
              title: 'Late Exits',
              value: lateExits,
              unit: 'days/week',
              icon: <Logout />,
              color: '#16a085',
              bgColor: '#16a08515',
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
                borderRadius: 2,
                boxShadow: 1,
                transition: 'all 0.3s ease',
                '&:hover': {
                  boxShadow: 3,
                  transform: 'translateY(-4px)',
                },
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '4px',
                  bgcolor: metric.color,
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                <Avatar
                  sx={{
                    width: 48,
                    height: 48,
                    bgcolor: metric.bgColor,
                    color: metric.color,
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
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#3498db' }}>
                    1.31x
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ boxShadow: 1 }}>
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
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#2ecc71' }}>
                    26h (68%)
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ boxShadow: 1 }}>
            <CardContent>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2 }}>
                Attendance Patterns
              </Typography>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                  <Typography variant="body2">Early Starts</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#27ae60' }}>
                    3 days
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                  <Typography variant="body2">Late Starts</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#e67e22' }}>
                    1 day
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">On-Time %</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#2ecc71' }}>
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
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' },
            gap: 2,
          }}
        >
            <Paper
              sx={{
                p: 2,
                borderLeft: '4px solid #2ecc71',
                bgcolor: '#2ecc7110',
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                Strong Performance
              </Typography>
              <Typography variant="caption" sx={{ color: '#7f8c8d' }}>
                92% task completion rate shows excellent productivity
              </Typography>
            </Paper>

            <Paper
              sx={{
                p: 2,
                borderLeft: '4px solid #3498db',
                bgcolor: '#3498db10',
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                Meeting Heavy
              </Typography>
              <Typography variant="caption" sx={{ color: '#7f8c8d' }}>
                32% of time in meetings - consider batching for deep work
              </Typography>
            </Paper>

            <Paper
              sx={{
                p: 2,
                borderLeft: '4px solid #f39c12',
                bgcolor: '#f39c1210',
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