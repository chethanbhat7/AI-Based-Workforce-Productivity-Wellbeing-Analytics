import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  RadioGroup,
  FormControlLabel,
  Radio,
  Divider,
  Alert,
  CircularProgress,
} from '@mui/material';
import { CheckCircle, Cancel, Close } from '@mui/icons-material';
import { collection, query, where, getDocs, addDoc } from 'firebase/firestore';
import { db } from '../firebase/config';
import { useAuth } from '../context/AuthContext';

interface ColleagueCheckDialogProps {
  open: boolean;
  onClose: () => void;
}

interface Colleague {
  id: string;
  name: string;
  email: string;
}

interface Question {
  id: string;
  text: string;
}

interface Vote {
  colleagueId: string;
  questionId: string;
  answer: 'yes' | 'no' | null;
}

const QUESTIONS: Question[] = [
  { id: 'burnout', text: 'Does this colleague seem burnt out?' },
  { id: 'teamwork', text: 'Is this colleague working well with the team?' },
  { id: 'motivation', text: 'Does this colleague seem motivated?' },
];

export const ColleagueCheckDialog = ({ open, onClose }: ColleagueCheckDialogProps) => {
  const { user } = useAuth();
  const [colleagues, setColleagues] = useState<Colleague[]>([]);
  const [votes, setVotes] = useState<Vote[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && user) {
      fetchColleagues();
    }
  }, [open, user]);

  const fetchColleagues = async () => {
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      // Fetch team members (excluding the current user)
      const usersRef = collection(db, 'users');
      const q = query(
        usersRef,
        where('role', '==', 'member')
      );
      
      const querySnapshot = await getDocs(q);
      const fetchedColleagues: Colleague[] = [];
      
      querySnapshot.forEach((doc) => {
        const data = doc.data();
        // Exclude current user
        if (doc.id !== user.id) {
          fetchedColleagues.push({
            id: doc.id,
            name: data.name || 'Unknown',
            email: data.email || '',
          });
        }
      });

      // Fetch voting history to see who this user has already reviewed
      const votesRef = collection(db, 'colleague_votes');
      const voterQuery = query(votesRef, where('voterId', '==', user.id));
      const votesSnapshot = await getDocs(voterQuery);
      
      const reviewedColleagueIds = new Set<string>();
      votesSnapshot.forEach((doc) => {
        reviewedColleagueIds.add(doc.data().colleagueId);
      });

      // Separate colleagues into reviewed and not reviewed
      const notReviewed = fetchedColleagues.filter(c => !reviewedColleagueIds.has(c.id));
      const reviewed = fetchedColleagues.filter(c => reviewedColleagueIds.has(c.id));

      // Prioritize colleagues who haven't been reviewed yet
      let selected: Colleague[] = [];
      
      if (notReviewed.length >= 5) {
        // If we have 5+ unreviewed colleagues, randomly pick 5 from them
        const shuffled = notReviewed.sort(() => 0.5 - Math.random());
        selected = shuffled.slice(0, 5);
      } else {
        // Otherwise, take all unreviewed and fill the rest with reviewed (shuffled for fairness)
        const shuffledReviewed = reviewed.sort(() => 0.5 - Math.random());
        selected = [...notReviewed, ...shuffledReviewed].slice(0, 5);
      }
      
      setColleagues(selected);

      // Initialize votes
      const initialVotes: Vote[] = [];
      selected.forEach(colleague => {
        QUESTIONS.forEach(question => {
          initialVotes.push({
            colleagueId: colleague.id,
            questionId: question.id,
            answer: null,
          });
        });
      });
      setVotes(initialVotes);

    } catch (err) {
      console.error('Error fetching colleagues:', err);
      setError('Failed to load colleagues. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleVoteChange = (colleagueId: string, questionId: string, answer: 'yes' | 'no') => {
    setVotes(prev => 
      prev.map(vote => 
        vote.colleagueId === colleagueId && vote.questionId === questionId
          ? { ...vote, answer }
          : vote
      )
    );
  };

  const getVote = (colleagueId: string, questionId: string): 'yes' | 'no' | null => {
    const vote = votes.find(v => v.colleagueId === colleagueId && v.questionId === questionId);
    return vote?.answer || null;
  };

  const handleSubmit = async () => {
    if (!user) return;

    setSubmitting(true);
    setError(null);

    try {
      // Save votes to Firestore
      const votesRef = collection(db, 'colleague_votes');
      const timestamp = new Date().toISOString();

      // Group votes by colleague for efficient storage
      for (const colleague of colleagues) {
        const colleagueVotes: { [key: string]: string } = {};
        
        QUESTIONS.forEach(question => {
          const vote = getVote(colleague.id, question.id);
          if (vote) {
            colleagueVotes[question.id] = vote;
          }
        });

        // Only save if at least one question was answered
        if (Object.keys(colleagueVotes).length > 0) {
          await addDoc(votesRef, {
            voterId: user.id, // Store voter ID but won't be shown to supervisor
            colleagueId: colleague.id,
            colleagueName: colleague.name,
            votes: colleagueVotes,
            timestamp: timestamp,
            teamNumber: (user as any).teamNumber || '1',
          });
        }
      }

      // Close dialog
      handleClose();
    } catch (err) {
      console.error('Error submitting votes:', err);
      setError('Failed to submit votes. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setVotes([]);
    setColleagues([]);
    setError(null);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      TransitionProps={{
        timeout: 400,
      }}
      PaperProps={{
        sx: {
          borderRadius: 2,
          boxShadow: 3,
          animation: 'slideIn 0.4s ease-out',
        },
      }}
      sx={{
        '@keyframes slideIn': {
          '0%': {
            opacity: 0,
            transform: 'translateY(-30px) scale(0.95)',
          },
          '100%': {
            opacity: 1,
            transform: 'translateY(0) scale(1)',
          },
        },
      }}
    >
      <DialogTitle sx={{ pb: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6" sx={{ fontWeight: 700 }}>
          How's Your Colleague?
        </Typography>
        <Button
          onClick={handleClose}
          sx={{ minWidth: 'auto', p: 0.5, color: 'text.secondary' }}
        >
          <Close />
        </Button>
      </DialogTitle>

      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : colleagues.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body1" color="text.secondary">
              No colleagues available for feedback.
            </Typography>
          </Box>
        ) : (
          <>
            <Alert severity="info" sx={{ mb: 3 }}>
              Your responses are anonymous and will help supervisors understand team wellbeing.
            </Alert>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {colleagues.map((colleague, index) => (
                <Box key={colleague.id}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2 }}>
                    {colleague.name}
                  </Typography>

                  {QUESTIONS.map((question) => (
                    <Box key={question.id} sx={{ mb: 2 }}>
                      <Typography variant="body2" sx={{ mb: 1, color: 'text.secondary' }}>
                        {question.text}
                      </Typography>
                      <RadioGroup
                        row
                        value={getVote(colleague.id, question.id) || ''}
                        onChange={(e) =>
                          handleVoteChange(colleague.id, question.id, e.target.value as 'yes' | 'no')
                        }
                      >
                        <FormControlLabel
                          value="yes"
                          control={<Radio size="small" />}
                          label={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                              <CheckCircle sx={{ fontSize: 18, color: '#2ecc71' }} />
                              <Typography variant="body2">Yes</Typography>
                            </Box>
                          }
                        />
                        <FormControlLabel
                          value="no"
                          control={<Radio size="small" />}
                          label={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                              <Cancel sx={{ fontSize: 18, color: '#e74c3c' }} />
                              <Typography variant="body2">No</Typography>
                            </Box>
                          }
                        />
                      </RadioGroup>
                    </Box>
                  ))}

                  {index < colleagues.length - 1 && <Divider sx={{ mt: 2 }} />}
                </Box>
              ))}
            </Box>
          </>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={handleClose} disabled={submitting}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading || submitting || colleagues.length === 0}
          sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #5568d3 0%, #63408a 100%)',
            },
          }}
        >
          {submitting ? <CircularProgress size={24} /> : 'Submit Feedback'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
