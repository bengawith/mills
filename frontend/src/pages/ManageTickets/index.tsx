import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getMaintenanceTickets } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { MACHINE_ID_MAP } from '@/lib/constants';
import TicketDetailView from './TicketDetailView';

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
  const [selectedTicketId, setSelectedTicketId] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState('Open');

  const { data: tickets, isLoading, error } = useQuery<MaintenanceTicket[]>({ 
    queryKey: ['maintenanceTickets', statusFilter],
    queryFn: () => getMaintenanceTickets(statusFilter),
  });

  if (isLoading) {
    return <div className="p-4">Loading tickets...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">Error loading tickets: {error.message}</div>;
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Manage Maintenance Tickets</h1>

      <div className="flex justify-between items-center mb-4">
        <ToggleGroup type="single" value={statusFilter} onValueChange={(value) => setStatusFilter(value || 'Open')} defaultValue="Open">
          <ToggleGroupItem value="Open">Open</ToggleGroupItem>
          <ToggleGroupItem value="Resolved">Resolved</ToggleGroupItem>
        </ToggleGroup>
      </div>

      <Card className="w-full max-w-2xl mb-6">
        <CardHeader>
          <CardTitle>Select a Ticket to Manage</CardTitle>
        </CardHeader>
        <CardContent>
          {tickets && tickets.length > 0 ? (
            <Select onValueChange={setSelectedTicketId} value={selectedTicketId}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder={`Choose a ${statusFilter.toLowerCase()} ticket`} />
              </SelectTrigger>
              <SelectContent>
                {tickets.map(ticket => (
                  <SelectItem key={ticket.id} value={String(ticket.id)}>
                    #{ticket.id} - {MACHINE_ID_MAP[ticket.machine_id] || ticket.machine_id} - {ticket.description.substring(0, 50)}...
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : (
            <p className="text-green-600">🎉 No {statusFilter.toLowerCase()} maintenance tickets!</p>
          )}
        </CardContent>
      </Card>

      {selectedTicketId && <TicketDetailView ticketId={parseInt(selectedTicketId)} />}
    </div>
  );
};

export default ManageTickets;
