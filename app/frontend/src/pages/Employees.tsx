import React from 'react'
import { 
  Box, 
  Container, 
  Card, 
  CardContent, 
  CardHeader, 
  Typography, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Paper,
  Toolbar,
  Avatar,
  Stack,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material'
import { MoreVert, OpenInNew } from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'

interface Employee {
  id: string
  name: string
  email: string
  role: string
  wellbeingScore: number
  riskLevel: 'Low' | 'Medium' | 'High'
  status: 'Healthy' | 'At Risk' | 'Critical'
}

const teamMembers: Employee[] = [
  {
    id: 'emp001',
    name: 'Alice Johnson',
    email: 'alice@example.com',
    role: 'Senior Developer',
    wellbeingScore: 8.2,
    riskLevel: 'Low',
    status: 'Healthy',
  },
  {
    id: 'emp002',
    name: 'Bob Smith',
    email: 'bob@example.com',
    role: 'Product Manager',
    wellbeingScore: 5.8,
    riskLevel: 'Medium',
    status: 'At Risk',
  },
  {
    id: 'emp003',
    name: 'Carol Davis',
    email: 'carol@example.com',
    role: 'Designer',
    wellbeingScore: 7.5,
    riskLevel: 'Low',
    status: 'Healthy',
  },
  {
    id: 'emp004',
    name: 'David Wilson',
    email: 'david@example.com',
    role: 'QA Engineer',
    wellbeingScore: 3.2,
    riskLevel: 'High',
    status: 'Critical',
  },
  {
    id: 'emp005',
    name: 'Emma Brown',
    email: 'emma@example.com',
    role: 'Data Analyst',
    wellbeingScore: 7.1,
    riskLevel: 'Low',
    status: 'Healthy',
  },
]

export default function Employees() {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null)
  const [selectedEmployee, setSelectedEmployee] = React.useState<Employee | null>(null)
  const navigate = useNavigate()

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, employee: Employee) => {
    setAnchorEl(event.currentTarget)
    setSelectedEmployee(employee)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
    setSelectedEmployee(null)
  }

  const handleViewDetails = (employee: Employee) => {
    navigate(`/employee/${employee.id}`, { state: { employee } })
    handleMenuClose()
  }

  const getRiskColor = (riskLevel: string): 'success' | 'warning' | 'error' => {
    switch (riskLevel) {
      case 'Low':
        return 'success'
      case 'Medium':
        return 'warning'
      case 'High':
        return 'error'
      default:
        return 'success'
    }
  }

  const getStatusColor = (status: string): 'success' | 'warning' | 'error' => {
    switch (status) {
      case 'Healthy':
        return 'success'
      case 'At Risk':
        return 'warning'
      case 'Critical':
        return 'error'
      default:
        return 'success'
    }
  }

  return (
    <Box sx={{ flex: 1, overflow: 'auto', bgcolor: 'background.default', pt: { xs: 8, sm: 0 } }}>
      <Toolbar sx={{ bgcolor: 'background.paper', boxShadow: 1, mb: 3 }}>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Team Members</Typography>
          <Typography variant="caption" color="textSecondary">Manage and monitor team wellbeing</Typography>
        </Box>
      </Toolbar>

      <Container maxWidth="lg" sx={{ pb: 4 }}>
        <Card sx={{ boxShadow: 2 }}>
          <CardHeader
            title="Team Members List"
            subheader={`${teamMembers.length} employees under supervision`}
          />
          <Divider />
          <CardContent sx={{ p: 0 }}>
            <TableContainer component={Paper} sx={{ boxShadow: 'none' }}>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: 'background.default' }}>
                    <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Email</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Position</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 600 }}>Wellbeing Score</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 600 }}>Risk Level</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 600 }}>Status</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 600 }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {teamMembers.map((employee) => (
                    <TableRow 
                      key={employee.id}
                      sx={{
                        '&:hover': { bgcolor: 'action.hover' },
                        '&:last-child td, &:last-child th': { border: 0 },
                      }}
                    >
                      <TableCell>
                        <Stack direction="row" spacing={2} alignItems="center">
                          <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                            {employee.name.charAt(0)}
                          </Avatar>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {employee.name}
                          </Typography>
                        </Stack>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="textSecondary">
                          {employee.email}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {employee.role}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
                          {employee.wellbeingScore}/10
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={employee.riskLevel}
                          color={getRiskColor(employee.riskLevel)}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={employee.status}
                          color={getStatusColor(employee.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                          size="small"
                          onClick={(e) => handleMenuOpen(e, employee)}
                        >
                          <MoreVert fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>

        {/* Context Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={() => selectedEmployee && handleViewDetails(selectedEmployee)}>
            <OpenInNew fontSize="small" sx={{ mr: 1 }} />
            View Details
          </MenuItem>
        </Menu>
      </Container>
    </Box>
  )
}
