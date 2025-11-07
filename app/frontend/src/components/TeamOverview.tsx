import { useState, useEffect } from 'react';
import { collection, query, where, getDocs, addDoc, serverTimestamp } from 'firebase/firestore';
import { db } from '../firebase/config';
import { useAuth } from '../context/AuthContext';
import { generateConsistentValue, getConsistentStressLevel, getConsistentTrend, getConsistentLastActive, getTestScenarioValues } from '../utils/consistentValues';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Chip,
  LinearProgress,
  Paper,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning,
  Psychology,
  FitnessCenter,
  AccessTime,
  Assignment,
} from '@mui/icons-material';

interface TeamMember {
  id: number;
  name: string;
  email: string;
  taskCompletionRate: number;
  loggedHours: number;
  wellbeingScore: number;
  isExhausted: boolean;
  stressLevel: 'low' | 'medium' | 'high';
  trend: 'up' | 'down' | 'stable';
  lastActive: string;
  firebaseId: string; // Made required instead of optional
  // Model predictions
  burnoutRisk?: number;
  efficiency?: number;
  colleagueVotes?: {
    burnoutYes: number;
    burnoutNo: number;
    teamworkYes: number;
    teamworkNo: number;
    motivationYes: number;
    motivationNo: number;
    totalVoters: number;
  };
}

interface TeamOverviewProps {
  onViewMember: (firebaseId: string) => void;
}

