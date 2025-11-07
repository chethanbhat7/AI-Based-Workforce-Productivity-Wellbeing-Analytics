import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  LinearProgress,
  Paper,
  IconButton,
  Breadcrumbs,
  Link,
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
  ArrowBack,
} from '@mui/icons-material';
import { collection, getDocs, query, where } from 'firebase/firestore';
import { db } from '../firebase/config';
import { generateConsistentValue, getTestScenarioValues } from '../utils/consistentValues';

interface MemberDetailProps {
  firebaseId: string;
  onBack: () => void;
}

interface MemberData {
  id: number;
  name: string;
  email: string;
  department: string;
  meetingHours: number;
  meetingCount: number;
  messagesSent: number;
  messagesReceived: number;
  taskCompletion: number;
  loggedHours: number;
  earlyStarts: number;
  lateExits: number;
  lateStarts: number;
  earlyExits: number;
}

export const MemberDetail = ({ firebaseId, onBack }: MemberDetailProps) => {
  const [memberData, setMemberData] = useState<MemberData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMemberData = async () => {
      try {
        setLoading(true);
        
        // Fetch the specific member by Firebase ID
        const membersRef = collection(db, 'users');
        const q = query(membersRef, where('role', '==', 'member'));
        const querySnapshot = await getDocs(q);
        
        let member: any = null;
        querySnapshot.forEach((doc) => {
          if (doc.id === firebaseId) {
            member = { firebaseId: doc.id, ...doc.data() };
          }
        });
        
        if (member) {
          const email = member.email || '';
          const testScenario = getTestScenarioValues(email);
          
          setMemberData({
            id: 1, // Not used anymore, but kept for backwards compatibility
            name: member.name || 'Unknown',
            email: email,
            department: member.department || 'Engineering',
            meetingHours: member.analytics?.meetingHours ?? generateConsistentValue(email, 5, 8, 15),
            meetingCount: member.analytics?.meetingCount ?? generateConsistentValue(email, 6, 10, 20),
            messagesSent: member.analytics?.messagesSent ?? generateConsistentValue(email, 7, 100, 250),
            messagesReceived: member.analytics?.messagesReceived ?? generateConsistentValue(email, 8, 100, 250),
            taskCompletion: testScenario?.taskCompletionRate ?? member.analytics?.taskCompletionRate ?? generateConsistentValue(email, 1, 60, 100),
            loggedHours: member.analytics?.loggedHours ?? generateConsistentValue(email, 2, 30, 45),
            earlyStarts: member.analytics?.earlyStarts ?? generateConsistentValue(email, 9, 0, 5),
            lateExits: member.analytics?.lateExits ?? generateConsistentValue(email, 10, 0, 3),
            lateStarts: member.analytics?.lateStarts ?? generateConsistentValue(email, 11, 0, 2),
            earlyExits: member.analytics?.earlyExits ?? generateConsistentValue(email, 12, 0, 2),
          });
        }
      } catch (error) {
        console.error('Error fetching member data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMemberData();
  }, [firebaseId]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!memberData) {
    return (
      <Box sx={{ width: '100%', p: 3 }}>
        <Typography variant="h6" sx={{ color: '#7f8c8d' }}>
          Member not found
        </Typography>
      </Box>
    );
  }

  const efficiencyScore = Math.round(
    (memberData.taskCompletion + Math.max(0, 100 - memberData.meetingCount * 3) + Math.min(100, (memberData.loggedHours / 40) * 100)) / 3
  );

  return (
    <Box sx={{ width: '100%', p: 3 }}>
      {/* Breadcrumb Navigation */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <IconButton onClick={onBack} sx={{ bgcolor: '#ecf0f1' }}>
          <ArrowBack />
        </IconButton>
        <Breadcrumbs>
          <Link
            component="button"
            variant="body2"
            onClick={onBack}
            sx={{ cursor: 'pointer', textDecoration: 'none', color: '#3498db' }}
          >
            Team Overview
          </Link>
          <Typography variant="body2" color="text.primary">
            {memberData.name}
          </Typography>
        </Breadcrumbs>
      </Box>

      {/* Member Header */}
      <Card sx={{ mb: 4, boxShadow: 2 }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
            <Avatar
              sx={{
                width: 80,
                height: 80,
                bgcolor: '#3498db',
                fontSize: 32,
              }}
            >
              {memberData.name.charAt(0)}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
                {memberData.name}
              </Typography>
              <Typography variant="body2" sx={{ color: '#7f8c8d', mb: 1 }}>
                {memberData.email} • {memberData.department}
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* PRODUCTIVITY METRICS SECTION */}
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 4 }}>
        Productivity Dashboard
      </Typography>

      {/* Efficiency Score Card */}
      <Card
        sx={{
          bgcolor: 'white',
          border: '1px solid',
          borderColor: 'divider',
          mb: 4,
          boxShadow: 2,
        }}
      >
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
            <Box
              sx={{
                width: 100,
                height: 100,
                borderRadius: '50%',
                bgcolor: '#e3f2fd',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h3" sx={{ fontWeight: 700, color: '#1976d2' }}>
                  {efficiencyScore}
                </Typography>
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>/100</Typography>
              </Box>
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                Overall Efficiency Score
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
                Based on task completion, meeting time, and logged hours
              </Typography>
              <LinearProgress
                variant="determinate"
                value={efficiencyScore}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  bgcolor: '#e0e0e0',
                  '& .MuiLinearProgress-bar': {
                    bgcolor: '#1976d2',
                    borderRadius: 4,
                  },
                }}
              />
            </Box>
          </Box>
        </CardContent>
      </Card>

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
            value: memberData.meetingHours,
            unit: 'hrs/week',
            icon: <VideoCall />,
            color: '#3498db',
            bgColor: '#3498db15',
            description: 'Time in meetings',
          },
          {
            title: 'Meeting Count',
            value: memberData.meetingCount,
            unit: 'meetings/week',
            icon: <VideoCall />,
            color: '#e74c3c',
            bgColor: '#e74c3c15',
            description: 'Meetings attended',
          },
          {
            title: 'Messages Sent',
            value: memberData.messagesSent,
            unit: 'msgs/week',
            icon: <Chat />,
            color: '#2ecc71',
            bgColor: '#2ecc7115',
            description: 'Messages sent',
          },
          {
            title: 'Messages Received',
            value: memberData.messagesReceived,
            unit: 'msgs/week',
            icon: <Chat />,
            color: '#f39c12',
            bgColor: '#f39c1215',
            description: 'Messages received',
          },
          {
            title: 'Task Completion',
            value: memberData.taskCompletion,
            unit: '%',
            icon: <Assignment />,
            color: '#9b59b6',
            bgColor: '#9b59b615',
            description: 'Completion rate',
          },
          {
            title: 'Logged Hours',
            value: memberData.loggedHours,
            unit: 'hrs/week',
            icon: <AccessTime />,
            color: '#1abc9c',
            bgColor: '#1abc9c15',
            description: 'Hours logged',
          },
          {
            title: 'Early Starts',
            value: memberData.earlyStarts,
            unit: 'days/week',
            icon: <Login />,
            color: '#27ae60',
            bgColor: '#27ae6015',
            description: 'Started early',
          },
          {
            title: 'Late Exits',
            value: memberData.lateExits,
            unit: 'days/week',
            icon: <Logout />,
            color: '#16a085',
            bgColor: '#16a08515',
            description: 'Left late',
          },
          {
            title: 'Late Starts',
            value: memberData.lateStarts,
            unit: 'days/week',
            icon: <TrendingUp />,
            color: '#e67e22',
            bgColor: '#e67e2215',
            description: 'Started late',
          },
          {
            title: 'Early Exits',
            value: memberData.earlyExits,
            unit: 'days/week',
            icon: <Speed />,
            color: '#c0392b',
            bgColor: '#c0392b15',
            description: 'Left early',
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
                  {memberData.messagesSent}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                <Typography variant="body2">Messages Received</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {memberData.messagesReceived}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Net Ratio</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600, color: '#3498db' }}>
                  {(memberData.messagesSent / memberData.messagesReceived).toFixed(2)}x
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
                  {memberData.loggedHours}h
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                <Typography variant="body2">Meeting Hours</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {memberData.meetingHours}h ({Math.round((memberData.meetingHours / memberData.loggedHours) * 100)}%)
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Deep Work Time</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600, color: '#2ecc71' }}>
                  {(memberData.loggedHours - memberData.meetingHours).toFixed(1)}h ({100 - Math.round((memberData.meetingHours / memberData.loggedHours) * 100)}%)
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
                  {memberData.earlyStarts} days
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                <Typography variant="body2">Late Starts</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600, color: '#e67e22' }}>
                  {memberData.lateStarts} day
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">On-Time %</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600, color: '#2ecc71' }}>
                  {Math.round(((5 - memberData.lateStarts) / 5) * 100)}%
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
              {memberData.taskCompletion}% task completion rate shows excellent productivity
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
              Meeting Load
            </Typography>
            <Typography variant="caption" sx={{ color: '#7f8c8d' }}>
              {Math.round((memberData.meetingHours / memberData.loggedHours) * 100)}% of time in meetings
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
              {memberData.messagesSent} messages sent - actively engaging
            </Typography>
          </Paper>
        </Box>
      </Box>
    </Box>
  );
};
