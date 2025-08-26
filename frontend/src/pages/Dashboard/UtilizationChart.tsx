import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface UtilizationChartProps {
  data: any;
}

const COLORS = ['#00C49F', '#0088FE', '#FF8042']; // Green, Blue, Orange

const UtilizationChart: React.FC<UtilizationChartProps> = ({ data }) => {
  const utilizationData = data.utilization;

  if (!utilizationData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Utilization</CardTitle>
        </CardHeader>
        <CardContent>
          <p>No utilization data available.</p>
        </CardContent>
      </Card>
    );
  }

  const chartData = [
    { name: 'Productive Uptime', value: Math.round(utilizationData.productive_uptime_seconds / 36 ) / 100 },
    { name: 'Productive Downtime', value: Math.round(utilizationData.productive_downtime_seconds / 36 ) / 100 },
    { name: 'Unproductive Downtime', value: Math.round(utilizationData.unproductive_downtime_seconds / 36 ) / 100 },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Utilization</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
        <div className="mt-4 text-sm">
          <p><strong>Total Time:</strong> {(utilizationData.total_time_seconds / 3600).toFixed(2)} hours</p>
          <p><strong>Productive Uptime:</strong> {(utilizationData.productive_uptime_seconds / 3600).toFixed(2)} hours</p>
          <p><strong>Productive Downtime:</strong> {(utilizationData.productive_downtime_seconds / 3600).toFixed(2)} hours</p>
          <p><strong>Unproductive Downtime:</strong> {(utilizationData.unproductive_downtime_seconds / 3600).toFixed(2)} hours</p>
          <p><strong>Utilization Percentage:</strong> {utilizationData.utilization_percentage.toFixed(2)}%</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default UtilizationChart;
