import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import apiClient from '@/lib/api';

const CompleteProfilePage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.patch('/api/v1/users/me', {
        onboarded: true,
      });

      toast({
        title: 'Profile Confirmed',
        description: 'Your profile has been confirmed. Welcome to Mill Dash!',
      });
      
      // After successful update, refresh user data in AuthContext
      // This assumes AuthContext has a mechanism to re-fetch user data
      // For now, we'll just navigate, but a proper refresh would be better.
      // A full refresh of the user object in AuthContext would typically involve
      // re-calling the /auth/users/me endpoint and updating the user state.
      // For simplicity in this step, we navigate, which will trigger AuthContext's
      // loadUser effect on the next page load.

      if (user?.role.toUpperCase() === 'ADMIN') {
        navigate('/dashboard');
      } else if (user?.role.toUpperCase() === 'EMPLOYEE') {
        navigate('/dashboard');
      } else {
        navigate('/');
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to confirm profile.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    navigate('/login');
    return null;
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl">Complete Your Profile</CardTitle>
          <CardDescription>
            Please confirm your profile details to get started with Mill Dash.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <p className="text-center text-muted-foreground">
              Click the button below to confirm your account setup and proceed to the application.
            </p>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Confirming...' : 'Complete Profile'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default CompleteProfilePage;