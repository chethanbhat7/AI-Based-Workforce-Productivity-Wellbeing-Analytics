import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  LinearProgress,
  Chip,
  Divider,
  Paper,
} from '@mui/material';
import {
  Psychology,
  Mediation,
  FitnessCenter,
  EmojiEmotions,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

interface WellbeingScore {
  category: string;
  score: number;
  icon: JSX.Element;
  description: string;
  color: string;
}

export const WellbeingProfile = () => {
  const { user } = useAuth();

  // Mock wellbeing data - in production, this would come from backend
  const wellbeingScores: WellbeingScore[] = [
    {
      category: 'Mental Health',
      score: 78,
      icon: <Psychology sx={{ color: '#8e44ad' }} />,
      description: 'Excellent mindfulness practice',
      color: '#8e44ad',
    },
    {
      category: 'Physical Health',
      score: 85,
      icon: <FitnessCenter sx={{ color: '#e74c3c' }} />,
      description: 'Regular exercise routine',
      color: '#e74c3c',
    },
    {
      category: 'Work-Life Balance',
      score: 72,
      icon: <EmojiEmotions sx={{ color: '#f39c12' }} />,
      description: 'Good balance maintained',
      color: '#f39c12',
    },
    {
      category: 'Stress Management',
      score: 65,
      icon: <Mediation sx={{ color: '#1abc9c' }} />,
      description: 'Needs improvement',
      color: '#1abc9c',
    },
  ];

  const overallScore = Math.round(
    wellbeingScores.reduce((sum, item) => sum + item.score, 0) / wellbeingScores.length
  );

  const getStatusMessage = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Fair';
    return 'Needs Improvement';
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      {/* Main Profile Card */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1fr 2fr' },
          gap: 3,
        }}
      >
        {/* Left - Profile Info */}
        <Box>
          <Card sx={{ boxShadow: 3, borderRadius: 2 }}>
            <CardContent sx={{ textAlign: 'center', pt: 4, pb: 3 }}>
              {/* Avatar */}
              <Avatar
                sx={{
                  width: 120,
                  height: 120,
                  bgcolor: '#3498db',
                  fontSize: 48,
                  mx: 'auto',
                  mb: 2,
                }}
              >
                {user?.name.charAt(0).toUpperCase()}
              </Avatar>

              {/* Name */}
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
                {user?.name}
              </Typography>
              <Typography variant="body2" sx={{ color: '#7f8c8d', mb: 3 }}>
                {user?.email}
              </Typography>

              {/* Overall Wellbeing Score */}
              <Box
                sx={{
                  bgcolor: '#ecf0f1',
                  p: 2,
                  borderRadius: 2,
                  mb: 2,
                }}
              >
                <Typography variant="caption" sx={{ color: '#7f8c8d' }}>
                  OVERALL WELLBEING SCORE
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mt: 1 }}>
                  <Typography variant="h3" sx={{ fontWeight: 700, color: '#3498db' }}>
                    {overallScore}
                  </Typography>
                  <Typography variant="h6" sx={{ color: '#7f8c8d' }}>/100</Typography>
                </Box>
                <Chip
                  label={getStatusMessage(overallScore)}
                  sx={{
                    mt: 1,
                    bgcolor: overallScore >= 75 ? '#2ecc71' : overallScore >= 60 ? '#f39c12' : '#e74c3c',
                    color: 'white',
                  }}
                />
              </Box>

              {/* Stats */}
              <Divider sx={{ my: 2 }} />
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, my: 2 }}>
                <Box>
                  <Typography variant="caption" sx={{ color: '#7f8c8d', textTransform: 'uppercase' }}>
                    Check-ins
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: '#2c3e50' }}>
                    24
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" sx={{ color: '#7f8c8d', textTransform: 'uppercase' }}>
                    Streak
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: '#2c3e50' }}>
                    7d
                  </Typography>
                </Box>
              </Box>
          </CardContent>
        </Card>
        </Box>

        {/* Right - Wellbeing Categories */}
        <Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 3 }}>
              Wellbeing Breakdown
            </Typography>

            {wellbeingScores.map((item, index) => (
              <Paper key={index} sx={{ p: 2.5, mb: 2, borderRadius: 2, boxShadow: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                  {/* Icon */}
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 48,
                      height: 48,
                      bgcolor: `${item.color}15`,
                      borderRadius: 1.5,
                      mt: 0.5,
                    }}
                  >
                    {item.icon}
                  </Box>

                  {/* Content */}
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {item.category}
                      </Typography>
                      <Typography
                        variant="subtitle2"
                        sx={{ fontWeight: 700, color: item.color }}
                      >
                        {item.score}/100
                      </Typography>
                    </Box>

                    {/* Progress Bar */}
                    <LinearProgress
                      variant="determinate"
                      value={item.score}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        bgcolor: '#ecf0f1',
                        '& .MuiLinearProgress-bar': {
                          bgcolor: item.color,
                          borderRadius: 4,
                        },
                      }}
                    />

                    {/* Description */}
                    <Typography variant="caption" sx={{ color: '#7f8c8d', display: 'block', mt: 1 }}>
                      {item.description}
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            ))}
          </Box>
        </Box>
      </Box>

      {/* Recent Activities */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
          Recent Check-ins
        </Typography>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' },
            gap: 2,
          }}
        >
          {[
            { date: 'Today', mood: 'Energetic', status: '😊' },
            { date: 'Yesterday', mood: 'Stressed', status: '😰' },
            { date: '2 days ago', mood: 'Calm', status: '🧘' },
            { date: '3 days ago', mood: 'Happy', status: '😄' },
          ].map((activity, index) => (
            <Box key={index}>
              <Paper
                sx={{
                  p: 2,
                  textAlign: 'center',
                  borderRadius: 2,
                  boxShadow: 1,
                  '&:hover': {
                    boxShadow: 3,
                    transform: 'translateY(-2px)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                <Typography variant="h3" sx={{ mb: 1 }}>
                  {activity.status}
                </Typography>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  {activity.mood}
                </Typography>
                <Typography variant="caption" sx={{ color: '#7f8c8d' }}>
                  {activity.date}
                </Typography>
              </Paper>
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
};
