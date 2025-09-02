/*
  index.tsx - MillDash Frontend Operator Terminal Page

  This file implements the operator terminal for the MillDash application using React and TypeScript. It provides a user interface for machine operators to start and complete production runs, view active runs, and monitor recent downtime events. The component integrates with backend APIs for machine, product, and run management, and uses custom UI components for a consistent and accessible layout.

  Key Features:
  - Uses React functional component with hooks for state management (selected machine, scrap modal, scrap length).
  - Fetches machine list, product list, active run, and recent downtime events using React Query.
  - Allows operators to start new production runs and complete active runs with scrap length input.
  - Displays recent downtime events for the selected machine.
  - Utilizes custom UI components (Card, Button, Dialog, Input) and Tailwind CSS for layout.
  - Responsive and visually appealing interface for operator workflow.

  This component is essential for efficient shop floor operations, enabling operators to manage production and downtime in real time.
*/

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMachines, getProducts, getActiveRunForMachine, startProductionRun, completeProductionRun, getRecentDowntimes } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { format } from 'date-fns';

const OperatorTerminal = () => {
  // React Query client for cache management and invalidation
  const queryClient = useQueryClient();
  // Toast notification handler for user feedback
  const { toast } = useToast();
  // State for selected machine ID
  const [selectedMachineId, setSelectedMachineId] = useState<string | null>(null);
  // State for controlling scrap modal visibility
  const [isScrapModalOpen, setIsScrapModalOpen] = useState<boolean>(false);
  // State for scrap length input
  const [scrapLength, setScrapLength] = useState<string>('');

  /**
   * Fetches the list of available machines from the backend for selection.
   * Uses React Query for caching and loading/error state management.
   */
  const { data: machines = [] } = useQuery<any[]>({ queryKey: ['machines'], queryFn: getMachines });
  /**
   * Fetches the list of available products from the backend for selection.
   * Uses React Query for caching and loading/error state management.
   */
  const { data: products = [] } = useQuery<any[]>({ queryKey: ['products'], queryFn: getProducts });

  /**
   * Fetches the active production run for the selected machine.
   * Uses React Query for caching and loading/error state management.
   */
  const { data: activeRun, isLoading: isLoadingActiveRun } = useQuery<any>({
    queryKey: ['activeRun', selectedMachineId],
    queryFn: () => getActiveRunForMachine(selectedMachineId!),
    enabled: !!selectedMachineId,
  });

  /**
   * Fetches recent downtime events for the selected machine (last 24 hours).
   * Uses React Query for caching and loading/error state management.
   */
  const { data: recentDowntimes, isLoading: isLoadingDowntimes } = useQuery<any[]>({
    queryKey: ['recentDowntimes', selectedMachineId],
    queryFn: () => getRecentDowntimes(selectedMachineId!, new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), new Date().toISOString()),
    enabled: !!selectedMachineId,
  });

  /**
   * Mutation for starting a new production run on the selected machine.
   * On success, invalidates active run query and shows success toast.
   */
  const startRunMutation = useMutation({
    mutationFn: ({ machine_id, product_id }: { machine_id: string; product_id: number }) => startProductionRun({ machine_id, product_id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activeRun', selectedMachineId] });
      toast({ title: 'Success', description: 'Production run started.' });
    },
  });

  /**
   * Mutation for completing the active production run with scrap length input.
   * On success, invalidates active run query, closes modal, and shows success toast.
   */
  const completeRunMutation = useMutation({
    mutationFn: ({ run_id, scrap_length }: { run_id: number; scrap_length: number }) => completeProductionRun({ run_id, scrap_length }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activeRun', selectedMachineId] });
      setIsScrapModalOpen(false);
      setScrapLength('');
      toast({ title: 'Success', description: 'Production run completed.' });
    },
  });

  /**
   * Handles completion of the active production run.
   * Triggers mutation with run ID and scrap length.
   */
  const handleCompleteRun = (): void => {
    if (activeRun) {
      completeRunMutation.mutate({ run_id: activeRun.id, scrap_length: parseFloat(scrapLength) });
    }
  };

  return (
    <div className="p-4 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold text-center mb-6">Operator Terminal</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1">
          <Card>
            <CardHeader><CardTitle>Select a Machine</CardTitle></CardHeader>
            <CardContent className="grid grid-cols-2 gap-4">
              {machines.map((machine) => (
                <Button key={machine.id} onClick={() => setSelectedMachineId(machine.id)} variant={selectedMachineId === machine.id ? 'default' : 'outline'} className="h-20 text-lg">
                  {machine.name}
                </Button>
              ))}
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-2">
          {selectedMachineId && (
            <Card>
              <CardHeader><CardTitle>Machine: {machines.find(m => m.id === selectedMachineId)?.name}</CardTitle></CardHeader>
              <CardContent>
                {isLoadingActiveRun ? (
                  <p>Loading...</p>
                ) : activeRun ? (
                  <div>
                    <h2 className="text-xl font-semibold mb-2">Active Run</h2>
                    <p><strong>Product:</strong> {products.find(p => p.id === activeRun.product_id)?.product_name}</p>
                    <p><strong>Start Time:</strong> {format(new Date(activeRun.start_time), 'PPP p')}</p>
                    <Dialog open={isScrapModalOpen} onOpenChange={setIsScrapModalOpen}>
                      <DialogTrigger asChild>
                        <Button className="w-full mt-4 h-16 text-xl">Complete Run</Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader><DialogTitle>Enter Scrap Length</DialogTitle></DialogHeader>
                        <div className="grid gap-4 py-4">
                          <Input type="number" placeholder="Scrap length in meters" value={scrapLength} onChange={(e) => setScrapLength(e.target.value)} className="text-2xl h-16" />
                        </div>
                        <DialogFooter>
                          <Button onClick={handleCompleteRun} className="w-full h-12 text-lg">Confirm</Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </div>
                ) : (
                  <div>
                    <h2 className="text-xl font-semibold mb-2">Start New Run</h2>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {products.map((product) => (
                        <Button key={product.id} onClick={() => startRunMutation.mutate({ machine_id: selectedMachineId, product_id: product.id })} className="h-20 text-lg">
                          {product.product_name}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mt-6">
                  <h2 className="text-xl font-semibold mb-2">Recent Downtime (Last 24h)</h2>
                  {isLoadingDowntimes ? (
                    <p>Loading downtime...</p>
                  ) : recentDowntimes && recentDowntimes.length > 0 ? (
                    <ul className="space-y-2">
                      {recentDowntimes.map((downtime) => (
                        <li key={downtime.id} className="p-2 border rounded-md">
                          <p><strong>Classification:</strong> {downtime.classification}</p>
                          <p><strong>Start:</strong> {format(new Date(downtime.start_time), 'p')} - <strong>End:</strong> {format(new Date(downtime.end_time), 'p')}</p>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p>No downtime events in the last 24 hours.</p>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default OperatorTerminal;
