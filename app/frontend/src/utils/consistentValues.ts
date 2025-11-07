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
 */
export const getTestScenarioValues = (email: string) => {
  const lowerEmail = email.toLowerCase();
  
  // Scenario 1: Burnt out member (low wellbeing, high stress, low task completion)
  if (lowerEmail.includes('member1') || lowerEmail.includes('burnout')) {
    return {
      wellbeingScore: 45,        // < 60 (burnt out)
      stressLevel: 'high' as const,
      taskCompletionRate: 55,    // < 75 (low completion)
      isExhausted: true,
    };
  }
  
  // Scenario 2: Capable helper (high wellbeing, low stress, high task completion)
  if (lowerEmail.includes('member2') || lowerEmail.includes('helper')) {
    return {
      wellbeingScore: 85,        // >= 60 (healthy)
      stressLevel: 'low' as const,
      taskCompletionRate: 92,    // > 75 (eligible to help)
      isExhausted: false,
    };
  }
  
  // Scenario 3: Struggling but not burnt out (medium wellbeing, low task completion)
  if (lowerEmail.includes('member3') || lowerEmail.includes('struggling')) {
    return {
      wellbeingScore: 68,        // >= 60 (not burnt out)
      stressLevel: 'medium' as const,
      taskCompletionRate: 65,    // < 75 (NOT eligible to help)
      isExhausted: false,
    };
  }
  
  // Scenario 4: Another capable helper
  if (lowerEmail.includes('member4') || lowerEmail.includes('productive')) {
    return {
      wellbeingScore: 78,        // >= 60 (healthy)
      stressLevel: 'low' as const,
      taskCompletionRate: 88,    // > 75 (eligible to help)
      isExhausted: false,
    };
  }
  
  // Scenario 5: High stress but good completion
  if (lowerEmail.includes('member5') || lowerEmail.includes('stressed')) {
    return {
      wellbeingScore: 55,        // < 60 (burnt out)
      stressLevel: 'high' as const,
      taskCompletionRate: 82,    // > 75 but still burnt out
      isExhausted: true,
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
