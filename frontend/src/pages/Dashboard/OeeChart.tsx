import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface OeeChartProps {
  data: any;
}

// A simplified diverging color scale, similar to RdYlGn
const COLOR_SCALE = [
  '#d73027', // Red for low values
  '#fc8d59',
  '#fee090',
  '#e0f3f8',
  '#91bfdb',
  '#4575b4', // Blue for high values
];

const get_color = (value: number): string => {
  // Assuming a target of 70% for OEE, Availability, Performance, Quality
  // Normalize value to a 0-1 scale based on a max of 100 (percentage)
  const normalised_percentage = Math.min(1, Math.max(0, value / 100));
  const color_index = Math.floor(normalised_percentage * (COLOR_SCALE.length - 1));
  return COLOR_SCALE[color_index];
};

const OeeChart: React.FC<OeeChartProps> = ({ data }) => {
  const oeeData = [
    { name: 'OEE', value: data.oee?.oee || 0 },
    { name: 'Availability', value: data.oee?.availability || 0 },
    { name: 'Performance', value: data.oee?.performance || 0 },
    { name: 'Quality', value: data.oee?.quality || 0 },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>OEE (Overall Equipment Effectiveness)</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={oeeData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 100]} /> {/* Assuming values are percentages */}
            <Tooltip />
            <Legend />
            <Bar dataKey="value">
              {oeeData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={get_color(entry.value)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default OeeChart;