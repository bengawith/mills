/*
  TicketInsights.tsx - MillDash Frontend Maintenance Ticket Insights Component

  This file implements the ticket insights section for the MillDash maintenance hub using React and TypeScript. It provides a summary of key maintenance metrics, including open tickets, critical tickets, average resolution time, and tickets resolved today. The component fetches ticket data from the backend, listens for WebSocket events to update in real time, and uses custom UI components for a consistent and accessible layout.

  Key Features:
  - Uses React functional component with memoized insights calculation.
  - Fetches all maintenance tickets using React Query.
  - Listens for ticket creation and status change events via WebSocket for live updates.
  - Calculates open, critical, and resolved tickets, and average resolution time.
  - Displays insights in a responsive grid of cards with Lucide icons.
  - Utilizes custom UI components (Card, CardHeader, CardContent, CardTitle).
  - Responsive and visually appealing layout using Tailwind CSS grid utilities.

  This component is essential for maintenance management, providing users with actionable insights into ticket status and resolution performance.
*/

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
  // React Query client for cache management and invalidation
  const queryClient = useQueryClient();

  /**
   * Fetches all maintenance tickets from the backend API.
   * Uses React Query for caching and loading/error state management.
   */
  const { data: tickets, isLoading, error } = useQuery<MaintenanceTicket[]>({ 
    queryKey: ['maintenanceTickets', 'all'], // Fetch all tickets
    queryFn: () => getMaintenanceTickets('all'),
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
   * Invalidates ticket queries to refetch updated data.
   */
  useWebSocketEvent(EventTypes.TICKET_STATUS_CHANGE, () => {
    queryClient.invalidateQueries({ queryKey: ['maintenanceTickets'] });
  });

  /**
   * Memoized calculation of ticket insights (open, critical, resolved, avg resolution time).
   */
  const insights = useMemo(() => {
    if (!tickets) {
      return {
        openTickets: 0,
        criticalTickets: 0,
        resolvedToday: 0,
        avgResolutionTime: 'N/A',
      };
    }

    const now: Date = new Date();
    const todayStart: Date = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    const openTickets: MaintenanceTicket[] = tickets.filter(t => t.status === 'Open');
    const criticalTickets: number = openTickets.filter(t => t.priority === 'High').length;

    const resolvedTickets: MaintenanceTicket[] = tickets.filter(t => t.status === 'Resolved' && t.resolved_time);
    
    const resolvedToday: number = resolvedTickets.filter(t => parseISO(t.resolved_time!) >= todayStart).length;

    const resolutionTimes: number[] = resolvedTickets
      .map(t => differenceInHours(parseISO(t.resolved_time!), parseISO(t.logged_time)))
      .filter(hours => hours >= 0);

    const avgResolutionTime: string = resolutionTimes.length > 0
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