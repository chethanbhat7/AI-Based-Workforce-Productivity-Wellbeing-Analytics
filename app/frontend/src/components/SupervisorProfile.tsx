import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  LinearProgress,
  Paper,
} from '@mui/material';
import {
  VideoCall,
  AccessTime,
  TrendingUp,
  Speed,
  Login,
  Logout,
} from '@mui/icons-material';

export const SupervisorProfile = () => {
  return (
    <Box sx={{ width: '100%', p: 3 }}>
      {/* PRODUCTIVITY METRICS SECTION */}
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 4 }}>
        My Productivity Dashboard
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
                  {Math.round((92 + Math.max(0, 100 - 18 * 3) + Math.min(100, (38.5 / 40) * 100)) / 3)}
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
                value={75}
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
            value: 12.5,
            unit: 'hrs/week',
            icon: <VideoCall />,
            color: '#3498db',
            bgColor: '#3498db15',
            description: 'Time in meetings',
          },
          {
            title: 'Meeting Count',
            value: 18,
            unit: 'meetings/week',
            icon: <VideoCall />,
            color: '#e74c3c',
            bgColor: '#e74c3c15',
            description: 'Meetings attended',
          },
          {
            title: 'Logged Hours',
            value: 38.5,
            unit: 'hrs/week',
            icon: <AccessTime />,
            color: '#1abc9c',
            bgColor: '#1abc9c15',
            description: 'Hours logged',
          },
          {
            title: 'Early Starts',
            value: 3,
            unit: 'days/week',
            icon: <Login />,
            color: '#27ae60',
            bgColor: '#27ae6015',
            description: 'Started early',
          },
          {
            title: 'Late Exits',
            value: 2,
            unit: 'days/week',
            icon: <Logout />,
            color: '#16a085',
            bgColor: '#16a08515',
            description: 'Left late',
          },
          {
            title: 'Late Starts',
            value: 1,
            unit: 'days/week',
            icon: <TrendingUp />,
            color: '#e67e22',
            bgColor: '#e67e2215',
            description: 'Started late',
          },
          {
            title: 'Early Exits',
            value: 0,
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
    </Box>
  );
};
