/*
  OeeChart.tsx - MillDash Frontend OEE Chart Component

  This file implements the OEE (Overall Equipment Effectiveness) chart for the MillDash dashboard using React, TypeScript, and Recharts. It visualizes key OEE metrics (OEE, Availability, Performance, Quality) as a bar chart, using a diverging color scale to highlight performance levels. The component receives analytics data as props and renders a responsive, interactive chart with tooltips and custom UI components.

  Key Features:
  - Uses React functional component with typed props for analytics data.
  - Visualizes OEE, Availability, Performance, and Quality as bars.
  - Applies a diverging color scale to indicate metric performance.
  - Custom tooltip displays metric value and color.
  - Responsive layout using Recharts ResponsiveContainer.
  - Utilizes custom UI components (Card, CardHeader, CardContent, CardTitle).
  - Accessible and visually appealing chart for dashboard analytics.

  This component is essential for monitoring manufacturing effectiveness and identifying areas for improvement.
*/

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Label } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface OeeChartProps {
  // Analytics data object containing OEE metrics
  data: {
    oee?: {
      oee?: number;
      availability?: number;
      performance?: number;
      quality?: number;
    };
  };
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

const getColor = (value: number): string => {
  /**
   * Returns a color from the diverging scale based on the metric value.
   * Normalizes value to a 0-1 scale (max 100%) and selects color.
   * @param value - Metric value (percentage)
   */
  const normalised_percentage: number = Math.min(1, Math.max(0, value / 100));
  const colorIndex: number = Math.floor(normalised_percentage * (COLOR_SCALE.length - 1));
  return COLOR_SCALE[colorIndex];
};

const CustomTooltip = ({ active, payload, label }: any) => {
  /**
   * Custom tooltip for OEE chart bars.
   * Displays metric name, value, and color.
   */
  if (active && payload && payload.length) {
    const value: number = payload[0].value;
    const color: string = getColor(value);
    return (
      <div className="p-2 bg-white border border-gray-300 rounded shadow-lg">
        <p style={{ color: color, fontWeight: 'bold' }}>{`${label}: ${value.toFixed(2)}%`}</p>
      </div>
    );
  }
  return null;
};

const OeeChart: React.FC<OeeChartProps> = ({ data }) => {
  // Prepare OEE metrics for chart rendering
  const oeeData: { name: string; value: number }[] = [
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
            <YAxis domain={[0, 100]}>
              <Label value="Percentage (%)" angle={-90} position="insideLeft" style={{ textAnchor: 'middle' }} />
            </YAxis>
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="value">
              {oeeData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(entry.value)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default OeeChart;