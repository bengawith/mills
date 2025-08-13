import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';
import { LayoutDashboard, LogOut, Settings } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadialBarChart, RadialBar, PieChart, Pie, Cell
} from 'recharts';

// Mock data based on your example images
const mockUtilisationTrend = [
  { name: '00:00', Mill1: 18 }, { name: '03:00', Mill1: 55 }, { name: '06:00', Mill1: 40 },
  { name: '09:00', Mill1: 80 }, { name: '12:00', Mill1: 25 }, { name: '15:00', Mill1: 65 },
  { name: '18:00', Mill1: 78 }, { name: '21:00', Mill1: 82 },
];

const mockStatusBreakdown = [
  { name: 'Uptime', value: 65, fill: '#22c55e' },
  { name: 'Productive Downtime', value: 10, fill: '#3b82f6' },
  { name: 'Unproductive Downtime', value: 25, fill: '#ef4444' },
];

export const DashboardPage = () => {
  const { logout } = useAuth();

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
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

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-y-auto">
        <h2 className="text-3xl font-bold mb-8">Factory Overview</h2>
        
        {/* Grid for charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Example Chart 1: Utilisation Trend */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-bold text-lg mb-4">Mill 1 Utilisation Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={mockUtilisationTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis unit="%" />
                <Tooltip />
                <Bar dataKey="Mill1" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Example Chart 2: Utilisation Readout */}
           <div className="bg-white p-6 rounded-lg shadow flex flex-col items-center justify-center">
            <h3 className="font-bold text-lg mb-4">Mill 1 Utilisation Readout</h3>
             <ResponsiveContainer width="100%" height={300}>
                <RadialBarChart 
                    innerRadius="70%" 
                    outerRadius="100%" 
                    data={[{name: 'Utilisation', value: 57.7, fill: '#8884d8'}]} 
                    startAngle={90} 
                    endAngle={-270}
                >
                    <RadialBar minAngle={15} background clockWise={true} dataKey='value' />
                    <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" className="text-4xl font-bold">
                        57.7%
                    </text>
                </RadialBarChart>
            </ResponsiveContainer>
          </div>

          {/* Example Chart 3: Status Breakdown */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-bold text-lg mb-4">Mill 1 Status Breakdown</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={mockStatusBreakdown} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} label>
                    {mockStatusBreakdown.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.fill} />)}
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