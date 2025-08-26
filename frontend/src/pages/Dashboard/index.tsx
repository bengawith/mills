import React, { useState } from 'react';
import { useQueries } from '@tanstack/react-query'; // Use useQueries for multiple queries
import { getOeeData, getUtilizationData, getDowntimeAnalysisData } from '@/lib/api'; // Import new functions
import FilterControls from './FilterControls';
import OeeChart from './OeeChart';
import UtilizationChart from './UtilizationChart';
import DowntimeAnalysis from './DowntimeAnalysis';

const Dashboard: React.FC = () => {
  const today: string = new Date().toISOString().replace('Z', '')

  const [filters, setFilters] = useState({
    start_time: '2025-05-05T00:00:00',
    end_time: today,
    machine_ids: 'All',
    shift: 'All',
    day_of_week: 'All',
  });



  // Use useQueries to fetch data from multiple endpoints
  const results = useQueries({
    queries: [
      {
        queryKey: ['oeeData', filters],
        queryFn: () => getOeeData(filters),
      },
      {
        queryKey: ['utilizationData', filters],
        queryFn: () => getUtilizationData(filters),
      },
      {
        queryKey: ['downtimeAnalysisData', filters],
        queryFn: () => getDowntimeAnalysisData(filters),
      },
    ],
  });

  const [oeeResult, utilizationResult, downtimeAnalysisResult] = results;

  const isLoading = results.some(result => result.isLoading);
  const isError = results.some(result => result.isError);

  // Combine data into a single object to pass to chart components
  const dashboardData = {
    oee: oeeResult.data,
    utilization: utilizationResult.data,
    downtimeAnalysis: downtimeAnalysisResult.data,
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <FilterControls filters={filters} setFilters={setFilters} />
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