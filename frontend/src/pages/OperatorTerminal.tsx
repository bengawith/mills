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

interface Product {
  id: number;
  product_name: string;
}

interface ProductionRun {
  id: number;
  machine_id: string;
  product_id: number;
  status: string;
  start_time: string;
  end_time: string | null;
  scrap_length: number | null;
}

interface DowntimeEvent {
  id: string;
  machine_id: string;
  classification: string;
  start_time: string;
  end_time: string;
}

const OperatorTerminal = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // State for Start Production Run form
  const [startRunMachineId, setStartRunMachineId] = useState('');
  const [startRunProductId, setStartRunProductId] = useState('');

  // State for Complete Production Run form
  const [completeRunId, setCompleteRunId] = useState('');
  const [scrapLength, setScrapLength] = useState('');

  // State for View Machine Downtimes
  const [downtimeMachineId, setDowntimeMachineId] = useState('');
  const [downtimeStartTime, setDowntimeStartTime] = useState('2023-01-01T00:00:00');
  const [downtimeEndTime, setDowntimeEndTime] = useState('2023-01-31T23:59:59');

  // Fetch Products for dropdown
  const { data: products } = useQuery<Product[]>({ 
    queryKey: ['products'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/products');
      return response.data;
    },
  });

  // Fetch Downtime Events
  const { data: downtimes, isLoading: isLoadingDowntimes, error: downtimeError } = useQuery<DowntimeEvent[]>({
    queryKey: ['downtimeEvents', downtimeMachineId, downtimeStartTime, downtimeEndTime],
    queryFn: async () => {
      if (!downtimeMachineId) return Promise.reject('No machine ID for downtimes');
      const response = await apiClient.get('/api/v1/fourjaw/downtimes', {
        params: {
          machine_id: downtimeMachineId,
          start_time: downtimeStartTime,
          end_time: downtimeEndTime,
        },
      });
      return response.data;
    },
    enabled: !!downtimeMachineId, // Only run query if machineId is available
  });

  // Mutation for Start Production Run
  const startProductionRunMutation = useMutation({
    mutationFn: async (newRun: { machine_id: string; product_id: number }) => {
      const response = await apiClient.post('/api/v1/runs', newRun);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productionRuns'] }); // Invalidate runs list
      toast({
        title: "Production Run Started",
        description: "New production run initiated.",
      });
      setStartRunMachineId('');
      setStartRunProductId('');
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to start production run.",
        variant: "destructive",
      });
    },
  });

  const handleStartRunSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    startProductionRunMutation.mutate({ machine_id: startRunMachineId, product_id: parseInt(startRunProductId) });
  };

  // Mutation for Complete Production Run
  const completeProductionRunMutation = useMutation({
    mutationFn: async (updateRun: { run_id: number; scrap_length: number }) => {
      const response = await apiClient.put(`/api/v1/runs/${updateRun.run_id}/complete`, { scrap_length: updateRun.scrap_length });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productionRuns'] }); // Invalidate runs list
      toast({
        title: "Production Run Completed",
        description: "Production run marked as complete.",
      });
      setCompleteRunId('');
      setScrapLength('');
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to complete production run.",
        variant: "destructive",
      });
    },
  });

  const handleCompleteRunSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    completeProductionRunMutation.mutate({ run_id: parseInt(completeRunId), scrap_length: parseFloat(scrapLength) });
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Operator Terminal</h1>

      {/* Start Production Run */}
      <Card className="w-full max-w-lg mb-6">
        <CardHeader>
          <CardTitle>Start New Production Run</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleStartRunSubmit} className="space-y-4">
            <div>
              <Label htmlFor="startRunMachineId">Machine ID</Label>
              <Input
                id="startRunMachineId"
                type="text"
                value={startRunMachineId}
                onChange={(e) => setStartRunMachineId(e.target.value)}
                required
              />
            </div>
            <div>
              <Label htmlFor="startRunProductId">Product</Label>
              <Select onValueChange={setStartRunProductId} value={startRunProductId} required>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a product" />
                </SelectTrigger>
                <SelectContent>
                  {products?.map((product) => (
                    <SelectItem key={product.id} value={product.id.toString()}>
                      {product.product_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button type="submit" className="w-full" disabled={startProductionRunMutation.isPending}>
              {startProductionRunMutation.isPending ? 'Starting...' : 'Start Run'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Complete Production Run */}
      <Card className="w-full max-w-lg mb-6">
        <CardHeader>
          <CardTitle>Complete Production Run</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCompleteRunSubmit} className="space-y-4">
            <div>
              <Label htmlFor="completeRunId">Run ID</Label>
              <Input
                id="completeRunId"
                type="number"
                value={completeRunId}
                onChange={(e) => setCompleteRunId(e.target.value)}
                required
              />
            </div>
            <div>
              <Label htmlFor="scrapLength">Scrap Length</Label>
              <Input
                id="scrapLength"
                type="number"
                step="0.01"
                value={scrapLength}
                onChange={(e) => setScrapLength(e.target.value)}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={completeProductionRunMutation.isPending}>
              {completeProductionRunMutation.isPending ? 'Completing...' : 'Complete Run'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* View Machine Downtimes */}
      <Card className="w-full max-w-lg mb-6">
        <CardHeader>
          <CardTitle>View Machine Downtimes</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="downtimeMachineId">Machine ID</Label>
            <Input
              id="downtimeMachineId"
              type="text"
              value={downtimeMachineId}
              onChange={(e) => setDowntimeMachineId(e.target.value)}
              placeholder="e.g., mill_1"
            />
          </div>
          <div>
            <Label htmlFor="downtimeStartTime">Start Time</Label>
            <Input
              id="downtimeStartTime"
              type="datetime-local"
              value={downtimeStartTime}
              onChange={(e) => setDowntimeStartTime(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="downtimeEndTime">End Time</Label>
            <Input
              id="downtimeEndTime"
              type="datetime-local"
              value={downtimeEndTime}
              onChange={(e) => setDowntimeEndTime(e.target.value)}
            />
          </div>

          {isLoadingDowntimes && downtimeMachineId && <div className="p-4">Loading downtimes...</div>}
          {downtimeError && downtimeMachineId && <div className="p-4 text-red-500">Error loading downtimes: {downtimeError.message}</div>}

          {downtimes && downtimes.length > 0 ? (
            <div className="space-y-2">
              <h3 className="font-semibold">Downtime Events:</h3>
              {downtimes.map((downtime) => (
                <Card key={downtime.id} className="p-3 text-sm">
                  <p><strong>Machine:</strong> {downtime.machine_id}</p>
                  <p><strong>Classification:</strong> {downtime.classification}</p>
                  <p><strong>Start:</strong> {format(new Date(downtime.start_time), 'PPP p')}</p>
                  <p><strong>End:</strong> {format(new Date(downtime.end_time), 'PPP p')}</p>
                </Card>
              ))}
            </div>
          ) : (
            downtimeMachineId && !isLoadingDowntimes && <p>No downtime events found for the selected machine and period.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default OperatorTerminal;