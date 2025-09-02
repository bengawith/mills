// -----------------------------------------------------------------------------
// ComponentLogSection.tsx
//
// This file defines the ComponentLogSection React functional component, which is
// used within the ManageTickets module of the MaintenanceHub to display and log
// components used for a specific maintenance ticket. It provides a UI for listing
// all components already logged for the ticket, and a form to add new components
// from inventory, including quantity used. The component uses React Query for data
// fetching and mutation, custom toast hooks for notifications, and UI components
// for consistent styling. It accepts the ticket ID, a list of components used, and
// a callback for when a new component is logged.
//
// Props:
//   - ticketId: number (ID of the ticket for which components are logged)
//   - componentsUsed: ComponentUsed[] (array of objects with quantity and component details)
//   - onComponentLogged: () => void (callback to trigger parent refresh after logging)
//
// Usage:
//   <ComponentLogSection ticketId={...} componentsUsed={...} onComponentLogged={...} />
// -----------------------------------------------------------------------------

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


/**
 * Represents a component used in a ticket, including quantity and component details.
 */
export interface ComponentUsed {
  quantity_used: number;
  component: {
    id: number;
    component_name: string;
    stock_code: string;
    current_stock: number;
  };
}


/**
 * Props for the ComponentLogSection component.
 */
export interface ComponentLogSectionProps {
  ticketId: number;
  componentsUsed: ComponentUsed[];
  onComponentLogged: () => void;
}


/**
 * ComponentLogSection displays all components used for a ticket and provides
 * functionality to log new components from inventory. Uses React Query for data fetching and mutation.
 */
const ComponentLogSection: React.FC<ComponentLogSectionProps> = ({ ticketId, componentsUsed, onComponentLogged }: ComponentLogSectionProps) => {
  // React Query client for cache management
  const queryClient = useQueryClient();
  // Toast hook for notifications
  const { toast } = useToast();
  // State for the currently selected component ID
  const [selectedComponentId, setSelectedComponentId] = useState<string>('');
  // State for the quantity used
  const [quantityUsed, setQuantityUsed] = useState<number>(1);

  /**
   * Query for fetching inventory components.
   */
  const { data: inventoryComponents, isLoading: isLoadingInventory } = useQuery<any[]>({
    queryKey: ['inventoryComponents'],
    queryFn: getInventoryComponents,
  });

  /**
   * Mutation for adding a component to the ticket.
   */
  const addComponentMutation = useMutation<{ componentId: number; quantityUsed: number }, unknown, { componentId: number; quantityUsed: number }>({
    mutationFn: (data: { componentId: number; quantityUsed: number }): Promise<any> =>
      addComponentToTicket(ticketId, data.componentId, data.quantityUsed),
    onSuccess: (): void => {
      setSelectedComponentId('');
      setQuantityUsed(1);
      onComponentLogged(); // Trigger refetch in parent
      queryClient.invalidateQueries({ queryKey: ['inventoryComponents'] }); // Invalidate inventory to update stock
      toast({
        title: "Component Logged",
        description: "Component usage logged successfully.",
      });
    },
    onError: (error: any): void => {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to log component usage.",
        variant: "destructive",
      });
    },
  });


  /**
   * Handles the form submission to add a component to the ticket.
   * @param e - Form event
   */
  const handleAddComponent = (e: React.FormEvent<HTMLFormElement>): void => {
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


  // Render the card with components used and form to log new components
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Components Used</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Display components used in a table */}
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
                componentsUsed.map((item: ComponentUsed, index: number) => (
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

        {/* Form to log a new component usage */}
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
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuantityUsed(parseInt(e.target.value))}
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
