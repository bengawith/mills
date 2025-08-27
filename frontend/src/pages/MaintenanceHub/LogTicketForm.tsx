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
  const { toast } = useToast();
  const [machineId, setMachineId] = useState('');
  const [incidentCategory, setIncidentCategory] = useState('');
  const [priority, setPriority] = useState('Medium');
  const [description, setDescription] = useState('');
  const [selectedDowntimeId, setSelectedDowntimeId] = useState<string | null>(null);
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);

  const { data: machines, isLoading: isLoadingMachines } = useQuery<{id: string, name: string}[]>({
    queryKey: ['machines'],
    queryFn: getMachines,
  });

  const { data: downtimeEvents, isLoading: isLoadingDowntimes } = useQuery({
    queryKey: ['recentDowntimes', machineId],
    queryFn: async () => {
      if (!machineId) return [];
      const endTime = formatISO(new Date());
      const startTime = formatISO(subDays(new Date(), 1));
      return getRecentDowntimes(machineId, startTime, endTime);
    },
    enabled: !!machineId,
  });

  const createTicketMutation = useMutation({
    mutationFn: createMaintenanceTicket,
    onSuccess: (newTicket) => {
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

  const handleSubmit = (e: React.FormEvent) => {
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
