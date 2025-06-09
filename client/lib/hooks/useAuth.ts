'use client';

import { useAuth as useClerkAuth } from '@clerk/nextjs';
import { useEffect } from 'react';
import { apiClient } from '../api';

export function useAuth() {
  const { getToken, isLoaded, isSignedIn, userId } = useClerkAuth();

  useEffect(() => {
    const updateAuthToken = async () => {
      if (isLoaded && isSignedIn) {
        try {
          const token = await getToken();
          apiClient.setAuthToken(token);
        } catch (error) {
          console.error('Failed to get auth token:', error);
          apiClient.setAuthToken(null);
        }
      } else {
        apiClient.setAuthToken(null);
      }
    };

    updateAuthToken();
  }, [isLoaded, isSignedIn, getToken]);

  return {
    isLoaded,
    isSignedIn,
    userId,
    getToken,
  };
} 