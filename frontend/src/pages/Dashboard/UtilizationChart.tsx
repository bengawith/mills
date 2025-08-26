import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface UtilizationChartProps {
  data: any;
}

const COLORS = ['#00C49F', '#0088FE', '#FF8042']; // Green, Blue, Orange

const CustomTooltip = ({ active, payload }: any) => {
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
