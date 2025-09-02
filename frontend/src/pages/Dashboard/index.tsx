/*
  index.tsx - MillDash Frontend Dashboard Page

  This file implements the main dashboard page for the MillDash application using React and TypeScript. It provides a comprehensive analytics interface for monitoring machine performance, utilization, OEE, downtime, and real-time metrics. The component leverages optimized backend endpoints and React Query for efficient data fetching, and integrates with WebSocket events for real-time updates.

  Key Features:
  - Uses React functional component with hooks for state management (filters, analytics data).
  - Fetches multiple analytics datasets in parallel using useQueries for performance.
  - Integrates with WebSocket events for real-time dashboard updates.
  - Displays charts and analytics using custom components (OeeChart, UtilizationChart, DowntimeAnalysis, PerformanceMonitor, DashboardOverview).
  - Provides filter controls for time range, machine selection, shift, and day of week.
  - Handles loading and error states gracefully.
  - Responsive and visually appealing layout using Tailwind CSS utility classes.

  This component is the core analytics hub for MillDash, enabling users to monitor and optimize manufacturing operations in real time.
*/

import React, { useState } from 'react';
import { useQueries } from '@tanstack/react-query'; // Use useQueries for multiple queries
import { getOeeData, getUtilizationData, getDowntimeAnalysisData, getRealTimeMetrics, getPerformanceSummary } from '@/lib/api'; // Import optimized functions
import { useDashboardEvents } from '@/contexts/WebSocketContext';
import FilterControls from './FilterControls';
import OeeChart from './OeeChart';
import UtilizationChart from './UtilizationChart';
import DowntimeAnalysis from './DowntimeAnalysis';
import DashboardOverview from './DashboardOverview';
import PerformanceMonitor from './PerformanceMonitor';

const Dashboard: React.FC = () => {

  /**
   * Rounds a date to the nearest 30 minutes for dashboard time filters.
   * @param date - Date object to round
   * @returns ISO string without 'Z'
   */
  const roundToNearest30Minutes = (date: Date): string => {
    const minutes = date.getMinutes();
    const remainder = minutes % 30;
    const roundedMinutes = remainder > 15 ? minutes + (30 - remainder) : minutes - remainder;
    date.setMinutes(roundedMinutes);
    date.setSeconds(0);
    date.setMilliseconds(0);
    return date.toISOString().replace('Z', '');
  };

  // Initial time range for dashboard analytics (last 7 days to tomorrow)
  const initialStartTime: string = roundToNearest30Minutes(new Date(new Date().getTime() - (7 * 24 * 60 * 60 * 1000)));
  const initialEndTime: string = roundToNearest30Minutes(new Date(new Date().getTime() + (1 * 24 * 60 * 60 * 1000)));

  // State for dashboard filter controls
  const [filters, setFilters] = useState<{
    start_time: string;
    end_time: string;
    machine_ids: string;
    shift: string;
    day_of_week: string;
  }>({
    start_time: initialStartTime,
    end_time: initialEndTime,
    machine_ids: 'All',
    shift: 'All',
    day_of_week: 'All',
  });

  // Extract machine IDs for the overview component
  const selectedMachineIds: string[] | undefined = filters.machine_ids === 'All' ? undefined : filters.machine_ids.split(',');

  // Use WebSocket events for real-time updates
  const { lastUpdate } = useDashboardEvents();

  /**
   * Fetches multiple analytics datasets in parallel using useQueries for performance.
   * Each query uses optimized backend endpoints and refetch intervals.
   */
  const results = useQueries({
    queries: [
      {
        queryKey: ['oeeData', filters, lastUpdate],
        queryFn: () => getOeeData(filters),
        refetchInterval: 5 * 60 * 1000,
      },
      {
        queryKey: ['utilizationData', filters, lastUpdate],
        queryFn: () => getUtilizationData(filters),
        refetchInterval: 5 * 60 * 1000,
      },
      {
        queryKey: ['downtimeAnalysisData', filters, lastUpdate],
        queryFn: () => getDowntimeAnalysisData(filters),
        refetchInterval: 5 * 60 * 1000,
      },
      {
        queryKey: ['realTimeMetrics', lastUpdate],
        queryFn: () => getRealTimeMetrics(),
        refetchInterval: 30 * 1000, // More frequent for real-time data
      },
      {
        queryKey: ['performanceSummary', selectedMachineIds, lastUpdate],
        queryFn: () => getPerformanceSummary(selectedMachineIds, 24),
        refetchInterval: 2 * 60 * 1000, // Every 2 minutes for performance summary
      },
    ],
  });

  // Destructure results for each analytics query
  const [oeeResult, utilizationResult, downtimeAnalysisResult, realTimeMetricsResult, performanceSummaryResult] = results;

  // Determine loading and error states for dashboard
  const isLoading: boolean = results.some(result => result.isLoading);
  const isError: boolean = results.some(result => result.isError);

  // Combine optimized analytics data into a single object to pass to chart components
  const dashboardData = {
    oee: oeeResult.data,
    utilization: utilizationResult.data,
    downtimeAnalysis: downtimeAnalysisResult.data,
    realTimeMetrics: realTimeMetricsResult.data,
    performanceSummary: performanceSummaryResult.data,
  };

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-2xl font-bold mb-4">Dashboard - Optimized Analytics</h1>
      
      {/* Dashboard Overview with optimized endpoints */}
      <DashboardOverview machineIds={selectedMachineIds} />
      
      <FilterControls filters={filters} setFilters={setFilters} />
      
      {/* Performance Monitor using optimized analytical data */}
      <PerformanceMonitor filters={filters} />
      
      {isLoading && <p>Loading...</p>}
      {isError && <p>Error loading data</p>}
      {!isLoading && !isError && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <OeeChart data={dashboardData} />
          <UtilizationChart data={dashboardData} />
          <DowntimeAnalysis data={dashboardData} />
        </div>
      )}
    </div>
  );
};

export default Dashboard;