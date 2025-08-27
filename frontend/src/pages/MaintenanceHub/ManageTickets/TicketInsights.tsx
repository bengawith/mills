import React, { useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getMaintenanceTickets } from '@/lib/api';
import { useWebSocketEvent } from '@/contexts/WebSocketContext';
import { EventTypes } from '@/lib/websocket-types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { differenceInHours, parseISO } from 'date-fns';
import { AlertTriangle, Clock, CheckCircle } from 'lucide-react';

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

const TicketInsights = () => {
  const queryClient = useQueryClient();

  const { data: tickets, isLoading, error } = useQuery<MaintenanceTicket[]>({ 
    queryKey: ['maintenanceTickets', 'all'], // Fetch all tickets
    queryFn: () => getMaintenanceTickets('all'),
  });

  useWebSocketEvent(EventTypes.TICKET_CREATED, () => {
    queryClient.invalidateQueries({ queryKey: ['maintenanceTickets'] });
  });

  useWebSocketEvent(EventTypes.TICKET_STATUS_CHANGE, () => {
    queryClient.invalidateQueries({ queryKey: ['maintenanceTickets'] });
  });

  const insights = useMemo(() => {
    if (!tickets) {
      return {
        openTickets: 0,
        criticalTickets: 0,
        resolvedToday: 0,
        avgResolutionTime: 'N/A',
      };
    }

    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    const openTickets = tickets.filter(t => t.status === 'Open');
    const criticalTickets = openTickets.filter(t => t.priority === 'High').length;

    const resolvedTickets = tickets.filter(t => t.status === 'Resolved' && t.resolved_time);
    
    const resolvedToday = resolvedTickets.filter(t => parseISO(t.resolved_time!) >= todayStart).length;

    const resolutionTimes = resolvedTickets
      .map(t => differenceInHours(parseISO(t.resolved_time!), parseISO(t.logged_time)))
      .filter(hours => hours >= 0);

    const avgResolutionTime = resolutionTimes.length > 0
      ? (resolutionTimes.reduce((a, b) => a + b, 0) / resolutionTimes.length).toFixed(1) + 'h'
      : 'N/A';

    return {
      openTickets: openTickets.length,
      criticalTickets,
      resolvedToday,
      avgResolutionTime,
    };
  }, [tickets]);

  if (isLoading) {
    return <div>Loading insights...</div>;
  }

  if (error) {
    return <div className="text-red-500">Error loading insights: {error.message}</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Open Tickets</CardTitle>
          <AlertTriangle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-orange-600">
            {insights.openTickets}
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
            {insights.criticalTickets}
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
            {insights.avgResolutionTime}
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
            {insights.resolvedToday}
          </div>
          <p className="text-xs text-muted-foreground">Resolved today</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default TicketInsights;