export const TeamOverview = ({ onViewMember }: TeamOverviewProps) => {
  const { user } = useAuth();
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch team members from Firestore
  useEffect(() => {
    const fetchTeamMembers = async () => {
      if (!user) return;

      try {
        setLoading(true);
        const supervisorTeamNumber = (user as any).teamNumber || '1';
        
        // Query Firestore for members with matching team number
        const membersRef = collection(db, 'users');
        const q = query(
          membersRef,
          where('role', '==', 'member'),
          where('teamNumber', '==', supervisorTeamNumber)
        );
        
        const querySnapshot = await getDocs(q);
        const members: TeamMember[] = [];
        
        // Fetch all colleague votes
        const votesRef = collection(db, 'colleague_votes');
        const votesSnapshot = await getDocs(votesRef);
        
        console.log('Total votes in database:', votesSnapshot.size);
        
        // Create a map of colleagueId -> votes
        const votesMap = new Map<string, any>();
        votesSnapshot.forEach((doc) => {
          const voteData = doc.data();
          console.log('Vote data:', voteData);
          const colleagueId = voteData.colleagueId;
          
          if (!votesMap.has(colleagueId)) {
            votesMap.set(colleagueId, {
              burnoutYes: 0,
              burnoutNo: 0,
              teamworkYes: 0,
              teamworkNo: 0,
              motivationYes: 0,
              motivationNo: 0,
              voters: new Set(),
            });
          }
          
          const votes = votesMap.get(colleagueId);
          votes.voters.add(voteData.voterId);
          
          // Count the votes
          if (voteData.votes?.burnout === 'yes') votes.burnoutYes++;
          if (voteData.votes?.burnout === 'no') votes.burnoutNo++;
          if (voteData.votes?.teamwork === 'yes') votes.teamworkYes++;
          if (voteData.votes?.teamwork === 'no') votes.teamworkNo++;
          if (voteData.votes?.motivation === 'yes') votes.motivationYes++;
          if (voteData.votes?.motivation === 'no') votes.motivationNo++;
        });
        
        console.log('Votes map:', Array.from(votesMap.entries()));
        
        querySnapshot.forEach((doc) => {
          const data = doc.data();
          const email = data.email || '';
          const firebaseId = doc.id;
          
          // Check for test scenario values first
          const testScenario = getTestScenarioValues(email);
          
          // Get colleague votes for this member
          const memberVotes = votesMap.get(firebaseId);
          const colleagueVotes = memberVotes ? {
            burnoutYes: memberVotes.burnoutYes,
            burnoutNo: memberVotes.burnoutNo,
            teamworkYes: memberVotes.teamworkYes,
            teamworkNo: memberVotes.teamworkNo,
            motivationYes: memberVotes.motivationYes,
            motivationNo: memberVotes.motivationNo,
            totalVoters: memberVotes.voters.size,
          } : undefined;
          
          console.log(`Member ${data.name} (${firebaseId}) votes:`, colleagueVotes);
          
          const taskCompletionRate = testScenario?.taskCompletionRate ?? data.analytics?.taskCompletionRate ?? generateConsistentValue(email, 1, 60, 100);
          const loggedHours = data.analytics?.loggedHours ?? generateConsistentValue(email, 2, 30, 45);
          const wellbeingScore = testScenario?.wellbeingScore ?? data.analytics?.wellbeingScore ?? generateConsistentValue(email, 3, 50, 90);
          const isExhausted = testScenario?.isExhausted ?? data.analytics?.isExhausted ?? (generateConsistentValue(email, 4, 0, 100) < 30);
          
          // Calculate burnout risk and efficiency (simple heuristics, can be replaced with model predictions)
          const meetingHours = data.analytics?.meetingHours ?? generateConsistentValue(email, 5, 8, 18);
          const burnoutRisk = data.analytics?.burnoutRisk ?? Math.min(100, Math.max(0, 100 - wellbeingScore + (meetingHours > 15 ? 20 : 0) + (isExhausted ? 30 : 0)));
          const efficiency = data.analytics?.efficiency ?? Math.round((taskCompletionRate + Math.min(100, (loggedHours / 40) * 100)) / 2);
          
          // Use test scenario, then real data, then fallback to consistent dummy values
          members.push({
            id: members.length + 1,
            firebaseId,
            name: data.name || 'Unknown',
            email: email,
            taskCompletionRate,
            loggedHours,
            wellbeingScore,
            isExhausted,
            stressLevel: testScenario?.stressLevel ?? data.analytics?.stressLevel ?? getConsistentStressLevel(email),
            trend: data.analytics?.trend ?? getConsistentTrend(email),
            lastActive: data.analytics?.lastActive ?? getConsistentLastActive(email),
            burnoutRisk,
            efficiency,
            colleagueVotes,
          });
        });
        
        setTeamMembers(members);
        
        // Check for members with majority burnout votes and create notifications
        await checkBurnoutMajority(members, user.id);
      } catch (error) {
        console.error('Error fetching team members:', error);
        // Show empty array on error instead of mock data
        setTeamMembers([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTeamMembers();
  }, [user]);

  // Function to check for majority burnout votes and create notifications
  const checkBurnoutMajority = async (members: TeamMember[], supervisorId: string) => {
    try {
      const notificationsRef = collection(db, 'notifications');
      
      for (const member of members) {
        if (member.colleagueVotes && member.colleagueVotes.totalVoters >= 2) {
          const totalVotes = member.colleagueVotes.burnoutYes + member.colleagueVotes.burnoutNo;
          const burnoutPercentage = totalVotes > 0 ? (member.colleagueVotes.burnoutYes / totalVotes) * 100 : 0;
          
          // If majority (>50%) say burnt out
          if (burnoutPercentage > 50) {
            // Check if we already sent this notification recently
            const recentNotifications = query(
              notificationsRef,
              where('userId', '==', supervisorId),
              where('type', '==', 'colleague_burnout_alert'),
              where('memberId', '==', member.firebaseId)
            );
            
            const notificationSnapshot = await getDocs(recentNotifications);
            
            // Only create notification if we haven't sent one recently
            if (notificationSnapshot.empty) {
              await addDoc(notificationsRef, {
                userId: supervisorId,
                type: 'colleague_burnout_alert',
                memberId: member.firebaseId,
                memberName: member.name,
                title: 'Colleague Burnout Alert',
                message: `${member.colleagueVotes.burnoutYes} out of ${member.colleagueVotes.totalVoters} colleagues report that ${member.name} seems burnt out. Please check in with them.`,
                severity: 'high',
                read: false,
                timestamp: serverTimestamp(),
                metadata: {
                  burnoutVotes: member.colleagueVotes.burnoutYes,
                  totalVoters: member.colleagueVotes.totalVoters,
                  percentage: Math.round(burnoutPercentage),
                }
              });
              
              console.log(`Created burnout alert for ${member.name}: ${member.colleagueVotes.burnoutYes}/${member.colleagueVotes.totalVoters} votes`);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error checking burnout majority:', error);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (teamMembers.length === 0) {
    return (
      <Box sx={{ width: '100%', p: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
          Team Overview
        </Typography>
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" sx={{ color: '#7f8c8d', mb: 1 }}>
            No team members found
          </Typography>
          <Typography variant="body2" sx={{ color: '#95a5a6' }}>
            There are no members assigned to team number {(user as any)?.teamNumber || '1'} yet.
          </Typography>
        </Paper>
      </Box>
    );
  }

  const getStressColor = (stressLevel: string) => {
    if (stressLevel === 'low') {
        return '#1e7e45';  // Darker green
    } else if (stressLevel === 'medium') {
        return '#c77c11';  // Darker orange
    } else {
        return '#a93226';  // Darker red
    }
  };

  const getWellbeingStatus = (score: number) => {
    if (score >= 80) return { label: 'Excellent', color: '#1e7e45' };
    if (score >= 70) return { label: 'Good', color: '#1e5f8c' };
    if (score >= 60) return { label: 'Fair', color: '#c77c11' };
    return { label: 'Poor', color: '#a93226' };
  };

  const exhaustedMembers = teamMembers.filter(m => m.isExhausted).length;
  const highStressMembers = teamMembers.filter(m => m.stressLevel === 'high').length;
  const avgTaskCompletion = teamMembers.length > 0 
    ? Math.round(teamMembers.reduce((sum, m) => sum + m.taskCompletionRate, 0) / teamMembers.length)
    : 0;

  return (
    <Box sx={{ width: '100%', p: 3 }}>
      {/* Header Stats */}
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
        Team Overview
      </Typography>

      {/* Summary Cards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' },
          gap: 3,
          mb: 4,
        }}
      >
        {/* Total Members */}
        <Card sx={{ 
          boxShadow: 2, 
          borderRadius: 2,
          bgcolor: 'white',
          border: '1px solid',
          borderColor: 'divider',
          transition: 'all 0.2s ease',
          '&:hover': {
            boxShadow: 3,
            transform: 'translateY(-2px)',
          },
        }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase' }}>
                  Total Members
                </Typography>
                <Typography variant="h3" sx={{ fontWeight: 700, mt: 1, color: '#1976d2' }}>
                  {teamMembers.length}
                </Typography>
              </Box>
              <Avatar sx={{ bgcolor: '#e3f2fd', color: '#1976d2', width: 56, height: 56 }}>
                <Psychology sx={{ fontSize: 28 }} />
              </Avatar>
            </Box>
          </CardContent>
        </Card>

        {/* Exhausted Members */}
        <Card sx={{ 
          boxShadow: 2, 
          borderRadius: 2,
          bgcolor: 'white',
          border: '1px solid',
          borderColor: exhaustedMembers > 0 ? '#c0392b' : 'divider',
          transition: 'all 0.2s ease',
          '&:hover': {
            boxShadow: 3,
            transform: 'translateY(-2px)',
          },
        }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase' }}>
                  Exhausted Members
                </Typography>
                <Typography variant="h3" sx={{ 
                  fontWeight: 700, 
                  mt: 1, 
                  color: exhaustedMembers > 0 ? '#c0392b' : '#27ae60' 
                }}>
                  {exhaustedMembers}
                </Typography>
              </Box>
              <Avatar sx={{ 
                bgcolor: exhaustedMembers > 0 ? '#ffebee' : '#e8f5e9', 
                color: exhaustedMembers > 0 ? '#c0392b' : '#27ae60', 
                width: 56, 
                height: 56 
              }}>
                <Warning sx={{ fontSize: 28 }} />
              </Avatar>
            </Box>
          </CardContent>
        </Card>

        {/* High Stress */}
        <Card sx={{ 
          boxShadow: 2, 
          borderRadius: 2,
          bgcolor: 'white',
          border: '1px solid',
          borderColor: highStressMembers > 0 ? '#e67e22' : 'divider',
          transition: 'all 0.2s ease',
          '&:hover': {
            boxShadow: 3,
            transform: 'translateY(-2px)',
          },
        }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase' }}>
                  High Stress
                </Typography>
                <Typography variant="h3" sx={{ 
                  fontWeight: 700, 
                  mt: 1, 
                  color: highStressMembers > 0 ? '#e67e22' : '#27ae60' 
                }}>
                  {highStressMembers}
                </Typography>
              </Box>
              <Avatar sx={{ 
                bgcolor: highStressMembers > 0 ? '#fff3e0' : '#e8f5e9', 
                color: highStressMembers > 0 ? '#e67e22' : '#27ae60', 
                width: 56, 
                height: 56 
              }}>
                <FitnessCenter sx={{ fontSize: 28 }} />
              </Avatar>
            </Box>
          </CardContent>
        </Card>

        {/* Task Completion */}
        <Card sx={{ 
          boxShadow: 2, 
          borderRadius: 2,
          bgcolor: 'white',
          border: '1px solid',
          borderColor: 'divider',
          transition: 'all 0.2s ease',
          '&:hover': {
            boxShadow: 3,
            transform: 'translateY(-2px)',
          },
        }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase' }}>
                  Avg Task Completion
                </Typography>
                <Typography variant="h3" sx={{ fontWeight: 700, mt: 1, color: '#27ae60' }}>
                  {avgTaskCompletion}%
                </Typography>
              </Box>
              <Avatar sx={{ bgcolor: '#e8f5e9', color: '#27ae60', width: 56, height: 56 }}>
                <Assignment sx={{ fontSize: 28 }} />
              </Avatar>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Team Members List */}
      <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
        Team Members Details
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {teamMembers.map((member) => {
          const wellbeingStatus = getWellbeingStatus(member.wellbeingScore);
          
          return (
            <Paper
              key={member.id}
              onClick={() => onViewMember(member.firebaseId)}
              sx={{
                p: 3,
                borderRadius: 2,
                boxShadow: 2,
                transition: 'all 0.3s ease',
                borderLeft: `4px solid ${member.isExhausted ? '#a93226' : '#1e7e45'}`,
                cursor: 'pointer',
                '&:hover': {
                  boxShadow: 4,
                  transform: 'translateY(-2px)',
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                {/* Avatar */}
                <Avatar
                  sx={{
                    width: 60,
                    height: 60,
                    bgcolor: member.isExhausted ? '#e74c3c' : '#3498db',
                    fontSize: 24,
                  }}
                >
                  {member.name.charAt(0)}
                </Avatar>

                {/* Member Info */}
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {member.name}
                    </Typography>
                    
                    {member.isExhausted && (
                      <Chip
                        icon={<Warning sx={{ fontSize: 16 }} />}
                        label="Exhausted"
                        size="small"
                        sx={{
                          bgcolor: '#e74c3c',
                          color: 'white',
                          fontWeight: 600,
                        }}
                      />
                    )}
                    
                    <Chip
                      label={`Stress: ${member.stressLevel.toUpperCase()}`}
                      size="small"
                      sx={{
                        bgcolor: getStressColor(member.stressLevel) + '20',
                        color: getStressColor(member.stressLevel),
                        fontWeight: 600,
                      }}
                    />

                    {member.trend === 'up' && (
                      <TrendingUp sx={{ color: '#2ecc71', fontSize: 20 }} />
                    )}
                    {member.trend === 'down' && (
                      <TrendingDown sx={{ color: '#e74c3c', fontSize: 20 }} />
                    )}
                  </Box>

                  <Typography variant="body2" sx={{ color: '#7f8c8d', mb: 2 }}>
                    {member.email} • Last active: {member.lastActive}
                  </Typography>

                  {/* Colleague Feedback */}
                  <Box sx={{ mb: 2, p: 1.5, bgcolor: '#f8f9fa', borderRadius: 1 }}>
                    <Typography variant="caption" sx={{ fontWeight: 700, color: '#7f8c8d', mb: 1, display: 'block' }}>
                      Colleague Feedback {member.colleagueVotes && member.colleagueVotes.totalVoters > 0 
                        ? `(${member.colleagueVotes.totalVoters} ${member.colleagueVotes.totalVoters === 1 ? 'vote' : 'votes'})`
                        : '(No votes yet)'}
                    </Typography>
                    {member.colleagueVotes && member.colleagueVotes.totalVoters > 0 ? (
                      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                        <Chip
                          label={`${member.colleagueVotes.burnoutYes} feel burnt out`}
                          size="small"
                          sx={{
                            bgcolor: member.colleagueVotes.burnoutYes > 0 ? '#e74c3c15' : '#ecf0f1',
                            color: member.colleagueVotes.burnoutYes > 0 ? '#e74c3c' : '#7f8c8d',
                            fontWeight: 600,
                            fontSize: '0.7rem',
                          }}
                        />
                        <Chip
                          label={`${member.colleagueVotes.teamworkYes} say good teamwork`}
                          size="small"
                          sx={{
                            bgcolor: '#2ecc7115',
                            color: '#2ecc71',
                            fontWeight: 600,
                            fontSize: '0.7rem',
                          }}
                        />
                        <Chip
                          label={`${member.colleagueVotes.motivationYes} say motivated`}
                          size="small"
                          sx={{
                            bgcolor: '#3498db15',
                            color: '#3498db',
                            fontWeight: 600,
                            fontSize: '0.7rem',
                          }}
                        />
                      </Box>
                    ) : (
                      <Typography variant="caption" sx={{ color: '#95a5a6', fontStyle: 'italic' }}>
                        No colleague feedback submitted yet. Members can submit feedback using "How's Your Colleague?" button.
                      </Typography>
                    )}
                  </Box>

                  {/* Metrics Grid */}
                  <Box
                    sx={{
                      display: 'grid',
                      gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)', lg: 'repeat(5, 1fr)' },
                      gap: 3,
                    }}
                  >
                    {/* Task Completion */}
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="caption" sx={{ fontWeight: 600 }}>
                          Task Completion
                        </Typography>
                        <Typography variant="caption" sx={{ fontWeight: 700 }}>
                          {member.taskCompletionRate}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={member.taskCompletionRate}
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          bgcolor: '#ecf0f1',
                          '& .MuiLinearProgress-bar': {
                            bgcolor: member.taskCompletionRate >= 80 ? '#2ecc71' : '#f39c12',
                            borderRadius: 3,
                          },
                        }}
                      />
                    </Box>

                    {/* Wellbeing Score */}
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="caption" sx={{ fontWeight: 600 }}>
                          Wellbeing Score
                        </Typography>
                        <Typography variant="caption" sx={{ fontWeight: 700 }}>
                          {member.wellbeingScore}/100
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={member.wellbeingScore}
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          bgcolor: '#ecf0f1',
                          '& .MuiLinearProgress-bar': {
                            bgcolor: wellbeingStatus.color,
                            borderRadius: 3,
                          },
                        }}
                      />
                    </Box>

                    {/* Logged Hours */}
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5, alignItems: 'center' }}>
                        <Typography variant="caption" sx={{ fontWeight: 600 }}>
                          Logged Hours
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <AccessTime sx={{ fontSize: 14, color: '#7f8c8d' }} />
                          <Typography variant="caption" sx={{ fontWeight: 700 }}>
                            {member.loggedHours}h
                          </Typography>
                        </Box>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={(member.loggedHours / 45) * 100}
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          bgcolor: '#ecf0f1',
                          '& .MuiLinearProgress-bar': {
                            bgcolor: member.loggedHours > 44 ? '#e74c3c' : '#3498db',
                            borderRadius: 3,
                          },
                        }}
                      />
                    </Box>

                    {/* Burnout Risk */}
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="caption" sx={{ fontWeight: 600 }}>
                          Burnout Risk
                        </Typography>
                        <Typography variant="caption" sx={{ fontWeight: 700 }}>
                          {member.burnoutRisk ? `${member.burnoutRisk.toFixed(1)}%` : 'N/A'}
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={member.burnoutRisk || 0}
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          bgcolor: '#ecf0f1',
                          '& .MuiLinearProgress-bar': {
                            bgcolor: (member.burnoutRisk || 0) > 60 ? '#e74c3c' : (member.burnoutRisk || 0) > 30 ? '#f39c12' : '#2ecc71',
                            borderRadius: 3,
                          },
                        }}
                      />
                    </Box>

                    {/* Efficiency */}
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="caption" sx={{ fontWeight: 600 }}>
                          Efficiency
                        </Typography>
                        <Typography variant="caption" sx={{ fontWeight: 700 }}>
                          {member.efficiency ? `${member.efficiency}/100` : 'N/A'}
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={member.efficiency || 0}
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          bgcolor: '#ecf0f1',
                          '& .MuiLinearProgress-bar': {
                            bgcolor: (member.efficiency || 0) >= 80 ? '#2ecc71' : (member.efficiency || 0) >= 60 ? '#3498db' : '#f39c12',
                            borderRadius: 3,
                          },
                        }}
                      />
                    </Box>
                  </Box>
                </Box>
              </Box>
            </Paper>
          );
        })}
      </Box>
    </Box>
  );
};
