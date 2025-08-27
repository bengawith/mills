import { useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getMaintenanceTickets } from '@/lib/api';
import { useWebSocketEvent } from '@/contexts/WebSocketContext';
import { EventTypes } from '@/lib/websocket-types';
import { differenceInHours, parseISO } from 'date-fns';

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

export const useTicketInsights = () => {
  const queryClient = useQueryClient();

  const { data: tickets, isLoading, error } = useQuery<MaintenanceTicket[]>({ 
    queryKey: ['maintenanceTickets', 'all'],
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

  return { insights, isLoading, error };
};