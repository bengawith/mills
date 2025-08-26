import React, { useState } from 'react';
import { useQueries } from '@tanstack/react-query'; // Use useQueries for multiple queries
import { getOeeData, getUtilizationData, getDowntimeAnalysisData } from '@/lib/api'; // Import new functions
import FilterControls from './FilterControls';
import OeeChart from './OeeChart';
import UtilizationChart from './UtilizationChart';
import DowntimeAnalysis from './DowntimeAnalysis';

const Dashboard: React.FC = () => {

  const roundToNearest30Minutes = (date: Date): string => {
    const minutes = date.getMinutes();
    const remainder = minutes % 30;
    const roundedMinutes = remainder > 15 ? minutes + (30 - remainder) : minutes - remainder;
    date.setMinutes(roundedMinutes);
    date.setSeconds(0);
    date.setMilliseconds(0);
    return date.toISOString().replace('Z', '');
  };

  const initialStartTime: string = roundToNearest30Minutes(new Date(new Date().getTime() - (7 * 24 * 60 * 60 * 1000)));
  const initialEndTime: string = roundToNearest30Minutes(new Date(new Date().getTime() + (1 * 24 * 60 * 60 * 1000)));


  const [filters, setFilters] = useState({
    start_time: initialStartTime,
    end_time: initialEndTime,
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
        refetchInterval: 5 * 60 * 1000,
      },
      {
        queryKey: ['utilizationData', filters],
        queryFn: () => getUtilizationData(filters),
        refetchInterval: 5 * 60 * 1000,
      },
      {
        queryKey: ['downtimeAnalysisData', filters],
        queryFn: () => getDowntimeAnalysisData(filters),
        refetchInterval: 5 * 60 * 1000,
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