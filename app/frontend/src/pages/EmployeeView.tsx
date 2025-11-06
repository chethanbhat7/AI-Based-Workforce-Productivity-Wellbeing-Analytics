import { Box, Container, Card, CardContent, CardHeader, Typography, LinearProgress, Alert as MuiAlert, Toolbar, Stack, Divider } from '@mui/material'
import { Favorite, TrendingDown, Schedule, Bolt, CheckCircle, Info, Psychology, FitnessCenter, HelpOutline } from '@mui/icons-material'
import StatCard from '../components/StatCard'

export default function EmployeeView() {
  const wellnessTips = [
    'Take 5-minute breaks every hour to stretch',
    'Maintain a consistent sleep schedule (7-8 hours)',
    'Stay hydrated with 8 glasses of water daily',
    'Practice 10 minutes of meditation daily',
    'Exercise at least 30 minutes, 3x per week',
  ]

  return (
    <Box sx={{ flex: 1, overflow: 'auto', bgcolor: 'background.default', pt: { xs: 8, sm: 0 } }}>
      <Toolbar sx={{ bgcolor: 'background.paper', boxShadow: 1, mb: 3 }}>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>My Wellbeing</Typography>
          <Typography variant="caption" color="textSecondary">Personal Health Dashboard</Typography>
        </Box>
        <Box sx={{ textAlign: 'right' }}>
          <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block' }}>Status</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5, justifyContent: 'flex-end' }}>
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'success.main' }} />
            <Typography variant="body2" sx={{ fontWeight: 500 }}>Healthy</Typography>
          </Box>
        </Box>
      </Toolbar>

      <Container maxWidth="lg" sx={{ pb: 4 }}>
        {/* Key Metrics */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: 'repeat(4, 1fr)' }, gap: 2, mb: 4 }}>
          <StatCard title="Wellbeing Score" value={7.5} icon={<Favorite />} bgColor="primary" isScore trend={5} />
          <StatCard title="Stress Level" value={4.2} icon={<TrendingDown />} bgColor="success" isScore trend={-2} />
          <StatCard title="Work-Life Balance" value={6.8} icon={<Schedule />} bgColor="info" isScore trend={3} />
          <StatCard title="Energy Level" value={7.2} icon={<Bolt />} bgColor="warning" isScore trend={1} />
        </Box>

        {/* Main Grid */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' }, gap: 3, mb: 4 }}>
          {/* Personalized Feedback */}
          <Card>
            <CardHeader title="Personalized Feedback" subheader="Based on your recent activity" />
            <Divider />
            <CardContent>
              <Stack spacing={2}>
                <MuiAlert severity="success">
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>Keep it up! 🎉</Typography>
                  <Typography variant="caption">You're maintaining a great work-life balance. Continue with your current routine.</Typography>
                </MuiAlert>
                <MuiAlert severity="info">
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>Doing great!</Typography>
                  <Typography variant="caption">Your stress levels are well-managed. Stay consistent with your wellness habits.</Typography>
                </MuiAlert>
                <MuiAlert severity="info">
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>Stay hydrated 💧</Typography>
                  <Typography variant="caption">Remember to drink water regularly throughout your workday for better productivity.</Typography>
                </MuiAlert>
              </Stack>
            </CardContent>
          </Card>

          {/* Weekly Stats */}
          <Card>
            <CardHeader title="This Week" />
            <Divider />
            <CardContent>
              <Stack spacing={2.5}>
                {[
                  { label: 'Productivity', value: 85 },
                  { label: 'Sleep Quality', value: 78 },
                  { label: 'Exercise', value: 60 },
                  { label: 'Meditation', value: 45 },
                ].map((stat) => (
                  <Box key={stat.label}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="caption" sx={{ fontWeight: 500 }}>{stat.label}</Typography>
                      <Typography variant="caption" sx={{ fontWeight: 600 }}>{stat.value}%</Typography>
                    </Box>
                    <LinearProgress variant="determinate" value={stat.value} sx={{ height: 6, borderRadius: 1 }} />
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Box>

        {/* Bottom Section */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 3 }}>
          {/* Wellness Tips */}
          <Card>
            <CardHeader
              title="Wellness Tips"
              avatar={<CheckCircle sx={{ color: 'success.main' }} />}
            />
            <Divider />
            <CardContent>
              <Stack spacing={1.5}>
                {wellnessTips.map((tip, idx) => (
                  <Box key={idx} sx={{ display: 'flex', gap: 1.5 }}>
                    <CheckCircle sx={{ color: 'success.main', fontSize: 18, flexShrink: 0, mt: 0.3 }} />
                    <Typography variant="body2" color="textSecondary">{tip}</Typography>
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </Card>

          {/* Support Resources */}
          <Card>
            <CardHeader
              title="Need Support?"
              avatar={<Info sx={{ color: 'info.main' }} />}
            />
            <Divider />
            <CardContent>
              <Stack spacing={1.5}>
                <Box sx={{ p: 1.5, bgcolor: 'info.lighter', borderRadius: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <Psychology sx={{ fontSize: 18, color: 'info.main' }} />
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>Mental Health Resources</Typography>
                  </Box>
                  <Typography variant="caption" color="textSecondary">Access counseling services and mental health support</Typography>
                </Box>
                <Box sx={{ p: 1.5, bgcolor: 'warning.lighter', borderRadius: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <FitnessCenter sx={{ fontSize: 18, color: 'warning.main' }} />
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>Fitness Programs</Typography>
                  </Box>
                  <Typography variant="caption" color="textSecondary">Join group fitness classes and wellness challenges</Typography>
                </Box>
                <Box sx={{ p: 1.5, bgcolor: 'error.lighter', borderRadius: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <HelpOutline sx={{ fontSize: 18, color: 'error.main' }} />
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>Emergency Support</Typography>
                  </Box>
                  <Typography variant="caption" color="textSecondary">24/7 assistance available for urgent matters</Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Box>
      </Container>
    </Box>
  )
}
