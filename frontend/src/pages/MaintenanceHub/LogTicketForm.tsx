/*
  LogTicketForm.tsx - MillDash Frontend Maintenance Ticket Logging Form

  This file implements the form for logging new maintenance tickets in the MillDash application using React and TypeScript. It provides a user interface for entering ticket details, selecting machine and incident category, setting priority, linking downtime events, and uploading images. The component integrates with backend APIs for ticket creation and image upload, and uses custom UI components for a consistent and accessible layout.

  Key Features:
  - Uses React functional component with props for ticket creation callback.
  - Manages form state for machine, category, priority, description, downtime event, and image upload.
  - Fetches machine list and recent downtime events using React Query.
  - Submits ticket data to backend and uploads image if provided.
  - Displays toast notifications for success, error, and validation feedback.
  - Utilizes custom UI components (Card, Button, Input, Label, Select, Textarea).
  - Responsive and visually appealing layout using Tailwind CSS utility classes.

  This component is essential for efficient maintenance management, enabling users to quickly log and track machine issues.
*/

import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createMaintenanceTicket, getMachines, getRecentDowntimes, uploadTicketImage } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { formatISO, subDays } from 'date-fns';

interface LogTicketFormProps {
  onTicketCreated: () => void;
}

const LogTicketForm: React.FC<LogTicketFormProps> = ({ onTicketCreated }) => {
  // Toast notification handler for user feedback
  const { toast } = useToast();
  // State for selected machine ID
  const [machineId, setMachineId] = useState<string>('');
  // State for selected incident category
  const [incidentCategory, setIncidentCategory] = useState<string>('');
  // State for selected priority
  const [priority, setPriority] = useState<string>('Medium');
  // State for ticket description
  const [description, setDescription] = useState<string>('');
  // State for selected downtime event ID (optional)
  const [selectedDowntimeId, setSelectedDowntimeId] = useState<string | null>(null);
  // State for uploaded image file (optional)
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);

  /**
   * Fetches the list of available machines from the backend for machine selection.
   * Uses React Query for caching and loading/error state management.
   */
  const { data: machines, isLoading: isLoadingMachines } = useQuery<{id: string, name: string}[]>({
    queryKey: ['machines'],
    queryFn: getMachines,
  });

  /**
   * Fetches recent downtime events for the selected machine (last 24 hours).
   * Uses React Query for caching and loading/error state management.
   */
  const { data: downtimeEvents, isLoading: isLoadingDowntimes } = useQuery<any[]>({
    queryKey: ['recentDowntimes', machineId],
    queryFn: async () => {
      if (!machineId) return [];
      const endTime = formatISO(new Date());
      const startTime = formatISO(subDays(new Date(), 1));
      return getRecentDowntimes(machineId, startTime, endTime);
    },
    enabled: !!machineId,
  });

  /**
   * Mutation for creating a new maintenance ticket.
   * On success, uploads image if provided and calls ticket created callback.
   * On error, displays error toast.
   */
  const createTicketMutation = useMutation({
    mutationFn: createMaintenanceTicket,
    onSuccess: (newTicket: any) => {
      toast({ title: 'Ticket Created', description: `Ticket #${newTicket.id} logged.` });
      if (uploadedImage && newTicket.id) {
        uploadTicketImage(newTicket.id, uploadedImage).then(() => {
          toast({ title: 'Image Uploaded' });
        }).catch(() => toast({ title: 'Image Upload Failed', variant: 'destructive' }));
      }
      onTicketCreated();
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.response?.data?.detail || 'Failed to log ticket.', variant: 'destructive' });
    },
  });

  /**
   * Handles form submission for logging a new maintenance ticket.
   * Validates required fields and triggers ticket creation mutation.
   * @param e - React form event
   */
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    if (!machineId || !incidentCategory || !description) {
      toast({ title: 'Validation Error', description: 'Please fill out all required fields.', variant: 'destructive' });
      return;
    }
    createTicketMutation.mutate({ machine_id: machineId, incident_category: incidentCategory, priority: priority, description: description, fourjaw_downtime_id: selectedDowntimeId });
  };

  return (
    <Card className="w-full max-w-lg mt-6">
      <CardHeader><CardTitle>Create New Ticket</CardTitle></CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>Machine</Label>
            <Select onValueChange={setMachineId} value={machineId} required>
              <SelectTrigger><SelectValue placeholder="Select a machine" /></SelectTrigger>
              <SelectContent>{isLoadingMachines ? <SelectItem value="loading" disabled>Loading...</SelectItem> : machines?.map(m => <SelectItem key={m.id} value={m.id}>{m.name}</SelectItem>)}</SelectContent>
            </Select>
          </div>
          <div>
            <Label>Incident Category</Label>
            <Select onValueChange={setIncidentCategory} value={incidentCategory} required>
              <SelectTrigger><SelectValue placeholder="Select a category" /></SelectTrigger>
              <SelectContent>{
                ["Mechanical", "Electrical", "Tooling", "Hydraulic", "Software", "Other"].map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)
              }</SelectContent>
            </Select>
          </div>
          <div>
            <Label>Priority</Label>
            <Select onValueChange={setPriority} value={priority} required>
              <SelectTrigger><SelectValue placeholder="Select priority" /></SelectTrigger>
              <SelectContent>{["Low", "Medium", "High"].map(p => <SelectItem key={p} value={p}>{p}</SelectItem>)}</SelectContent>
            </Select>
          </div>
          <div>
            <Label>Description</Label>
            <Textarea value={description} onChange={(e) => setDescription(e.target.value)} required rows={5} />
          </div>
          {machineId && (
            <div>
              <Label>Link to FourJaw Downtime Event (Optional)</Label>
              <Select onValueChange={(v) => setSelectedDowntimeId(v === 'none' ? null : v)} value={selectedDowntimeId || ''}>
                <SelectTrigger><SelectValue placeholder="Select a downtime event" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {isLoadingDowntimes ? <SelectItem value="loading" disabled>Loading...</SelectItem> : downtimeEvents?.map((evt: any) => <SelectItem key={evt.id} value={evt.id}>{`${new Date(evt.start_timestamp).toLocaleString()} (${(evt.duration_seconds / 60).toFixed(0)} mins) - ${evt.downtime_reason_name || 'N/A'}`}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          )}
          <div>
            <Label>Upload Image (Optional)</Label>
            <Input type="file" accept="image/*" onChange={(e) => setUploadedImage(e.target.files ? e.target.files[0] : null)} />
          </div>
          <Button type="submit" className="w-full" disabled={createTicketMutation.isPending}>{createTicketMutation.isPending ? 'Logging...' : 'Log Ticket'}</Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default LogTicketForm;
