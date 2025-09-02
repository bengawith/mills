/*
  index.tsx - MillDash Frontend Maintenance Hub Page

  This file implements the main maintenance hub page for the MillDash application using React and TypeScript. It provides a comprehensive interface for viewing, filtering, logging, and managing maintenance tickets. The component integrates with backend APIs and WebSocket events for real-time updates, and uses custom UI components for a consistent and accessible layout.

  Key Features:
  - Uses React functional component with hooks for state management (active tab, selected ticket, filters).
  - Fetches maintenance tickets and machine list using React Query.
  - Integrates with WebSocket events for real-time ticket updates and status changes.
  - Provides tabbed navigation for overview, logging new tickets, and managing selected tickets.
  - Displays ticket insights, ticket list with filtering, and detailed ticket view.
  - Utilizes custom UI components (Card, Table, Select, Tabs, etc.) and Lucide icons.
  - Responsive and visually appealing layout using Tailwind CSS utility classes.

  This component is the core maintenance management hub for MillDash, enabling users to efficiently track and resolve machine issues.
*/

import React, { useState, useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getMaintenanceTickets, getMachines } from '@/lib/api';
import { useWebSocketEvent } from '@/contexts/WebSocketContext';
import { EventTypes } from '@/lib/websocket-types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { format } from 'date-fns';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Search } from 'lucide-react';
import TicketInsights from './ManageTickets/TicketInsights';
import TicketDetailView from './ManageTickets/TicketDetailView';
import LogTicketForm from './LogTicketForm';

interface MaintenanceTicket {
    id: number;
    machine_id: string;
    incident_category: string;
    description: string;
    priority: string;
    status: string;
    logged_time: string;
    resolved_time: string | null;
}

const MaintenanceHub = () => {
  // State for managing the active tab in the maintenance hub
  const [activeTab, setActiveTab] = useState<string>("overview");
  // State for storing the selected ticket ID for management
  const [selectedTicketId, setSelectedTicketId] = useState<number | null>(null);
  // State for filtering tickets by status
  const [selectedStatus, setSelectedStatus] = useState<string>('All');
  // State for filtering tickets by machine
  const [selectedMachine, setSelectedMachine] = useState<string>('All');
  // React Query client for cache management and invalidation
  const queryClient = useQueryClient();

  /**
   * Fetches all maintenance tickets from the backend API.
   * Uses React Query for caching and loading/error state management.
   */
  const { data: tickets, isLoading: isLoadingTickets } = useQuery<MaintenanceTicket[]>({ 
    queryKey: ['maintenanceTickets', 'all'],
    queryFn: () => getMaintenanceTickets('all'),
  });

  /**
   * Fetches the list of available machines from the backend for filtering and display.
   * Uses React Query for caching and loading/error state management.
   */
  const { data: machines, isLoading: isLoadingMachines } = useQuery<{id: string, name: string}[]>({
    queryKey: ['machines'],
    queryFn: getMachines,
  });

  /**
   * WebSocket event handler for ticket creation.
   * Invalidates ticket queries to refetch updated data.
   */
  useWebSocketEvent(EventTypes.TICKET_CREATED, () => {
    queryClient.invalidateQueries({ queryKey: ['maintenanceTickets'] });
  });

  /**
   * WebSocket event handler for ticket status change.
   * Invalidates ticket queries and selected ticket details to refetch updated data.
   */
  useWebSocketEvent(EventTypes.TICKET_STATUS_CHANGE, () => {
    queryClient.invalidateQueries({ queryKey: ['maintenanceTickets'] });
    if (selectedTicketId) {
      queryClient.invalidateQueries({ queryKey: ['ticketDetails', selectedTicketId] });
    }
  });

  /**
   * Memoized filter for maintenance tickets based on selected status and machine.
   */
  const filteredTickets: MaintenanceTicket[] = useMemo(() => {
    if (!tickets) return [];
    return tickets.filter(ticket => {
      const statusMatch = selectedStatus === 'All' || ticket.status === selectedStatus;
      const machineMatch = selectedMachine === 'All' || ticket.machine_id === selectedMachine;
      return statusMatch && machineMatch;
    });
  }, [tickets, selectedStatus, selectedMachine]);

  /**
   * Handles selection of a ticket for management.
   * Sets the selected ticket ID and switches to the manage tab.
   * @param ticketId - The ID of the selected ticket
   */
  const handleTicketSelect = (ticketId: number): void => {
    setSelectedTicketId(ticketId);
    setActiveTab("manage");
  }

  /**
   * Handles closing the ticket detail view.
   * Clears the selected ticket ID and switches to the overview tab.
   */
  const handleCloseTicketView = (): void => {
    setSelectedTicketId(null);
    setActiveTab("overview");
  }

  /**
   * Returns the machine name for a given machine ID.
   * @param machineId - The machine ID
   */
  const getMachineName = (machineId: string): string => {
    const machine = machines?.find(m => m.id === machineId);
    return machine ? machine.name : machineId;
  };

  // List of all unique ticket statuses for filtering
  const allStatuses: string[] = ['All', ...new Set(tickets?.map(ticket => ticket.status) || [])];

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-2xl font-bold mb-4">Maintenance Hub</h1>
      <TicketInsights />

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="log">Log New Ticket</TabsTrigger>
          <TabsTrigger value="manage" disabled={!selectedTicketId}>Manage Ticket</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 my-6">
            <div>
              <Select onValueChange={setSelectedStatus} value={selectedStatus}>
                <SelectTrigger><SelectValue placeholder="Filter by Status" /></SelectTrigger>
                <SelectContent>{allStatuses.map(status => <SelectItem key={status} value={status}>{status}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div>
              <Select onValueChange={setSelectedMachine} value={selectedMachine}>
                <SelectTrigger><SelectValue placeholder="Filter by Machine" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="All">All</SelectItem>
                  {machines?.map(machine => <SelectItem key={machine.id} value={machine.id}>{machine.name}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>
          <Card>
            <CardHeader><CardTitle>All Maintenance Tickets</CardTitle></CardHeader>
            <CardContent>
              {isLoadingTickets ? <p>Loading...</p> : (
                <Table>
                  <TableHeader><TableRow><TableHead>ID</TableHead><TableHead>Machine</TableHead><TableHead>Category</TableHead><TableHead>Description</TableHead><TableHead>Status</TableHead><TableHead>Logged</TableHead></TableRow></TableHeader>
                  <TableBody>
                    {filteredTickets?.map((ticket) => (
                      <TableRow key={ticket.id} onClick={() => handleTicketSelect(ticket.id)} className="cursor-pointer hover:bg-muted/50">
                        <TableCell>{ticket.id}</TableCell>
                        <TableCell>{getMachineName(ticket.machine_id)}</TableCell>
                        <TableCell>{ticket.incident_category}</TableCell>
                        <TableCell>{ticket.description}</TableCell>
                        <TableCell>{ticket.status}</TableCell>
                        <TableCell>{format(new Date(ticket.logged_time), 'PPP p')}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="log">
          <LogTicketForm onTicketCreated={() => setActiveTab("overview")} />
        </TabsContent>

        <TabsContent value="manage">
          {selectedTicketId ? (
            <TicketDetailView ticketId={selectedTicketId} onClose={handleCloseTicketView} />
          ) : (
            <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed rounded-lg">
              <Search className="h-12 w-12 text-muted-foreground" />
              <p className="text-muted-foreground mt-4">Select a ticket from the overview tab to manage it.</p>
            </div>
          )}
        </TabsContent>

      </Tabs>
    </div>
  );
};

export default MaintenanceHub;