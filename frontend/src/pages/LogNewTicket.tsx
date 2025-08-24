import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const LogNewTicket = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [machineId, setMachineId] = useState('');
  const [incidentCategory, setIncidentCategory] = useState('');
  const [description, setDescription] = useState('');

  const createTicketMutation = useMutation({
    mutationFn: async (newTicket: { machine_id: string; incident_category: string; description: string }) => {
      const response = await apiClient.post('/api/v1/tickets/', newTicket);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenanceTickets'] }); // Invalidate tickets list to refetch
      toast({
        title: "Ticket Created",
        description: "New maintenance ticket logged successfully.",
      });
      // Clear form
      setMachineId('');
      setIncidentCategory('');
      setDescription('');
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to log ticket.",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createTicketMutation.mutate({ machine_id: machineId, incident_category: incidentCategory, description });
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Log New Maintenance Ticket</h1>

      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle>Create New Ticket</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="machineId">Machine ID</Label>
              <Input
                id="machineId"
                type="text"
                value={machineId}
                onChange={(e) => setMachineId(e.target.value)}
                required
              />
            </div>
            <div>
              <Label htmlFor="incidentCategory">Incident Category</Label>
              <Select onValueChange={setIncidentCategory} value={incidentCategory} required>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Mechanical">Mechanical</SelectItem>
                  <SelectItem value="Electrical">Electrical</SelectItem>
                  <SelectItem value="Software">Software</SelectItem>
                  <SelectItem value="Other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
                rows={5}
              />
            </div>
            <Button type="submit" className="w-full" disabled={createTicketMutation.isPending}>
              {createTicketMutation.isPending ? 'Logging...' : 'Log Ticket'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default LogNewTicket;