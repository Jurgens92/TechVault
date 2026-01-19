import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useOrganization } from '@/contexts/OrganizationContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, loading: authLoading, user } = useAuth();
  const { loading: orgLoading } = useOrganization();

  // Show loading spinner while auth is loading, or while orgs are loading for authenticated users
  if (authLoading || (isAuthenticated && orgLoading)) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Redirect to 2FA setup if user doesn't have 2FA enabled
  if (user && !user.twofa_enabled) {
    return <Navigate to="/setup-2fa" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
