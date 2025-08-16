import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../context/AuthContext'; 
import { getOeeData, getUtilizationData, getDowntimeAnalysisData } from '../lib/api';
import { Button, Input, Label, Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../components/ui';
import { LayoutDashboard, LogOut, Settings } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { machineOptions, shiftOptions, dayOfWeekOptions } from '@/assets/constants';
import { CollapsibleLegend } from '../components/CollapsibleLegend';
import { CustomTooltip } from '../components/CustomTooltip';

const getUtilizationColor = (percentage: number): string => {
  // Define color range: Red (0%) to Green (70%)
  const red = [255, 0, 0]; // RGB for Red
  const green = [0, 150, 0]; // RGB for Green (a darker green for better contrast)

  if (percentage >= 70) {
    return `rgb(${green[0]}, ${green[1]}, ${green[2]})`;
  }

  // Interpolate between red and green based on percentage towards 70%
  // Normalize percentage to a 0-1 scale where 0 is 0% and 1 is 70%
  const normalizedPercentage = Math.min(1, percentage / 70);

  const r = red[0] + normalizedPercentage * (green[0] - red[0]);
  const g = red[1] + normalizedPercentage * (green[1] - red[1]);
  const b = red[2] + normalizedPercentage * (green[2] - red[2]);

  return `rgb(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)})`;
};

export const DashboardPage = () => {
  const { logout, token } = useAuth();
  const [oeeData, setOeeData] = useState<any>(null);
  const [utilizationData, setUtilizationData] = useState<any>(null);
  const [downtimeAnalysisData, setDowntimeAnalysisData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [selectedMachineIds, setSelectedMachineIds] = useState<string[]>([]);
  const [selectedShift, setSelectedShift] = useState<string>('');
  const [selectedDayOfWeek, setSelectedDayOfWeek] = useState<string>('');

  const handleLogout = useCallback(() => {
    logout();
  }, [logout]);

  const fetchDashboardData = useCallback(async () => {
    if (!token) {
      setError("Authentication token not found.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const params: Record<string, any> = {};
      if (startDate) params.start_time = startDate;
      if (endDate) params.end_time = endDate;
      if (selectedMachineIds.length > 0) params.machine_ids = selectedMachineIds;
      if (selectedShift) params.shift = selectedShift;
      if (selectedDayOfWeek) params.day_of_week = selectedDayOfWeek;

      const [oee, utilization, downtime] = await Promise.all([
        getOeeData(token, params),
        getUtilizationData(token, params),
        getDowntimeAnalysisData(token, params),
      ]);

      setOeeData(oee);
      setUtilizationData(utilization);
      setDowntimeAnalysisData(downtime);

    } catch (err) {
      if (err instanceof Error && err.message === 'Unauthorized') {
        handleLogout();
      } else {
        setError("Failed to fetch dashboard data.");
        console.error("Error fetching dashboard data:", err);
      }
    } finally {
      setLoading(false);
    }
  }, [token, startDate, endDate, selectedMachineIds, selectedShift, selectedDayOfWeek, handleLogout]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  if (loading) return <div className="flex justify-center items-center h-screen">Loading dashboard...</div>;
  if (error) return <div className="flex justify-center items-center h-screen text-red-500">Error: {error}</div>;



  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="h-16 flex items-center justify-center border-b">
          <h1 className="text-xl font-bold">Mill Dash</h1>
        </div>
        <nav className="flex-1 px-4 py-6 space-y-2">
          <a href="#" className="flex items-center px-4 py-2 text-gray-700 bg-gray-100 rounded-md">
            <LayoutDashboard className="w-5 h-5 mr-3" />
            Dashboard
          </a>
          <a href="#" className="flex items-center px-4 py-2 text-gray-700 rounded-md hover:bg-gray-100">
            <Settings className="w-5 h-5 mr-3" />
            Settings
          </a>
        </nav>
        <div className="p-4 border-t">
          <Button onClick={handleLogout} variant="outline" className="w-full">
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </aside>

      <main className="flex-1 p-8 overflow-y-auto">
        <h2 className="text-3xl font-bold mb-8">Factory Overview</h2>
        
        {/* Filters Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div>
            <Label htmlFor="startDate">Start Date</Label>
            <Input id="startDate" type="datetime-local" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </div>
          <div>
            <Label htmlFor="endDate">End Date</Label>
            <Input id="endDate" type="datetime-local" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </div>
          <div>
            <Label htmlFor="machineSelect">Machines</Label>
            <Select onValueChange={(value) => setSelectedMachineIds(value ? [value] : [])} value={selectedMachineIds[0] || ''}>
              <SelectTrigger id="machineSelect">
                <SelectValue placeholder="Select Machine" />
              </SelectTrigger>
              <SelectContent>
                {machineOptions.map(option => (
                  <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="shiftSelect">Shift</Label>
            <Select onValueChange={(value) => setSelectedShift(value)} value={selectedShift}>
              <SelectTrigger id="shiftSelect">
                <SelectValue placeholder="Select Shift" />
              </SelectTrigger>
              <SelectContent>
                {shiftOptions.map(option => (
                  <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="dayOfWeekSelect">Day of Week</Label>
            <Select onValueChange={(value) => setSelectedDayOfWeek(value)} value={selectedDayOfWeek}>
              <SelectTrigger id="dayOfWeekSelect">
                <SelectValue placeholder="Select Day" />
              </SelectTrigger>
              <SelectContent>
                {dayOfWeekOptions.map(option => (
                  <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Dashboard Data Display */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
          {/* OEE Card */}
          {oeeData && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-bold text-lg mb-4">Overall Equipment Effectiveness (OEE)</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart
                                    data={[
                    { name: 'OEE', value: oeeData.oee, color: getUtilizationColor(oeeData.oee), fill: getUtilizationColor(oeeData.oee) },
                    { name: 'Availability', value: oeeData.availability, color: getUtilizationColor(oeeData.availability), fill: getUtilizationColor(oeeData.availability) },
                    { name: 'Performance', value: oeeData.performance, color: getUtilizationColor(oeeData.performance), fill: getUtilizationColor(oeeData.performance) },
                    { name: 'Quality', value: oeeData.quality, color: getUtilizationColor(oeeData.quality), fill: getUtilizationColor(oeeData.quality) },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Bar dataKey="value" key="value" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Utilization Card */}
          {utilizationData && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-bold text-lg mb-4">Utilization</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Productive Uptime', value: Math.round(utilizationData.productive_uptime_seconds / 3600), color: '#4CAF50' },
                      { name: 'Productive Downtime', value: Math.round(utilizationData.productive_downtime_seconds / 3600), color: '#2196F3' },
                      { name: 'Unproductive Downtime', value: Math.round(utilizationData.unproductive_downtime_seconds / 3600), color: '#F44336' },
                    ]}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    // label // Removed label prop
                  >
                    <Cell key={`cell-0`} fill="#4CAF50" /> {/* Green */}
                    <Cell key={`cell-1`} fill="#2196F3" /> {/* Blue */}
                    <Cell key={`cell-2`} fill="#F44336" /> {/* Red */}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                  <CollapsibleLegend
                    title="Utilization Legend"
                    payload={[
                      { value: 'Productive Uptime', color: '#4CAF50' },
                      { value: 'Productive Downtime', color: '#2196F3' },
                      { value: 'Unproductive Downtime', color: '#F44336' },
                    ]}
                  />
                </PieChart>
              </ResponsiveContainer>
              <p className="mt-4">Total Time: {Math.round(utilizationData.total_time_seconds / 3600)} hours</p>
              <p className="mt-1">Productive Uptime: {Math.round(utilizationData.productive_uptime_seconds / 3600)} hours</p>
              <p className="mt-1">Unproductive Downtime: {Math.round(utilizationData.unproductive_downtime_seconds / 3600)} hours</p>
              <p className="mt-1">Productive Downtime: {Math.round(utilizationData.productive_downtime_seconds / 3600)} hours</p>
              <p className="mt-1">
                Utilization Percentage:{" "}
                <span style={{ color: getUtilizationColor(utilizationData.utilization_percentage) }}>
                  {utilizationData.utilization_percentage}%
                </span>
              </p>
            </div>
          )}
          {/* Downtime Analysis Card */}
          {downtimeAnalysisData && (
            <div className="bg-white p-6 rounded-lg shadow col-span-1 lg:col-span-2 xl:col-span-1">
              <h3 className="font-bold text-lg mb-4">Downtime Analysis</h3>
              <h4 className="font-semibold mb-2">Excessive Downtimes:</h4>
              <div className="max-h-40 overflow-y-auto"> {/* Added scrollable div */}
                {downtimeAnalysisData.excessive_downtimes.length > 0 ? (
                  <ul>
                    {downtimeAnalysisData.excessive_downtimes.map((d: any, index: number) => (
                      <li key={index}>
                        {d.name}: {d.downtime_reason_name} for {Math.round(d.duration_seconds / 60)} minutes and {Math.round(d.duration_seconds % 60)} seconds
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>No excessive downtimes found.</p>
                )}
              </div>

              <h4 className="font-semibold mt-4 mb-4">Recurring Downtime Reasons:</h4>
              <div className="max-h-80 overflow-y-auto"> {/* Added scrollable div */}
                {Object.keys(downtimeAnalysisData.recurring_downtime_reasons).length > 0 ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={Object.entries(downtimeAnalysisData.recurring_downtime_reasons).map(([name, value], index) => ({ name, value: Math.round(value as number / 3600), color: `hsl(${index * 40}, 75%, 50%)` }))}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {Object.keys(downtimeAnalysisData.recurring_downtime_reasons).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={`hsl(${index * 40}, 75%, 50%)`} /> // Dynamic colors
                        ))}
                      </Pie>
                      <Tooltip content={<CustomTooltip />} />
                      <CollapsibleLegend
                        title="Downtime Reasons Legend"
                        payload={Object.entries(downtimeAnalysisData.recurring_downtime_reasons).map(([name, value], index) => ({
                          value: name,
                          color: `hsl(${index * 40}, 75%, 50%)`
                        }))}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <p>No recurring downtime reasons found.</p>
                )}
              </div>

              <h4 className="font-bold text-lg mb-4 mt-8">Downtime Reasons Bar Chart</h4>
              <div className="max-h-80 overflow-y-auto"> {/* Added scrollable div */}
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart
                    data={Object.entries(downtimeAnalysisData.recurring_downtime_reasons).map(([name, value]) => ({
                      name,
                      duration: Math.round(value as number / 3600) // Convert seconds to hours
                    }))}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" label={{ value: 'Downtime Reason', angle: -90, position: 'insideLeft' }} />
                    <YAxis label={{ value: 'Duration (hours)', angle: -90, position: 'left' }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Bar dataKey="duration" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;
