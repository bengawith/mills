import React, { useState } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { createMaintenanceTicket, getMachines, getRecentDowntimes, uploadTicketImage } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { MACHINE_ID_MAP } from '@/lib/constants'; // Import MACHINE_ID_MAP
import { formatISO, subDays } from 'date-fns'; // For date formatting

const LogNewTicket = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [machineId, setMachineId] = useState('');
  const [incidentCategory, setIncidentCategory] = useState('');
  const [priority, setPriority] = useState('Medium'); // Default priority
  const [description, setDescription] = useState('');
  const [selectedDowntimeId, setSelectedDowntimeId] = useState<string | null>(null);
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);

  const { data: machines, isLoading: isLoadingMachines } = useQuery({
    queryKey: ['machines'],
    queryFn: getMachines,
  });

  const { data: downtimeEvents, isLoading: isLoadingDowntimes } = useQuery({
    queryKey: ['recentDowntimes', machineId],
    queryFn: async () => {
      if (!machineId) return [];
      const endTime = formatISO(new Date());
      const startTime = formatISO(subDays(new Date(), 1)); // Last 24 hours
      return getRecentDowntimes(machineId, startTime, endTime);
    },
    enabled: !!machineId, // Only fetch if machineId is selected
  });

  const createTicketMutation = useMutation({
    mutationFn: async (newTicket: {
      machine_id: string;
      incident_category: string;
      priority: string;
      description: string;
      fourjaw_downtime_id?: string | null;
    }) => {
      const response = await createMaintenanceTicket(newTicket);
      return response;
    },
    onSuccess: (newTicket) => {
      queryClient.invalidateQueries({ queryKey: ['maintenanceTickets'] });
      toast({
        title: 'Ticket Created',
        description: `New maintenance ticket #${newTicket.id} logged successfully.`,
      });

      if (uploadedImage && newTicket.id) {
        uploadTicketImage(newTicket.id, uploadedImage)
          .then(() => {
            toast({
              title: 'Image Uploaded',
              description: 'Image attached to ticket successfully.',
            });
          })
          .catch((error) => {
            toast({
              title: 'Image Upload Failed',
              description: error.response?.data?.detail || 'Failed to upload image.',
              variant: 'destructive',
            });
          });
      }

      // Clear form
      setMachineId('');
      setIncidentCategory('');
      setPriority('Medium');
      setDescription('');
      setSelectedDowntimeId(null);
      setUploadedImage(null);
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to log ticket.',
        variant: 'destructive',
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!machineId || !incidentCategory || !description) {
      toast({
        title: 'Validation Error',
        description: 'Please fill out all required fields.',
        variant: 'destructive',
      });
      return;
    }

    const payload = {
      machine_id: machineId,
      incident_category: incidentCategory,
      priority: priority,
      description: description,
      fourjaw_downtime_id: selectedDowntimeId,
    };
    createTicketMutation.mutate(payload);
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setUploadedImage(e.target.files[0]);
    } else {
      setUploadedImage(null);
    }
  };

  const downtimeOptions = downtimeEvents?.map((evt: any) => ({
    label: `${new Date(evt.start_timestamp).toLocaleString()} (${(evt.duration_seconds / 60).toFixed(0)} mins) - ${evt.downtime_reason_name || 'N/A'}`,
    value: evt.id,
  })) || [];

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
              <Label htmlFor="machineId">Machine</Label>
              <Select onValueChange={setMachineId} value={machineId} required>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a machine" />
                </SelectTrigger>
                <SelectContent>
                  {isLoadingMachines && <SelectItem value="" disabled>Loading machines...</SelectItem>}
                  {machines?.map((m: string) => (
                    <SelectItem key={m} value={m}>
                      {MACHINE_ID_MAP[m] || m}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
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
                  <SelectItem value="Tooling">Tooling</SelectItem>
                  <SelectItem value="Hydraulic">Hydraulic</SelectItem>
                  <SelectItem value="Software">Software</SelectItem>
                  <SelectItem value="Other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="priority">Priority</Label>
              <Select onValueChange={setPriority} value={priority} required>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Low">Low</SelectItem>
                  <SelectItem value="Medium">Medium</SelectItem>
                  <SelectItem value="High">High</SelectItem>
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

            {machineId && (
              <div>
                <Label htmlFor="downtimeLink">Link to FourJaw Downtime Event (Optional)</Label>
                <Select onValueChange={setSelectedDowntimeId} value={selectedDowntimeId || ''}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select a downtime event" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">None</SelectItem>
                    {isLoadingDowntimes && <SelectItem value="loading" disabled>Loading downtimes...</SelectItem>}
                    {downtimeOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div>
              <Label htmlFor="imageUpload">Upload Image (Optional)</Label>
              <Input id="imageUpload" type="file" accept="image/*" onChange={handleImageChange} />
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
