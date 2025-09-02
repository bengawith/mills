/*
  DashboardOverview.tsx - MillDash Frontend Dashboard Overview Component

  This file implements the dashboard overview section for the MillDash application using React and TypeScript. It provides a summary of key metrics and machine statuses, integrating with backend APIs and custom hooks for optimized data fetching. The component displays quick stats, machine status, and maintenance insights, using custom UI components for a consistent and visually appealing layout.

  Key Features:
  - Uses React functional component with props for machine filtering.
  - Fetches quick stats, machine summaries, and maintenance insights using React Query and custom hooks.
  - Displays loading skeletons while data is being fetched.
  - Renders quick stats cards for total machines, active machines, open tickets, and average utilization.
  - Shows machine status overview with icons and color coding for operational state and utilization.
  - Presents maintenance insights including critical tickets, average resolution time, and tickets completed today.
  - Utilizes custom UI components (Card, CardHeader, CardContent, CardTitle, CardDescription) and Lucide icons.
  - Responsive layout using Tailwind CSS grid utilities.

  This component is a key part of the dashboard, providing users with a high-level summary of manufacturing operations and maintenance health.
*/

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getQuickStats, getMachineSummary } from '@/lib/api';
import { useTicketInsights } from '@/hooks/useTicketInsights';
import { MACHINE_ID_MAP } from '@/lib/constants';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, AlertTriangle, CheckCircle, Clock, Cog, TrendingUp } from 'lucide-react';

interface QuickStatsProps {
  machineIds?: string[];
}

const DashboardOverview: React.FC<QuickStatsProps> = ({ machineIds }) => {
  /**
   * Fetches quick stats for the dashboard (total machines, active machines, avg utilization).
   * Uses React Query for caching and refetching every 30 seconds.
   */
  const { data: quickStats, isLoading: statsLoading } = useQuery({
    queryKey: ['quickStats'],
    queryFn: getQuickStats,
    refetchInterval: 30 * 1000, // Refresh every 30 seconds
  });

  /**
   * Fetches machine summary for the dashboard (status, utilization, etc.).
   * Uses React Query for caching and refetching every 30 seconds.
   */
  const { data: machineSummary, isLoading: machineLoading } = useQuery({
    queryKey: ['machineSummary', machineIds],
    queryFn: () => getMachineSummary(machineIds),
    refetchInterval: 30 * 1000,
  });

  /**
   * Fetches maintenance ticket insights using a custom hook.
   * Returns open, critical, resolved tickets and average resolution time.
   */
  const { insights: maintenanceOverview, isLoading: maintenanceLoading } = useTicketInsights();

  // Combined loading state for all queries
  const isLoading: boolean = statsLoading || machineLoading || maintenanceLoading;

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="pb-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-full"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  /**
   * Returns a Tailwind color class for a given machine status string.
   * @param status - Machine status string
   */
  const getStatusColor = (status: string): string => {
    switch (status?.toLowerCase()) {
      case 'running':
      case 'operational':
        return 'text-green-600';
      case 'idle':
      case 'warning':
        return 'text-yellow-600';
      case 'down':
      case 'maintenance':
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  /**
   * Returns a Lucide icon component for a given machine status string.
   * @param status - Machine status string
   */
  const getStatusIcon = (status: string): JSX.Element => {
    switch (status?.toLowerCase()) {
      case 'running':
      case 'operational':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'idle':
      case 'warning':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'down':
      case 'maintenance':
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Quick Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Machines</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{quickStats?.total_machines || 0}</div>
            <p className="text-xs text-muted-foreground">
              Across all production lines
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Machines</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {quickStats?.active_machines || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Currently running
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Tickets</CardTitle>
            <Cog className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {maintenanceOverview?.openTickets || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Maintenance required
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Utilization</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {quickStats?.avg_utilization ? `${(quickStats.avg_utilization * 100).toFixed(1)}%` : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              Last 24 hours
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Machine Status Overview */}
      {machineSummary && machineSummary.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Machine Status Overview</CardTitle>
            <CardDescription>
              Current status of all machines
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {machineSummary.map((machine: any, index: number) => (
                <div
                  key={MACHINE_ID_MAP[machine.machine_id] || index}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(machine.status)}
                    <div>
                      <p className="font-medium">{machine.machine_name || MACHINE_ID_MAP[machine.machine_id]}</p>
                      <p className={`text-sm ${getStatusColor(machine.status)}`}>
                        {machine.status || 'Unknown'}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">
                      {machine.utilization ? `${(machine.utilization * 100).toFixed(1)}%` : 'N/A'}
                    </p>
                    <p className="text-xs text-muted-foreground">Utilization</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Maintenance Overview */}
      {maintenanceOverview && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Critical Tickets</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {maintenanceOverview.criticalTickets || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                High priority maintenance
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Avg Resolution Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {maintenanceOverview.avgResolutionTime || 'N/A'}
              </div>
              <p className="text-xs text-muted-foreground">
                Hours to resolve
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Completed Today</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {maintenanceOverview.resolvedToday || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                Tickets resolved
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default DashboardOverview;
