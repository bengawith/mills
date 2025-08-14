import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { getMachineData } from '../lib/api';
import { Button } from '../components/ui/Button';
import { LayoutDashboard, LogOut, Settings } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';

export const DashboardPage = () => {
  const { logout, token } = useAuth();
  const [utilisationTrend, setUtilisationTrend] = useState([]);
  const [statusBreakdown, setStatusBreakdown] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleLogout = useCallback(() => {
    logout();
  }, [logout]);

  useEffect(() => {
    const fetchData = async () => {
      if (!token) {
        setError("Authentication token not found.");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const now = new Date();
        const twentyFourHoursAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

        const params = {
          start_time: twentyFourHoursAgo.toISOString(),
          end_time: now.toISOString(),
          machine_ids: ['mill_1', 'mill_2', 'mill_3'],
        };

        const data = await getMachineData(token, params);

        const processedTrend = data.map((item: any) => ({
          name: new Date(item.start_timestamp).toLocaleTimeString(),
          Mill1: item.productivity === 'productive' ? (item.duration_seconds / 60) : 0,
        }));

        const breakdownMap = new Map();
        data.forEach((item: any) => {
          const category = item.utilisation_category || item.classification;
          const duration = item.duration_seconds || 0;
          breakdownMap.set(category, (breakdownMap.get(category) || 0) + duration);
        });

        const processedBreakdown = Array.from(breakdownMap.entries()).map(([name, value]) => {
          let fill = '#cccccc';
          if (name.includes('UPTIME')) fill = '#22c55e';
          else if (name.includes('PRODUCTIVE DOWNTIME')) fill = '#3b82f6';
          else if (name.includes('UNPRODUCTIVE DOWNTIME')) fill = '#ef4444';
          return { name, value, fill };
        });

        setUtilisationTrend(processedTrend);
        setStatusBreakdown(processedBreakdown);

      } catch (err) {
        if (err instanceof Error && err.message === 'Unauthorized') {
          handleLogout();
        } else {
          setError("Failed to fetch machine data.");
          console.error("Error fetching machine data:", err);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [token, handleLogout]);

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
          <Button onClick={logout} variant="outline" className="w-full">
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </aside>

      <main className="flex-1 p-8 overflow-y-auto">
        <h2 className="text-3xl font-bold mb-8">Factory Overview</h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-bold text-lg mb-4">Mill 1 Utilisation Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={utilisationTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis unit="%" />
                <Tooltip />
                <Bar dataKey="Mill1" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-bold text-lg mb-4">Mill 1 Status Breakdown</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={statusBreakdown} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} label>
                    {statusBreakdown.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.fill} />)}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;
