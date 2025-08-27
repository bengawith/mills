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
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [selectedMachineId, setSelectedMachineId] = useState<string | null>(null);
  const [isScrapModalOpen, setIsScrapModalOpen] = useState(false);
  const [scrapLength, setScrapLength] = useState('');

  const { data: machines = [] } = useQuery({ queryKey: ['machines'], queryFn: getMachines });
  const { data: products = [] } = useQuery({ queryKey: ['products'], queryFn: getProducts });

  const { data: activeRun, isLoading: isLoadingActiveRun } = useQuery({
    queryKey: ['activeRun', selectedMachineId],
    queryFn: () => getActiveRunForMachine(selectedMachineId!),
    enabled: !!selectedMachineId,
  });

  const { data: recentDowntimes, isLoading: isLoadingDowntimes } = useQuery({
    queryKey: ['recentDowntimes', selectedMachineId],
    queryFn: () => getRecentDowntimes(selectedMachineId!, new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), new Date().toISOString()),
    enabled: !!selectedMachineId,
  });

  const startRunMutation = useMutation({
    mutationFn: ({ machine_id, product_id }: { machine_id: string; product_id: number }) => startProductionRun({ machine_id, product_id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activeRun', selectedMachineId] });
      toast({ title: 'Success', description: 'Production run started.' });
    },
  });

  const completeRunMutation = useMutation({
    mutationFn: ({ run_id, scrap_length }: { run_id: number; scrap_length: number }) => completeProductionRun({ run_id, scrap_length }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activeRun', selectedMachineId] });
      setIsScrapModalOpen(false);
      setScrapLength('');
      toast({ title: 'Success', description: 'Production run completed.' });
    },
  });

  const handleCompleteRun = () => {
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
