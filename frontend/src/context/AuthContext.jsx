import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('gymtrac_token') || null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Verify token on load
      api.get('/api/auth/me')
        .then(res => {
          setUser(res.data.user);
        })
        .catch(() => {
          // Token invalid — clear it
          localStorage.removeItem('gymtrac_token');
          setToken(null);
          delete api.defaults.headers.common['Authorization'];
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (username, password) => {
    const res = await api.post('/api/auth/login', { username, password });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('gymtrac_token', access_token);
    setToken(access_token);
    setUser(userData);
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    return userData;
  };

  const signup = async (data) => {
    const res = await api.post('/api/auth/register', data);
    const { user: userData } = res.data;
    return userData;
  };

  const logout = async () => {
    try {
      await api.post('/api/auth/logout');
    } catch (_) {
      // ignore — client-side logout is the important part
    }
    localStorage.removeItem('gymtrac_token');
    setToken(null);
    setUser(null);
    delete api.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!user,
    login,
    signup,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
