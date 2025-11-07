/**
 * Generate consistent dummy/placeholder values based on email hash
 * This ensures the same email always gets the same values across all views
 */

export const generateConsistentValue = (email: string, seed: number, min: number, max: number): number => {
  let hash = 0;
  const str = email + seed.toString();
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash = hash & hash; // Convert to 32bit integer
  }
  return min + (Math.abs(hash) % (max - min + 1));
};

/**
 * TEST SCENARIOS FOR BURNOUT FEATURE TESTING
 * Assign specific values based on email to test different conditions
 * 
 * BURNOUT THRESHOLD: 70%
 * OVERTIME ALERT: 3+ times per week
 */
export const getTestScenarioValues = (email: string) => {
  const lowerEmail = email.toLowerCase();
  
  // Scenario 1: CRITICAL - High burnout (75%) + 3 overtimes → Email to supervisor
  if (lowerEmail.includes('member1') || lowerEmail.includes('burnout')) {
    return {
      wellbeingScore: 45,        // Low wellbeing
      stressLevel: 'high' as const,
      taskCompletionRate: 55,
      isExhausted: true,
      meetingHours: 18,          // High meeting hours
      overtimeCount: 3,          // 3rd overtime → triggers email
    };
  }
  
  // Scenario 2: SAFE - Healthy member, good performance
  if (lowerEmail.includes('member2') || lowerEmail.includes('helper')) {
    return {
      wellbeingScore: 85,        // High wellbeing
      stressLevel: 'low' as const,
      taskCompletionRate: 92,
      isExhausted: false,
      meetingHours: 10,
      overtimeCount: 1,          // Safe overtime level
    };
  }
  
  // Scenario 3: MODERATE - Approaching threshold (68% burnout)
  if (lowerEmail.includes('member3') || lowerEmail.includes('struggling')) {
    return {
      wellbeingScore: 68,
      stressLevel: 'medium' as const,
      taskCompletionRate: 65,
      isExhausted: false,
      meetingHours: 14,
      overtimeCount: 2,          // Close to overtime limit
    };
  }
  
  // Scenario 4: SAFE - Productive and healthy
  if (lowerEmail.includes('member4') || lowerEmail.includes('productive')) {
    return {
      wellbeingScore: 78,
      stressLevel: 'low' as const,
      taskCompletionRate: 88,
      isExhausted: false,
      meetingHours: 12,
      overtimeCount: 0,          // No overtime
    };
  }
  
  // Scenario 5: CRITICAL - High burnout (75%) + excessive overtime (4) → Email to supervisor
  if (lowerEmail.includes('member5') || lowerEmail.includes('stressed')) {
    return {
      wellbeingScore: 55,        // Low wellbeing
      stressLevel: 'high' as const,
      taskCompletionRate: 82,
      isExhausted: true,
      meetingHours: 16,          // High meeting hours
      overtimeCount: 4,          // Excessive overtime → triggers email
    };
  }
  
  // Default: Use hash-based generation for other emails
  return null;
};

export const getConsistentStressLevel = (email: string): 'low' | 'medium' | 'high' => {
  // Check if there's a test scenario first
  const scenario = getTestScenarioValues(email);
  if (scenario) return scenario.stressLevel;
  
  const levels: ('low' | 'medium' | 'high')[] = ['low', 'medium', 'high'];
  const index = generateConsistentValue(email, 999, 0, 2);
  return levels[index];
};

export const getConsistentTrend = (email: string): 'up' | 'down' | 'stable' => {
  const trends: ('up' | 'down' | 'stable')[] = ['up', 'down', 'stable'];
  const index = generateConsistentValue(email, 888, 0, 2);
  return trends[index];
};

export const getConsistentLastActive = (email: string): string => {
  const times = ['Just now', '15 minutes ago', '1 hour ago', '2 hours ago'];
  const index = generateConsistentValue(email, 777, 0, 3);
  return times[index];
};

/**
 * Seed values for consistent generation across application
 * Using different seeds ensures different metrics have different values
 */
export const SEEDS = {
  TASK_COMPLETION: 1,
  LOGGED_HOURS: 2,
  WELLBEING_SCORE: 3,
  IS_EXHAUSTED: 4,
  MEETING_HOURS: 5,
  MEETING_COUNT: 6,
  MESSAGES_SENT: 7,
  MESSAGES_RECEIVED: 8,
  EARLY_STARTS: 9,
  LATE_EXITS: 10,
  LATE_STARTS: 11,
  EARLY_EXITS: 12,
};
