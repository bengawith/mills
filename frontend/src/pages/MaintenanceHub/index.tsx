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
  const [activeTab, setActiveTab] = useState("overview");
  const [selectedTicketId, setSelectedTicketId] = useState<number | null>(null);
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [selectedMachine, setSelectedMachine] = useState('All');
  const queryClient = useQueryClient();

  // Data Fetching
  const { data: tickets, isLoading: isLoadingTickets } = useQuery<MaintenanceTicket[]>({ 
    queryKey: ['maintenanceTickets', 'all'],
    queryFn: () => getMaintenanceTickets('all'),
  });

  const { data: machines, isLoading: isLoadingMachines } = useQuery<{id: string, name: string}[]>({
    queryKey: ['machines'],
    queryFn: getMachines,
  });

  // WebSocket events
  useWebSocketEvent(EventTypes.TICKET_CREATED, () => {
    queryClient.invalidateQueries({ queryKey: ['maintenanceTickets'] });
  });

  useWebSocketEvent(EventTypes.TICKET_STATUS_CHANGE, () => {
    queryClient.invalidateQueries({ queryKey: ['maintenanceTickets'] });
    if (selectedTicketId) {
      queryClient.invalidateQueries({ queryKey: ['ticketDetails', selectedTicketId] });
    }
  });

  const filteredTickets = useMemo(() => {
    if (!tickets) return [];
    return tickets.filter(ticket => {
      const statusMatch = selectedStatus === 'All' || ticket.status === selectedStatus;
      const machineMatch = selectedMachine === 'All' || ticket.machine_id === selectedMachine;
      return statusMatch && machineMatch;
    });
  }, [tickets, selectedStatus, selectedMachine]);

  const handleTicketSelect = (ticketId: number) => {
    setSelectedTicketId(ticketId);
    setActiveTab("manage");
  }

  const handleCloseTicketView = () => {
    setSelectedTicketId(null);
    setActiveTab("overview");
  }

  const getMachineName = (machineId: string) => {
    const machine = machines?.find(m => m.id === machineId);
    return machine ? machine.name : machineId;
  };

  const allStatuses = ['All', ...new Set(tickets?.map(ticket => ticket.status) || [])];

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