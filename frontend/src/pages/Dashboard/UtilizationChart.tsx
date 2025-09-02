/*
  UtilizationChart.tsx - MillDash Frontend Utilization Chart Component

  This file implements the utilization chart for the MillDash dashboard using React, TypeScript, and Recharts. It visualizes productive and unproductive machine time as a pie chart, providing insights into operational efficiency. The component receives analytics data as props and renders a responsive, interactive chart with tooltips, legends, and custom UI components.

  Key Features:
  - Uses React functional component with typed props for utilization analytics data.
  - Visualizes productive uptime, productive downtime, and unproductive downtime as pie chart segments.
  - Custom tooltip displays segment name, value, and color.
  - Custom legend shows segment breakdown and percentage.
  - Responsive layout using Recharts ResponsiveContainer.
  - Utilizes custom UI components (Card, CardHeader, CardContent, CardTitle).
  - Accessible and visually appealing chart for dashboard analytics.

  This component is essential for monitoring machine utilization and identifying opportunities for operational improvement.
*/

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface UtilizationChartProps {
  // Analytics data object containing utilization metrics
  data: {
    utilization?: {
      productive_uptime_seconds: number;
      productive_downtime_seconds: number;
      unproductive_downtime_seconds: number;
      total_time_seconds: number;
      utilization_percentage: number;
    };
  };
}

const COLORS = ['#00C49F', '#0088FE', '#FF8042']; // Green, Blue, Orange

const CustomTooltip = ({ active, payload }: any) => {
  /**
   * Custom tooltip for utilization chart segments.
   * Displays segment name, value, and color.
   */
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="p-2 bg-white border border-gray-300 rounded shadow-lg">
        <p style={{ color: payload[0].color, fontWeight: 'bold' }}>{`${data.name}: ${data.value.toFixed(2)} hours`}</p>
      </div>
    );
  }
  return null;
};

const renderLegend = (props: any) => {
  /**
   * Custom legend for utilization chart segments.
   * Displays segment name, color, and percentage of total time.
   */
  const { payload } = props;
  return (
    <ul style={{ listStyle: 'none', padding: 0 }}>
      {
        payload.map((entry: any, index: number) => (
          <li key={`item-${index}`} style={{ color: entry.color, marginBottom: '4px' }}>
            <span style={{ display: 'inline-block', marginRight: '10px', width: '10px', height: '10px', backgroundColor: entry.color }}></span>
            {entry.value} ({((entry.payload.value / (props.data.utilization.total_time_seconds / 3600)) * 100).toFixed(2)}%)
          </li>
        ))
      }
    </ul>
  );
};


const UtilizationChart: React.FC<UtilizationChartProps> = ({ data }) => {
  // Extract utilization metrics from analytics data
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

  // Prepare chart data for pie chart rendering
  const chartData: { name: string; value: number }[] = [
    { name: 'Productive Uptime', value: utilizationData.productive_uptime_seconds / 3600 },
    { name: 'Productive Downtime', value: utilizationData.productive_downtime_seconds / 3600 },
    { name: 'Unproductive Downtime', value: utilizationData.unproductive_downtime_seconds / 3600 },
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
              nameKey="name"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend content={(props) => renderLegend({ ...props, data })} />
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
