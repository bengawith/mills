import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getMaintenanceTickets, getMachines, getMaintenanceOverview } from '@/lib/api';
import { useMaintenanceEvents } from '@/contexts/WebSocketContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { format } from 'date-fns';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'; // Import Select components
import { AlertTriangle, Clock, CheckCircle, Wrench, Bell } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface MaintenanceTicket {
    id: number;
    machine_id: string;
    incident_category: string;
    description: string;
    status: string;
    logged_time: string;
    resolved_time: string | null;
}

const MaintenanceHub = () => {
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [selectedMachine, setSelectedMachine] = useState('All');

  // Use WebSocket events for real-time maintenance updates
  const { alerts, ticketUpdates } = useMaintenanceEvents();

  // Fetch maintenance overview using optimized endpoint
  const { data: maintenanceOverview, isLoading: overviewLoading } = useQuery({
    queryKey: ['maintenanceOverview'],
    queryFn: () => getMaintenanceOverview(),
    refetchInterval: 30 * 1000, // Refresh every 30 seconds
  });

  const { data: tickets, isLoading, error } = useQuery<MaintenanceTicket[]>({ 
    queryKey: ['maintenanceTickets'],
    queryFn: () => getMaintenanceTickets(),
  });

  const { data: machines, isLoading: isLoadingMachines, error: machinesError } = useQuery<{id: string, name: string}[]>({
    queryKey: ['machines'],
    queryFn: getMachines,
  });

  if (isLoading || isLoadingMachines) {
    return <div className="p-4">Loading maintenance tickets...</div>;
  }

  if (error || machinesError) {
    return <div className="p-4 text-red-500">Error loading tickets: {error?.message || (machinesError as any)?.message}</div>;
  }

  const filteredTickets = tickets?.filter(ticket => {
    const statusMatch = selectedStatus === 'All' || ticket.status === selectedStatus;
    const machineMatch = selectedMachine === 'All' || ticket.machine_id === selectedMachine;
    return statusMatch && machineMatch;
  });

  const allStatuses = ['All', ...new Set(tickets?.map(ticket => ticket.status) || [])];
  
  const getMachineName = (machineId: string) => {
    const machine = machines?.find(m => m.id === machineId);
    return machine ? machine.name : machineId;
  };

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-2xl font-bold mb-4">Maintenance Hub</h1>

      {/* Maintenance Overview Cards using optimized endpoint */}
      {!overviewLoading && maintenanceOverview && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Open Tickets</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {maintenanceOverview.open_tickets || 0}
              </div>
              <p className="text-xs text-muted-foreground">Require attention</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Critical Tickets</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {maintenanceOverview.critical_tickets || 0}
              </div>
              <p className="text-xs text-muted-foreground">High priority</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Resolution</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {maintenanceOverview.avg_resolution_time || 'N/A'}
              </div>
              <p className="text-xs text-muted-foreground">Hours to resolve</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed Today</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {maintenanceOverview.completed_today || 0}
              </div>
              <p className="text-xs text-muted-foreground">Resolved today</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Real-time Alerts Section */}
      {alerts.length > 0 && (
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-800">
              <Bell className="h-5 w-5" />
              Recent Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {alerts.slice(0, 3).map((alert, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
                  <div>
                    <p className="font-medium">Ticket #{alert.ticket_id}</p>
                    <p className="text-sm text-muted-foreground">{alert.description}</p>
                  </div>
                  <div className="text-right">
                    <Badge variant={alert.priority === 'Critical' ? 'destructive' : 'secondary'}>
                      {alert.priority}
                    </Badge>
                    <p className="text-xs text-muted-foreground">{alert.machine_id}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <Select onValueChange={setSelectedStatus} value={selectedStatus}>
            <SelectTrigger>
              <SelectValue placeholder="Filter by Status" />
            </SelectTrigger>
            <SelectContent>
              {allStatuses.map(status => (
                <SelectItem key={status} value={status}>{status}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Select onValueChange={setSelectedMachine} value={selectedMachine}>
            <SelectTrigger>
              <SelectValue placeholder="Filter by Machine" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="All">All</SelectItem>
              {machines?.map(machine => (
                <SelectItem key={machine.id} value={machine.id}>
                  {machine.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Maintenance Tickets</CardTitle>
        </CardHeader>
        <CardContent>
          {filteredTickets && filteredTickets.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Machine</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Logged Time</TableHead>
                  <TableHead>Resolved Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTickets.map((ticket) => (
                  <TableRow key={ticket.id}>
                    <TableCell>{ticket.id}</TableCell>
                    <TableCell>{getMachineName(ticket.machine_id)}</TableCell>
                    <TableCell>{ticket.incident_category}</TableCell>
                    <TableCell>{ticket.description}</TableCell>
                    <TableCell>{ticket.status}</TableCell>
                    <TableCell>{format(new Date(ticket.logged_time), 'PPP p')}</TableCell>
                    <TableCell>
                      {ticket.resolved_time 
                        ? format(new Date(ticket.resolved_time), 'PPP p') 
                        : 'N/A'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p>No maintenance tickets found.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default MaintenanceHub;
