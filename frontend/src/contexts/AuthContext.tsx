import { createContext, useState, useEffect, ReactNode, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../lib/api';

interface AuthProviderProps {
  children: ReactNode;
}

interface User {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'ADMIN' | 'EMPLOYEE';
  onboarded: boolean;
}

interface LoginData {
  email: string;
  password: string;
}

interface AuthContextType {
  user: User | null;
  login: (data: LoginData) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const userResponse = await apiClient.get('/auth/users/me/');
          const fetchedUser: User = userResponse.data;
          setUser(fetchedUser);
          setIsAuthenticated(true);

          if (fetchedUser.role.toUpperCase() === 'EMPLOYEE' && !fetchedUser.onboarded) {
            navigate('/complete-profile');
          }
        } catch (error: any) {
          console.error("Failed to fetch user data:", error.response?.data?.detail || error.message);
          logout();
        }
      }
      setLoading(false);
    };
    loadUser();
  }, [navigate]);

  const login = async (data: LoginData) => {
    const response = await apiClient.post('/auth/token', data);
    const { access_token, refresh_token } = response.data;

    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);

    // Directly use the received access token for the immediate user data fetch
    const userResponse = await apiClient.get('/auth/users/me/', {
      headers: {
        Authorization: `Bearer ${access_token}`,
      },
    });
    const fetchedUser: User = userResponse.data;

    setUser(fetchedUser);
    setIsAuthenticated(true);

    if (fetchedUser.role.toUpperCase() === 'ADMIN') {
      navigate('/admin');
    } else if (fetchedUser.role.toUpperCase() === 'EMPLOYEE') {
      if (!fetchedUser.onboarded) {
        navigate('/complete-profile');
      } else {
        navigate('/employee');
      }
    } else {
      navigate('/');
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setIsAuthenticated(false);
    navigate('/');
  };

  if (loading) {
    return null; // Or a loading spinner
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};