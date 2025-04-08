import { useEffect, useState } from 'react';
import { getBaseURL } from '../../store/useAPIStore';
import { useNavigate } from 'react-router-dom';

export const useUser = () => {
  const [user, setUser] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await fetch(`${getBaseURL()}/api/auth/me`, {
          credentials: 'include',
          headers: {
            Accept: 'application,json',
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch user');
        }

        const data = await response.json();
        setUser(data.email);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, []);

  const loginWithGithub = () => {
    window.location.href = `${getBaseURL()}/api/auth/login/github`;
  };

  const logout = async () => {
    try {
      await fetch(`${getBaseURL()}/api/auth/logout`, {
        method: 'GET',
        credentials: 'include',
      });
      setUser(null);
      window.location.href = '/login'; 
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  return { user, isLoading, error, loginWithGithub, logout };
};
