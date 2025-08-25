import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getTicketDetails, updateTicketStatus } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { MACHINE_ID_MAP } from '@/lib/constants';
import { format } from 'date-fns';
import WorkNotesSection from './WorkNotesSection';
import ImageSection from './ImageSection';
import ComponentLogSection from './ComponentLogSection';

interface TicketDetailViewProps {
  ticketId: number;
}

const TicketDetailView: React.FC<TicketDetailViewProps> = ({ ticketId }) => {
  const { data: ticket, isLoading, error, refetch } = useQuery({
    queryKey: ['ticketDetails', ticketId],
    queryFn: () => getTicketDetails(ticketId),
  });

  const handleStatusChange = async (newStatus: string) => {
    try {
      await updateTicketStatus(ticketId, newStatus);
      refetch(); // Refetch ticket details to update UI
    } catch (err) {
      console.error("Failed to update status", err);
    }
  };

  if (isLoading) {
    return <div className="p-4">Loading ticket details...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">Error loading ticket details: {error.message}</div>;
  }

  if (!ticket) {
    return <div className="p-4">No ticket found.</div>;
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Ticket #{ticket.id} Details</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Ticket Information */}
        <div className="lg:col-span-2 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div><strong>Machine:</strong> {MACHINE_ID_MAP[ticket.machine_id] || ticket.machine_id}</div>
            <div><strong>Category:</strong> {ticket.incident_category}</div>
            <div><strong>Priority:</strong> {ticket.priority}</div>
            <div><strong>Status:</strong> {ticket.status}</div>
            <div><strong>Logged:</strong> {format(new Date(ticket.logged_time), 'PPP p')}</div>
            <div><strong>Resolved:</strong> {ticket.resolved_time ? format(new Date(ticket.resolved_time), 'PPP p') : 'N/A'}</div>
          </div>
          <div>
            <strong>Description:</strong>
            <p className="bg-gray-100 p-3 rounded-md mt-1">{ticket.description}</p>
          </div>

          {/* Work Notes Section */}
          <WorkNotesSection ticketId={ticket.id} workNotes={ticket.work_notes || []} onNoteAdded={refetch} />

          {/* Image Section */}
          <ImageSection ticketId={ticket.id} images={ticket.images || []} onImageUploaded={refetch} />
        </div>

        {/* Actions and Components */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader><CardTitle className="text-lg">Update Status</CardTitle></CardHeader>
            <CardContent>
              <Select onValueChange={handleStatusChange} value={ticket.status}>
                <SelectTrigger>
                  <SelectValue placeholder="Select new status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Open">Open</SelectItem>
                  <SelectItem value="In Progress">In Progress</SelectItem>
                  <SelectItem value="Resolved">Resolved</SelectItem>
                </SelectContent>
              </Select>
            </CardContent>
          </Card>

          {/* Component Log Section */}
          <ComponentLogSection ticketId={ticket.id} componentsUsed={ticket.components_used || []} onComponentLogged={refetch} />
        </div>
      </CardContent>
    </Card>
  );
};

export default TicketDetailView;
