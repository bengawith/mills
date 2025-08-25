import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';

const Dashboard = () => {
  const [startTime, setStartTime] = useState('2023-01-01T00:00:00');
  const [endTime, setEndTime] = useState('2023-01-31T23:59:59');
  const [machineIds, setMachineIds] = useState('mill_1,mill_2'); // Hardcoded for now

  const { data, isLoading, error } = useQuery({
    queryKey: ['analyticalData', startTime, endTime, machineIds],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/dashboard/analytical-data', {
        params: {
          start_time: startTime,
          end_time: endTime,
          machine_ids: machineIds,
        },
      });
      return response.data;
    },
  });

  if (isLoading) {
    return <div className="p-4">Loading dashboard data...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">Error loading dashboard data: {error.message}</div>;
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Date Range</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="startTime">Start Time</Label>
              <Input
                id="startTime"
                type="datetime-local"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="endTime">End Time</Label>
              <Input
                id="endTime"
                type="datetime-local"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Machine IDs</CardTitle>
          </CardHeader>
          <CardContent>
            <Label htmlFor="machineIds">Machine IDs (comma-separated)</Label>
            <Input
              id="machineIds"
              type="text"
              value={machineIds}
              onChange={(e) => setMachineIds(e.target.value)}
              placeholder="e.g., mill_1,mill_2"
            />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Analytical Data</CardTitle>
        </CardHeader>
        <CardContent>
          {data && data.length > 0 ? (
            <pre className="bg-gray-100 p-4 rounded-md overflow-auto text-sm">
              {JSON.stringify(data, null, 2)}
            </pre>
          ) : (
            <p>No data available for the selected filters.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;