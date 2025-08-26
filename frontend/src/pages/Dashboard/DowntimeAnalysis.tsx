import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

interface DowntimeAnalysisProps {
  data: any;
}

const DowntimeAnalysis: React.FC<DowntimeAnalysisProps> = ({ data }) => {
  const excessiveDowntimes = data.downtimeAnalysis?.excessive_downtimes || [];
  const recurringDowntimeReasons = data.downtimeAnalysis?.recurring_downtime_reasons || {};

  const recurringData = Object.keys(recurringDowntimeReasons).map(key => ({
    name: key,
    value: Math.round(recurringDowntimeReasons[key] / 36) / 100, // Convert seconds to hours with 2 d.p.
  }));

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
                <TableHead>Machine ID</TableHead>
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
                    <TableCell>{downtime.machine_id}</TableCell>
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
            <YAxis label={{ value: 'Hours', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Bar dataKey="value" fill="#82ca9d" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default DowntimeAnalysis;
