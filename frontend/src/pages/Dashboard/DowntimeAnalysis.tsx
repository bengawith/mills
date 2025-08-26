import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Label } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

interface DowntimeAnalysisProps {
  data: any;
}

const COLOR_SCALE = [
  '#d73027', // Red for high values
  '#fc8d59',
  '#fee090',
  '#e0f3f8',
  '#91bfdb',
  '#4575b4', // Blue for low values
].reverse();

const getColor = (value: number, maxValue: number): string => {
  const normalised_percentage = Math.min(1, Math.max(0, value / maxValue));
  const colorIndex = Math.floor(normalised_percentage * (COLOR_SCALE.length - 1));
  return COLOR_SCALE[colorIndex];
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const value = payload[0].value;
    const color = payload[0].fill;
    return (
      <div className="p-2 bg-white border border-gray-300 rounded shadow-lg">
        <p style={{ color: color, fontWeight: 'bold' }}>{`${label}: ${value.toFixed(2)} hours`}</p>
      </div>
    );
  }
  return null;
};

const DowntimeAnalysis: React.FC<DowntimeAnalysisProps> = ({ data }) => {
  const excessiveDowntimes = data.downtimeAnalysis?.excessive_downtimes || [];
  const recurringDowntimeReasons = data.downtimeAnalysis?.recurring_downtime_reasons || {};

  const recurringData = Object.keys(recurringDowntimeReasons).map(key => ({
    name: key,
    value: recurringDowntimeReasons[key] / 3600, // Convert seconds to hours
  }));

  const maxValue = Math.max(...recurringData.map(d => d.value), 0);

  return (
    <Card className="col-span-2">
      <CardHeader>
        <CardTitle>Downtime Analysis</CardTitle>
      </CardHeader>
      <CardContent>
        <h3 className="text-lg font-semibold mb-2">Excessive Downtimes</h3>
        <div className="max-h-60 overflow-y-auto mb-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Machine Name</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>Duration (hours)</TableHead>
                <TableHead>Start Time</TableHead>
                <TableHead>End Time</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {excessiveDowntimes.length > 0 ? (
                excessiveDowntimes.map((downtime: any, index: number) => (
                  <TableRow key={index}>
                    <TableCell>{downtime.name}</TableCell>
                    <TableCell>{downtime.downtime_reason_name}</TableCell>
                    <TableCell>{(downtime.duration_seconds / 3600).toFixed(2)}</TableCell>
                    <TableCell>{new Date(downtime.start_timestamp).toLocaleString()}</TableCell>
                    <TableCell>{new Date(downtime.end_timestamp).toLocaleString()}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} className="text-center">No excessive downtimes found.</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>

        <h3 className="text-lg font-semibold mb-2">Recurring Downtime Reasons</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={recurringData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis>
              <Label value="Total Duration (hours)" angle={-90} position="insideLeft" style={{ textAnchor: 'middle' }} />
            </YAxis>
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="value">
              {recurringData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(entry.value, maxValue)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default DowntimeAnalysis;
