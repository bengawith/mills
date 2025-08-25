import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getAnalyticalData } from '@/lib/api';
import FilterControls from './FilterControls';
import OeeChart from './OeeChart';
import UtilizationChart from './UtilizationChart';
import DowntimeAnalysis from './DowntimeAnalysis';

const Dashboard: React.FC = () => {
  const [filters, setFilters] = useState({
    start_time: '2023-01-01T00:00:00',
    end_time: '2023-01-31T23:59:59',
    machine_ids: 'mill_1,mill_2',
    shift: 'All',
    day_of_week: 'All',
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['analyticalData', filters],
    queryFn: () => getAnalyticalData(filters),
  });

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <FilterControls filters={filters} setFilters={setFilters} />
      {isLoading && <p>Loading...</p>}
      {error && <p>Error loading data</p>}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <OeeChart data={data} />
          <UtilizationChart data={data} />
          <DowntimeAnalysis data={data} />
        </div>
      )}
    </div>
  );
};

export default Dashboard;
