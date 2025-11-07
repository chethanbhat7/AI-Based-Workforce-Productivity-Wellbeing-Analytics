import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { onAuthStateChanged as firebaseOnAuthStateChanged } from 'firebase/auth';
import { doc, getDoc } from 'firebase/firestore';
import { auth, db } from '../firebase/config';
import { loginWithEmail, logoutUser } from '../firebase/auth';

export type UserRole = 'supervisor' | 'member';

interface AuthUser {
  id: string;
  email: string;
  role: UserRole;
  name: string;
}

interface AuthContextType {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  // Load user from localStorage and listen to Firebase auth state
  useEffect(() => {
    try {
      const savedUser = localStorage.getItem('authUser');
      if (savedUser) {
        const parsedUser = JSON.parse(savedUser);
        setUser(parsedUser);
      }
    } catch (err) {
      localStorage.removeItem('authUser');
    } finally {
      setLoading(false);
    }

    // Listen to Firebase auth state changes
    const unsubscribe = firebaseOnAuthStateChanged(auth, async (firebaseUser: any) => {
      if (firebaseUser) {
        // User is signed in with Firebase
        const savedUser = localStorage.getItem('authUser');
        if (!savedUser) {
          // Fetch user details from Firestore
          try {
            const userDocRef = doc(db, 'users', firebaseUser.uid);
            const userDoc = await getDoc(userDocRef);
            
            if (userDoc.exists()) {
              const data = userDoc.data();
              const userData = {
                id: firebaseUser.uid,
                email: data.email,
                role: data.role as UserRole,
                name: data.name,
              };
              setUser(userData);
              localStorage.setItem('authUser', JSON.stringify(userData));
            } else {
              // User document doesn't exist in Firestore, use mock data
              const mockUserData = {
                id: firebaseUser.uid,
                email: firebaseUser.email || '',
                role: (firebaseUser.email === 'supervisor@test.com' ? 'supervisor' : 'member') as UserRole,
                name: firebaseUser.email?.split('@')[0] || 'User',
              };
              setUser(mockUserData);
              localStorage.setItem('authUser', JSON.stringify(mockUserData));
            }
          } catch (error) {
            console.error('Error fetching user data:', error);
          }
        }
      } else {
        // User is signed out
        setUser(null);
        localStorage.removeItem('authUser');
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      // Authenticate with Firebase
      const firebaseUser = await loginWithEmail(email, password);
      
      // Get user details from Firestore
      let userData;
      try {
        const userDocRef = doc(db, 'users', firebaseUser.uid);
        const userDoc = await getDoc(userDocRef);
        
        if (userDoc.exists()) {
          const data = userDoc.data();
          userData = {
            id: firebaseUser.uid,
            email: data.email,
            role: data.role as UserRole,
            name: data.name,
          };
        } else {
          // User document doesn't exist in Firestore, use mock data based on email
          console.warn('User document not found in Firestore, using mock data');
          
          if (email === 'supervisor@test.com') {
            userData = {
              id: firebaseUser.uid,
              email: email,
              role: 'supervisor' as UserRole,
              name: 'Test Supervisor',
            };
          } else if (email === 'member@test.com') {
            userData = {
              id: firebaseUser.uid,
              email: email,
              role: 'member' as UserRole,
              name: 'Test Member',
            };
          } else {
            // Default to member role for unknown emails
            userData = {
              id: firebaseUser.uid,
              email: email,
              role: 'member' as UserRole,
              name: email.split('@')[0] || 'User',
            };
          }
        }
      } catch (firestoreError) {
        console.error('Error fetching from Firestore:', firestoreError);
        // Fallback to mock data
        userData = {
          id: firebaseUser.uid,
          email: email,
          role: (email === 'supervisor@test.com' ? 'supervisor' : 'member') as UserRole,
          name: email.split('@')[0] || 'User',
        };
      }

      setUser(userData);
      localStorage.setItem('authUser', JSON.stringify(userData));
    } catch (error: any) {
      setLoading(false);
      // Provide user-friendly error messages
      if (error.message?.includes('auth/wrong-password')) {
        throw new Error('Incorrect password. Please try again.');
      } else if (error.message?.includes('auth/user-not-found')) {
        throw new Error('No account found with this email.');
      } else if (error.message?.includes('auth/invalid-email')) {
        throw new Error('Invalid email address.');
      } else if (error.message?.includes('auth/configuration-not-found')) {
        throw new Error('Firebase not configured. Please check .env file.');
      } else {
        throw new Error(error.message || 'Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await logoutUser();
      setUser(null);
      localStorage.removeItem('authUser');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <AuthContext.Provider
      value={{ user, loading, login, logout, isAuthenticated: !!user }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
