import React, { useState } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { addComponentToTicket, getInventoryComponents } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { useToast } from '@/hooks/use-toast';

interface ComponentUsed {
  quantity_used: number;
  component: {
    id: number;
    component_name: string;
    stock_code: string;
    current_stock: number;
  };
}

interface ComponentLogSectionProps {
  ticketId: number;
  componentsUsed: ComponentUsed[];
  onComponentLogged: () => void;
}

const ComponentLogSection: React.FC<ComponentLogSectionProps> = ({ ticketId, componentsUsed, onComponentLogged }) => {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [selectedComponentId, setSelectedComponentId] = useState('');
  const [quantityUsed, setQuantityUsed] = useState(1);

  const { data: inventoryComponents, isLoading: isLoadingInventory } = useQuery({
    queryKey: ['inventoryComponents'],
    queryFn: getInventoryComponents,
  });

  const addComponentMutation = useMutation({
    mutationFn: (data: { componentId: number; quantityUsed: number }) =>
      addComponentToTicket(ticketId, data.componentId, data.quantityUsed),
    onSuccess: () => {
      setSelectedComponentId('');
      setQuantityUsed(1);
      onComponentLogged(); // Trigger refetch in parent
      queryClient.invalidateQueries({ queryKey: ['inventoryComponents'] }); // Invalidate inventory to update stock
      toast({
        title: "Component Logged",
        description: "Component usage logged successfully.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to log component usage.",
        variant: "destructive",
      });
    },
  });

  const handleAddComponent = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedComponentId && quantityUsed > 0) {
      addComponentMutation.mutate({ componentId: parseInt(selectedComponentId), quantityUsed });
    } else {
      toast({
        title: "Validation Error",
        description: "Please select a component and enter a valid quantity.",
        variant: "destructive",
      });
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Components Used</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="max-h-40 overflow-y-auto mb-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Component</TableHead>
                <TableHead>Quantity</TableHead>
                <TableHead>Stock Code</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {componentsUsed.length > 0 ? (
                componentsUsed.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell>{item.component.component_name}</TableCell>
                    <TableCell>{item.quantity_used}</TableCell>
                    <TableCell>{item.component.stock_code}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={3} className="text-center">No components logged for this ticket.</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>

        <form onSubmit={handleAddComponent} className="space-y-2">
          <div>
            <Label htmlFor="componentSelect">Component</Label>
            <Select onValueChange={setSelectedComponentId} value={selectedComponentId}>
              <SelectTrigger>
                <SelectValue placeholder="Select a component" />
              </SelectTrigger>
              <SelectContent>
                {isLoadingInventory && <SelectItem value="loading" disabled>Loading components...</SelectItem>}
                {inventoryComponents?.map((comp: any) => (
                  <SelectItem key={comp.id} value={String(comp.id)}>
                    {comp.component_name} (Stock: {comp.current_stock})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="quantityUsed">Quantity Used</Label>
            <Input
              id="quantityUsed"
              type="number"
              value={quantityUsed}
              onChange={(e) => setQuantityUsed(parseInt(e.target.value))}
              min={1}
            />
          </div>
          <Button type="submit" size="sm" disabled={addComponentMutation.isPending}>
            {addComponentMutation.isPending ? 'Logging...' : 'Log Component'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default ComponentLogSection;
