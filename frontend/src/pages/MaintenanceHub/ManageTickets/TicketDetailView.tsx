/*
  TicketDetailView.tsx - MillDash Frontend Maintenance Ticket Detail View Component

  This file implements the detailed view for a maintenance ticket in the MillDash maintenance hub using React and TypeScript. It provides a user interface for viewing ticket information, updating status, adding work notes, uploading images, and logging components used. The component fetches ticket details from the backend, allows status updates with confirmation, and uses custom UI components for a consistent and accessible layout.

  Key Features:
  - Uses React functional component with props for ticket ID and close handler.
  - Fetches ticket details using React Query and updates on mutation or note/image/component changes.
  - Allows status updates with confirmation dialog for resolving tickets.
  - Displays ticket information, work notes, images, and components used.
  - Utilizes custom UI components (Card, Select, AlertDialog, Button) and Lucide icons.
  - Responsive and visually appealing layout using Tailwind CSS grid utilities.

  This component is essential for maintenance management, enabling users to track, update, and resolve machine issues efficiently.
*/

import React, { useState } from 'react';
import { useToast } from '@/hooks/use-toast';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getTicketDetails, updateTicketStatus } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { MACHINE_ID_MAP } from '@/lib/constants';
import { format } from 'date-fns';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';
import WorkNotesSection from './WorkNotesSection';
import ImageSection from './ImageSection';
import ComponentLogSection from './ComponentLogSection';


/**
 * Props for the TicketDetailView component.
 */
export interface TicketDetailViewProps {
  ticketId: number;
  onClose?: () => void;
}


/**
 * TicketDetailView component displays detailed information for a maintenance ticket,
 * including status, work notes, images, and components used. Allows status updates and logging.
 */
const TicketDetailView: React.FC<TicketDetailViewProps> = ({ ticketId, onClose }: TicketDetailViewProps) => {
  // React Query client for cache management
  const queryClient = useQueryClient();
  // Toast notification handler for user feedback
  const { toast } = useToast();
  // State for alert dialog visibility
  const [isAlertOpen, setIsAlertOpen] = useState<boolean>(false);
  // State for new status to be confirmed
  const [newStatus, setNewStatus] = useState<string | null>(null);

  /**
   * Query for fetching ticket details.
   */
  const { data: ticket, isLoading, error } = useQuery<any>({
    queryKey: ['ticketDetails', ticketId],
    queryFn: () => getTicketDetails(ticketId),
  });

  /**
   * Mutation for updating ticket status.
   */
  const mutation = useMutation<string, unknown, string>({
    mutationFn: (status: string): Promise<any> => updateTicketStatus(ticketId, status),
    onSuccess: (): void => {
      queryClient.invalidateQueries({ queryKey: ['ticketDetails', ticketId] });
    },
    onError: (err: any): void => {
      toast({
        title: 'Error',
        description: err?.response?.data?.detail || 'Failed to update ticket status.',
        variant: 'destructive',
      });
      console.error("Failed to update status", err);
    },
  });

  /**
   * Handles status change selection.
   * @param status - New status value
   */
  const handleStatusChange = (status: string): void => {
    if (status === 'Resolved') {
      setNewStatus(status);
      setIsAlertOpen(true);
    } else {
      mutation.mutate(status);
    }
  };

  /**
   * Confirms status change to 'Resolved'.
   */
  const confirmStatusChange = (): void => {
    if (newStatus) {
      mutation.mutate(newStatus);
    }
    setIsAlertOpen(false);
    setNewStatus(null);
  };


  // Loading state
  if (isLoading) {
    return <div className="p-4">Loading ticket details...</div>;
  }

  // Error state
  if (error) {
    // Type assertion for error message
    return <div className="p-4 text-red-500">Error loading ticket details: {(error as Error).message}</div>;
  }

  // No ticket found state
  if (!ticket) {
    return <div className="p-4">No ticket found.</div>;
  }


  // Render the detailed ticket view
  return (
    <>
      <Card className="w-full">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Ticket #{ticket.id} Details</CardTitle>
          {onClose && (
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          )}
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
            <WorkNotesSection ticketId={ticket.id} workNotes={ticket.work_notes || []} onNoteAdded={() => queryClient.invalidateQueries({ queryKey: ['ticketDetails', ticketId] })} />

            {/* Image Section */}
            <ImageSection ticketId={ticket.id} images={ticket.images || []} onImageUploaded={() => queryClient.invalidateQueries({ queryKey: ['ticketDetails', ticketId] })} />
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
            <ComponentLogSection ticketId={ticket.id} componentsUsed={ticket.components_used || []} onComponentLogged={() => queryClient.invalidateQueries({ queryKey: ['ticketDetails', ticketId] })} />
          </div>
        </CardContent>
      </Card>

      {/* Confirmation dialog for resolving ticket */}
      <AlertDialog open={isAlertOpen} onOpenChange={setIsAlertOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action will mark the ticket as resolved and cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setNewStatus(null)}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmStatusChange}>Continue</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};

export default TicketDetailView;
