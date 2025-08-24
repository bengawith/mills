import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import apiClient from '@/lib/api';

const CompleteProfilePage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [taxCode, setTaxCode] = useState('');
  const [niNumber, setNiNumber] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.put('/api/my-profile/', {
        tax_code: taxCode,
        ni_number: niNumber,
        onboarded: true,
      });

      toast({
        title: 'Profile Updated',
        description: 'Your profile has been successfully updated.',
      });
      logout();
      navigate('/login');
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to update profile.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  if (!user || user.role !== 'EMPLOYEE') {
    navigate('/login');
    return null;
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl">Complete Your Profile</CardTitle>
          <CardDescription>
            Please provide your Tax Code and National Insurance Number to complete your profile.
            This information is securely encrypted.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="taxCode">Tax Code</Label>
              <Input
                id="taxCode"
                type="text"
                value={taxCode}
                onChange={(e) => setTaxCode(e.target.value)}
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                Your tax code can be found on your payslip or P45/P60.
              </p>
            </div>
            <div>
              <Label htmlFor="niNumber">National Insurance Number</Label>
              <Input
                id="niNumber"
                type="text"
                value={niNumber}
                onChange={(e) => setNiNumber(e.target.value)}
                maxLength={9}
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                Your NI number is a unique personal number. Example: QQ123456C.
                <a
                  href="https://www.gov.uk/national-insurance-number"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline ml-1"
                >
                  Find out more on GOV.UK
                </a>
              </p>
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Saving...' : 'Complete Profile'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default CompleteProfilePage;