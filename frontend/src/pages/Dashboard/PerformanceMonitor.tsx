import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getAnalyticalDataOptimized } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Clock, TrendingUp, TrendingDown, Activity } from 'lucide-react';

interface PerformanceMonitorProps {
  filters: {
    start_time: string;
    end_time: string;
    machine_ids: string;
    shift: string;
    day_of_week: string;
  };
}

const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({ filters }) => {
  const [activeTab, setActiveTab] = useState('overview');

  const { data: analyticalData, isLoading, isError } = useQuery({
    queryKey: ['analyticalDataOptimized', filters],
    queryFn: () => getAnalyticalDataOptimized(filters),
    refetchInterval: 2 * 60 * 1000, // Refresh every 2 minutes
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Performance Monitor</CardTitle>
          <CardDescription>Loading optimized analytics...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isError || !analyticalData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Performance Monitor</CardTitle>
          <CardDescription>Error loading analytics data</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Unable to load performance data. Please try again.</p>
        </CardContent>
      </Card>
    );
  }

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getTrendIcon = (trend: number) => {
    if (trend > 0) return <TrendingUp className="h-4 w-4 text-green-600" />;
    if (trend < 0) return <TrendingDown className="h-4 w-4 text-red-600" />;
    return <Activity className="h-4 w-4 text-gray-600" />;
  };

  const getTrendColor = (trend: number) => {
    if (trend > 0) return 'text-green-600';
    if (trend < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Performance Monitor
        </CardTitle>
        <CardDescription>
          Real-time analytics with optimized data processing
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="efficiency">Efficiency</TabsTrigger>
            <TabsTrigger value="downtime">Downtime</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {analyticalData.total_records || 0}
                </div>
                <div className="text-sm text-muted-foreground">Total Records</div>
              </div>
              
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {analyticalData.machines_count || 0}
                </div>
                <div className="text-sm text-muted-foreground">Machines</div>
              </div>

              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {analyticalData.avg_utilization ? formatPercentage(analyticalData.avg_utilization) : 'N/A'}
                </div>
                <div className="text-sm text-muted-foreground">Avg Utilization</div>
              </div>

              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {analyticalData.total_downtime_minutes ? formatDuration(analyticalData.total_downtime_minutes) : 'N/A'}
                </div>
                <div className="text-sm text-muted-foreground">Total Downtime</div>
              </div>
            </div>

            {analyticalData.time_range && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
                <span>
                  Data from {new Date(analyticalData.time_range.start).toLocaleDateString()} to{' '}
                  {new Date(analyticalData.time_range.end).toLocaleDateString()}
                </span>
              </div>
            )}
          </TabsContent>

          <TabsContent value="efficiency" className="space-y-4">
            {analyticalData.efficiency_trends && (
              <div className="space-y-3">
                <h4 className="font-medium">Efficiency Trends</h4>
                {Object.entries(analyticalData.efficiency_trends).map(([metric, data]: [string, any]) => (
                  <div key={metric} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-2">
                      {getTrendIcon(data.trend)}
                      <span className="capitalize">{metric.replace('_', ' ')}</span>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{formatPercentage(data.current)}</div>
                      <div className={`text-sm ${getTrendColor(data.trend)}`}>
                        {data.trend > 0 ? '+' : ''}{formatPercentage(data.trend)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="downtime" className="space-y-4">
            {analyticalData.downtime_analysis && (
              <div className="space-y-3">
                <h4 className="font-medium">Downtime Analysis</h4>
                {analyticalData.downtime_analysis.map((item: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <div className="font-medium">{item.reason || 'Unknown'}</div>
                      <div className="text-sm text-muted-foreground">
                        Machine: {item.machine_id || 'N/A'}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{formatDuration(item.duration_minutes)}</div>
                      <Badge variant={item.severity === 'high' ? 'destructive' : 'secondary'}>
                        {item.severity || 'normal'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>

        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center gap-2 text-sm text-green-800">
            <TrendingUp className="h-4 w-4" />
            <span className="font-medium">Optimized Performance:</span>
            <span>Using pre-computed analytics for faster loading</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default PerformanceMonitor;
