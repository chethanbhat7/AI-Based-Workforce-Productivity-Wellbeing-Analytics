import { Container, Card, CardContent, CardHeader, Box, Typography, List, ListItem, ListItemIcon, ListItemText, Chip, Toolbar, Divider, Avatar } from '@mui/material'
import { Warning, TrendingUp, People, CheckCircle, ErrorOutline } from '@mui/icons-material'
import StatCard from '../components/StatCard'
import BurnoutChart from '../components/BurnoutChart'

const atRiskEmployees = [
  { id: 1, name: 'John Smith', risk: 'High', score: 3.5 },
  { id: 2, name: 'Sarah Johnson', risk: 'Medium', score: 5.2 },
  { id: 3, name: 'Mike Davis', risk: 'High', score: 4.1 },
]

export default function SupervisorView() {
  return (
    <Box sx={{ flex: 1, overflow: 'auto', bgcolor: 'background.default', pt: { xs: 8, sm: 0 } }}>
      <Toolbar sx={{ bgcolor: 'background.paper', boxShadow: 1, mb: 3 }}>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Dashboard</Typography>
          <Typography variant="caption" color="textSecondary">Team Overview</Typography>
        </Box>
      </Toolbar>

      <Container maxWidth="lg" sx={{ pb: 4 }}>
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(4, 1fr)' }, gap: 2, mb: 3 }}>
          <StatCard title="Team Members" value={24} icon={<People />} bgColor="primary" trend={5} />
          <StatCard title="High Risk" value={3} icon={<Warning sx={{ color: 'error.main' }} />} bgColor="error" trend={-2} />
          <StatCard title="Medium Risk" value={5} icon={<TrendingUp sx={{ color: 'warning.main' }} />} bgColor="warning" trend={1} />
          <StatCard title="Avg Wellbeing" value={7.8} icon={<CheckCircle sx={{ color: 'success.main' }} />} bgColor="success" isScore trend={3} />
        </Box>

        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 3 }}>
          <Card sx={{ height: '100%' }}>
            <CardHeader title="Burnout Trend" subheader="Last 30 days" />
            <Divider />
            <CardContent sx={{ pt: 3 }}>
              <BurnoutChart />
            </CardContent>
          </Card>
          
          <Card sx={{ height: '100%' }}>
            <CardHeader 
              title="At Risk Employees" 
              avatar={<ErrorOutline sx={{ color: 'error.main' }} />}
            />
            <Divider />
            <CardContent sx={{ p: 0 }}>
              <List sx={{ width: '100%' }}>
                {atRiskEmployees.map((employee, index) => (
                  <Box key={employee.id}>
                    <ListItem sx={{ px: 2, py: 1.5 }}>
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: employee.risk === 'High' ? 'error.main' : 'warning.main' }}>
                          {employee.name.charAt(0)}
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={employee.name}
                        secondary={`Score: ${employee.score}/10`}
                      />
                      <Chip 
                        label={employee.risk} 
                        size="small"
                        color={employee.risk === 'High' ? 'error' : 'warning'}
                        variant="outlined"
                      />
                    </ListItem>
                    {index < atRiskEmployees.length - 1 && <Divider />}
                  </Box>
                ))}
              </List>
            </CardContent>
          </Card>
        </Box>
      </Container>
    </Box>
  )
}
