import React, { useState } from 'react';
import { Button } from 'internal-packages-ui';
import { authEndpoints } from '../../utils/api';
import { authStorage } from '../../utils/auth';

export function LogoutButton({
  onSuccess,
  variant = 'secondary',
  className = '',
  children = 'Logout'
}) {
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);

    try {
      // Call logout endpoint
      await authEndpoints.logout();
    } catch (error) {
      // Even if API call fails, still clear local tokens
      console.error('Logout error:', error);
    } finally {
      // Clear stored tokens and user data
      authStorage.clear();

      // Call success callback if provided
      if (onSuccess) {
        onSuccess();
      } else {
        // Redirect to login page
        window.location.href = '/login';
      }

      setIsLoggingOut(false);
    }
  };

  return (
    <Button
      onClick={handleLogout}
      variant={variant}
      className={className}
      disabled={isLoggingOut}
    >
      {isLoggingOut ? 'Logging out...' : children}
    </Button>
  );
}
