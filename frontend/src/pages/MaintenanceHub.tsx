import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getMaintenanceTickets, getMachines } from '@/lib/api';
import { MACHINE_ID_MAP } from '@/lib/constants';
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



const MaintenanceHub = () => {
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [selectedMachine, setSelectedMachine] = useState('All');

  const { data: tickets, isLoading, error } = useQuery<MaintenanceTicket[]>({ 
    queryKey: ['maintenanceTickets'],
    queryFn: getMaintenanceTickets,
  });

  const { data: machines, isLoading: isLoadingMachines, error: machinesError } = useQuery({
    queryKey: ['machines'],
    queryFn: getMachines,
  });

  if (isLoading || isLoadingMachines) {
    return <div className="p-4">Loading maintenance tickets...</div>;
  }

  if (error || machinesError) {
    return <div className="p-4 text-red-500">Error loading tickets: {error?.message || machinesError?.message}</div>;
  }

  const filteredTickets = tickets?.filter(ticket => {
    const statusMatch = selectedStatus === 'All' || ticket.status === selectedStatus;
    const machineMatch = selectedMachine === 'All' || ticket.machine_id === selectedMachine;
    return statusMatch && machineMatch;
  });

  const allStatuses = ['All', ...new Set(tickets?.map(ticket => ticket.status))];
  const allMachines = ['All', ...(machines || [])];

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Maintenance Hub</h1>

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
              {allMachines.map(machineId => (
                <SelectItem key={machineId} value={machineId}>
                  {MACHINE_ID_MAP[machineId] || machineId}
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
                  <TableHead>Machine</TableHead> {/* Changed to Machine */}
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
                    <TableCell>{MACHINE_ID_MAP[ticket.machine_id] || ticket.machine_id}</TableCell> {/* Display mapped name */}
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
