import React from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
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

const MaintenanceHub = () => {
  const { data: tickets, isLoading, error } = useQuery<MaintenanceTicket[]>({ 
    queryKey: ['maintenanceTickets'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/tickets/');
      return response.data;
    },
  });

  if (isLoading) {
    return <div className="p-4">Loading maintenance tickets...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">Error loading tickets: {error.message}</div>;
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Maintenance Hub</h1>

      <Card>
        <CardHeader>
          <CardTitle>All Maintenance Tickets</CardTitle>
        </CardHeader>
        <CardContent>
          {tickets && tickets.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Machine ID</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Logged Time</TableHead>
                  <TableHead>Resolved Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tickets.map((ticket) => (
                  <TableRow key={ticket.id}>
                    <TableCell>{ticket.id}</TableCell>
                    <TableCell>{ticket.machine_id}</TableCell>
                    <TableCell>{ticket.incident_category}</TableCell>
                    <TableCell>{ticket.description}</TableCell>
                    <TableCell>{ticket.status}</TableCell>
                    <TableCell>{format(new Date(ticket.logged_time), 'PPP p')}</TableCell>
                    <TableCell>
                      {ticket.resolved_time 
                        ? format(new Date(ticket.resolved_time), 'PPP p') 
                        : 'N/A'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p>No maintenance tickets found.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default MaintenanceHub;