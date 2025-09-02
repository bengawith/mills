/*
  ManageTickets.tsx - MillDash Frontend Maintenance Ticket Management Page

  This file implements the maintenance ticket management interface for MillDash using React and TypeScript. It allows users to view details of a specific maintenance ticket and update its status. The component integrates with the backend API using React Query for efficient data fetching and mutation, and provides user feedback via toast notifications.

  Key Features:
  - Uses React functional component with hooks for state management (selected ticket ID, new status).
  - Integrates React Query for fetching ticket details and updating ticket status.
  - Displays ticket details including machine, category, description, status, and timestamps.
  - Provides a dropdown for status updates and a button to submit changes.
  - Handles loading and error states gracefully.
  - Utilizes custom UI components for consistent styling (Card, Input, Button, Label, Select).
  - Responsive and user-friendly layout using Tailwind CSS utility classes.
  - All functions and state variables are explicitly typed for type safety.
*/

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { format } from 'date-fns';

interface MaintenanceTicket {
  id: number;
  machine_id: string;
  incident_category: string;
  description: string;
  status: string;
  logged_time: string;
  resolved_time: string | null;
}

const ManageTickets = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [selectedTicketId, setSelectedTicketId] = useState<string>('');
  const [newStatus, setNewStatus] = useState<string>('');

  // Query to fetch ticket details based on selectedTicketId
  const { data: ticket, isLoading, error } = useQuery<MaintenanceTicket>({
    queryKey: ['maintenanceTicket', selectedTicketId],
    queryFn: async () => {
      if (!selectedTicketId) return Promise.reject('No ticket ID provided');
      const response = await apiClient.get(`/api/v1/tickets/${selectedTicketId}`);
      return response.data;
    },
    enabled: !!selectedTicketId, // Only run query if selectedTicketId is available
  });

  // Mutation to update the status of a ticket
  /**
   * Mutation for updating the status of a maintenance ticket.
   * On success, invalidates relevant queries and shows a success toast.
   * On error, displays an error toast with details.
   */
  const updateTicketStatusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: number; status: string }): Promise<any> => {
      const response = await apiClient.put(`/api/v1/tickets/${id}`, null, { params: { status } });
      return response.data;
    },
    onSuccess: () => {
      // Invalidate queries to refetch ticket and tickets list
      queryClient.invalidateQueries({ queryKey: ['maintenanceTicket', selectedTicketId] });
      queryClient.invalidateQueries({ queryKey: ['maintenanceTickets'] }); // Invalidate list as well
      toast({
        title: "Ticket Status Updated",
        description: "Ticket status updated successfully.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to update ticket status.",
        variant: "destructive",
      });
    },
  });

  // Handler to update ticket status
  /**
   * Handles the status update action when the user clicks the update button.
   * Triggers the mutation to update the ticket status in the backend.
   */
  const handleStatusUpdate = (): void => {
    if (ticket && newStatus) {
      updateTicketStatusMutation.mutate({ id: ticket.id, status: newStatus });
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Manage Maintenance Tickets</h1>

      <Card className="w-full max-w-lg mb-6">
        <CardHeader>
          <CardTitle>Select Ticket</CardTitle>
        </CardHeader>
        <CardContent>
          <Label htmlFor="ticketId">Ticket ID</Label>
          <Input
            id="ticketId"
            type="number"
            value={selectedTicketId}
            onChange={(e) => setSelectedTicketId(e.target.value)}
            placeholder="Enter Ticket ID"
          />
        </CardContent>
      </Card>

      {isLoading && selectedTicketId && <div className="p-4">Loading ticket details...</div>}
      {error && selectedTicketId && <div className="p-4 text-red-500">Error loading ticket: {error.message}</div>}

      {ticket && (
        <Card className="w-full max-w-lg">
          <CardHeader>
            <CardTitle>Ticket Details (ID: {ticket.id})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p><strong>Machine ID:</strong> {ticket.machine_id}</p>
              <p><strong>Category:</strong> {ticket.incident_category}</p>
              <p><strong>Description:</strong> {ticket.description}</p>
              <p><strong>Status:</strong> {ticket.status}</p>
              <p><strong>Logged Time:</strong> {format(new Date(ticket.logged_time), 'PPP p')}</p>
              <p><strong>Resolved Time:</strong> {ticket.resolved_time ? format(new Date(ticket.resolved_time), 'PPP p') : 'N/A'}</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="newStatus">Update Status</Label>
              <Select onValueChange={setNewStatus} value={newStatus}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select new status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Open">Open</SelectItem>
                  <SelectItem value="In Progress">In Progress</SelectItem>
                  <SelectItem value="Resolved">Resolved</SelectItem>
                  <SelectItem value="Closed">Closed</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={handleStatusUpdate} className="w-full" disabled={updateTicketStatusMutation.isPending || !newStatus}>
                {updateTicketStatusMutation.isPending ? 'Updating...' : 'Update Status'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ManageTickets;