import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { getOeeData, getUtilizationData, getDowntimeAnalysisData } from '../lib/api';
import { Button, Input, Label, Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../components/ui';
import { LayoutDashboard, LogOut, Settings } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { machineOptions, shiftOptions, dayOfWeekOptions } from '@/assets/constants';

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
              <p>OEE: {oeeData.oee}%</p>
              <p>Availability: {oeeData.availability}%</p>
              <p>Performance: {oeeData.performance}%</p>
              <p>Quality: {oeeData.quality}%</p>
            </div>
          )}

          {/* Utilization Card */}
          {utilizationData && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-bold text-lg mb-4">Utilization</h3>
              <p>Total Time: {Math.round(utilizationData.total_time_seconds / 3600)} hours</p>
              <p>Productive Uptime: {Math.round(utilizationData.productive_uptime_seconds / 3600)} hours</p>
              <p>Unproductive Downtime: {Math.round(utilizationData.unproductive_downtime_seconds / 3600)} hours</p>
              <p>Productive Downtime: {Math.round(utilizationData.productive_downtime_seconds / 3600)} hours</p>
              <p>Utilization Percentage: {utilizationData.utilization_percentage}%</p>
            </div>
          )}

          {/* Downtime Analysis Card */}
          {downtimeAnalysisData && (
            <div className="bg-white p-6 rounded-lg shadow col-span-1 lg:col-span-2 xl:col-span-1">
              <h3 className="font-bold text-lg mb-4">Downtime Analysis</h3>
              <h4 className="font-semibold mb-2">Excessive Downtimes:</h4>
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

              <h4 className="font-semibold mt-4 mb-2">Recurring Downtime Reasons:</h4>
              {Object.keys(downtimeAnalysisData.recurring_downtime_reasons).length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={Object.entries(downtimeAnalysisData.recurring_downtime_reasons).map(([name, value]) => ({ name, value: value as number }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} interval={0} />
                    <YAxis formatter={(value: number) => `${Math.round(value / 3600)} hours`} />
                    <Tooltip formatter={(value: number) => `${Math.round(value / 3600)} hours`} />
                    <Bar dataKey="value" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p>No recurring downtime reasons found.</p>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;
