import React, { useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getMaintenanceTickets } from '@/lib/api';
import { useWebSocketEvent } from '@/contexts/WebSocketContext';
import { EventTypes } from '@/lib/websocket-types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { differenceInHours, parseISO } from 'date-fns';

interface MaintenanceTicket {
  id: number;
  machine_id: string;
  incident_category: string;
  description: string;
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
        resolvedToday: 0,
        avgResolutionTime: 0,
      };
    }

    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    const openTickets = tickets.filter(t => t.status === 'Open').length;

    const resolvedTickets = tickets.filter(t => t.status === 'Resolved' && t.resolved_time);
    
    const resolvedToday = resolvedTickets.filter(t => parseISO(t.resolved_time!) >= todayStart).length;

    const resolutionTimes = resolvedTickets
      .map(t => differenceInHours(parseISO(t.resolved_time!), parseISO(t.logged_time)))
      .filter(hours => hours >= 0);

    const avgResolutionTime = resolutionTimes.length > 0
      ? resolutionTimes.reduce((a, b) => a + b, 0) / resolutionTimes.length
      : 0;

    return {
      openTickets,
      resolvedToday,
      avgResolutionTime: parseFloat(avgResolutionTime.toFixed(1)),
    };
  }, [tickets]);

  if (isLoading) {
    return <div>Loading insights...</div>;
  }

  if (error) {
    return <div className="text-red-500">Error loading insights: {error.message}</div>;
  }

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Ticket Insights</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold">{insights.openTickets}</p>
            <p className="text-sm text-muted-foreground">Open Tickets</p>
          </div>
          <div>
            <p className="text-2xl font-bold">{insights.resolvedToday}</p>
            <p className="text-sm text-muted-foreground">Resolved Today</p>
          </div>
          <div>
            <p className="text-2xl font-bold">{insights.avgResolutionTime}h</p>
            <p className="text-sm text-muted-foreground">Avg. Resolution Time</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default TicketInsights;
