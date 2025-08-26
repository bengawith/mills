import axios from 'axios';

const API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_URL, // Update with Django production url
  headers: {
    'Content-Type': 'application/json',
  },
});

const shouldAttachAuth = (url) => {
  const excludedPaths = [
    '/auth/users/',
    '/auth/users/activation/', // Exclude the activation endpoint
    '/auth/users/reset_password_confirm/'
  ];
  
  // Return false if it's explicitly excluded
  if (excludedPaths.includes(url)) {
    return false;
  }
  
  return true;
};

// Add a request interceptor to include the auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token && shouldAttachAuth(config.url)) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Dashboard Endpoints
export const getAnalyticalData = async (rawParams: any) => {
  const params = {
    start_time: rawParams.start_time,
    end_time: rawParams.end_time,
    machine_ids: rawParams.machine_ids === "All" ? undefined : rawParams.machine_ids,
    shift: rawParams.shift === "All" ? undefined : rawParams.shift,
    day_of_week: rawParams.day_of_week === "All" ? undefined : rawParams.day_of_week,
  };
  const response = await apiClient.get("/api/v1/dashboard/analytical-data", { params });
  return response.data;
};

// NEW: Optimized analytical data endpoint
export const getAnalyticalDataOptimized = async (rawParams: any) => {
  const params = {
    start_time: rawParams.start_time,
    end_time: rawParams.end_time,
    machine_ids: rawParams.machine_ids === "All" ? undefined : rawParams.machine_ids,
    shift: rawParams.shift === "All" ? undefined : rawParams.shift,
    day_of_week: rawParams.day_of_week === "All" ? undefined : rawParams.day_of_week,
  };
  const response = await apiClient.get("/api/v1/dashboard/analytical-data-optimized", { params });
  return response.data;
};

// NEW: Machine summary endpoint
export const getMachineSummary = async (machineIds?: string[]) => {
  const params = machineIds && machineIds.length > 0 && !machineIds.includes("All") ? { machine_ids: machineIds } : {};
  const response = await apiClient.get("/api/v1/dashboard/machine-summary", { params });
  return response.data;
};

// NEW: Production metrics endpoint
export const getProductionMetrics = async (rawParams: any) => {
  const params = {
    start_time: rawParams.start_time,
    end_time: rawParams.end_time,
    machine_ids: rawParams.machine_ids === "All" ? undefined : rawParams.machine_ids,
  };
  const response = await apiClient.get("/api/v1/dashboard/production-metrics", { params });
  return response.data;
};

// NEW: Maintenance overview endpoint
export const getMaintenanceOverview = async (machineIds?: string[]) => {
  const params = machineIds && machineIds.length > 0 && !machineIds.includes("All") ? { machine_ids: machineIds } : {};
  const response = await apiClient.get("/api/v1/dashboard/maintenance-overview", { params });
  return response.data;
};

// NEW: Quick stats endpoint
export const getQuickStats = async () => {
  const response = await apiClient.get("/api/v1/dashboard/quick-stats");
  return response.data;
};

export const getOeeData = async (rawParams: any) => {
  const params = {
    start_time: rawParams.start_time,
    end_time: rawParams.end_time,
    machine_ids: rawParams.machine_ids === "All" ? undefined : rawParams.machine_ids,
    shift: rawParams.shift === "All" ? undefined : rawParams.shift,
    day_of_week: rawParams.day_of_week === "All" ? undefined : rawParams.day_of_week,
  };
  const response = await apiClient.get("/api/v1/analytics/oee-optimized", { params });
  return response.data;
};

export const getUtilizationData = async (rawParams: any) => {
  const params = {
    start_time: rawParams.start_time,
    end_time: rawParams.end_time,
    machine_ids: rawParams.machine_ids === "All" ? undefined : rawParams.machine_ids,
    shift: rawParams.shift === "All" ? undefined : rawParams.shift,
    day_of_week: rawParams.day_of_week === "All" ? undefined : rawParams.day_of_week,
  };
  const response = await apiClient.get("/api/v1/analytics/utilization-optimized", { params });
  return response.data;
};

export const getDowntimeAnalysisData = async (rawParams: any) => {
  const params = {
    start_time: rawParams.start_time,
    end_time: rawParams.end_time,
    machine_ids: rawParams.machine_ids === "All" ? undefined : rawParams.machine_ids,
    shift: rawParams.shift === "All" ? undefined : rawParams.shift,
    day_of_week: rawParams.day_of_week === "All" ? undefined : rawParams.day_of_week,
  };
  const response = await apiClient.get("/api/v1/analytics/downtime-analysis-optimized", { params });
  return response.data;
};

export const getMachines = async () => {
  const response = await apiClient.get("/api/v1/machines");
  return response.data;
};

// Maintenance Endpoints
export const getMaintenanceTickets = async (status: string = 'Open') => {
  const response = await apiClient.get("/api/v1/tickets", { params: { status } });
  return response.data;
};

export const createMaintenanceTicket = async (payload: any) => {
  const response = await apiClient.post("/api/v1/tickets", payload);
  return response.data;
};

export const getTicketDetails = async (ticketId: number) => {
  const response = await apiClient.get(`/api/v1/tickets/${ticketId}`);
  return response.data;
};

export const updateTicketStatus = async (ticketId: number, newStatus: string) => {
  const response = await apiClient.put(`/api/v1/tickets/${ticketId}`, null, { params: { status: newStatus } });
  return response.data;
};

export const addWorkNote = async (ticketId: number, note: any) => {
  const response = await apiClient.post(`/api/v1/tickets/${ticketId}/notes`, note);
  return response.data;
};

export const uploadTicketImage = async (ticketId: number, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post(`/api/v1/tickets/${ticketId}/upload-image`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getInventoryComponents = async () => {
  const response = await apiClient.get("/api/v1/inventory/components");
  return response.data;
};

export const addComponentToTicket = async (ticketId: number, componentId: number, quantity: number) => {
  const response = await apiClient.post(`/api/v1/tickets/${ticketId}/components`, null, { params: { component_id: componentId, quantity_used: quantity } });
  return response.data;
};

export const getRecentDowntimes = async (machineId: string, startTime: string, endTime: string) => {
  const response = await apiClient.get("/api/v1/fourjaw/downtimes", { params: { machine_id: machineId, start_time: startTime, end_time: endTime } });
  return response.data;
};

// Production Run Endpoints
export const getProducts = async () => {
  const response = await apiClient.get("/api/v1/products");
  return response.data;
};

export const getActiveRunForMachine = async (machineId: string) => {
  const response = await apiClient.get(`/api/v1/runs/active/${machineId}`);
  return response.data;
};

export const startProductionRun = async (payload: { machine_id: string; product_id: number }) => {
  const response = await apiClient.post("/api/v1/runs", payload);
  return response.data;
};

export const completeProductionRun = async (payload: { run_id: number; scrap_length: number }) => {
  const response = await apiClient.put(`/api/v1/runs/${payload.run_id}/complete`, { scrap_length: payload.scrap_length });
  return response.data;
};

// NEW: Advanced Analytics Optimized Endpoints
export const getRealTimeMetrics = async () => {
  const response = await apiClient.get("/api/v1/analytics/real-time-metrics");
  return response.data;
};

export const getPerformanceSummary = async (machineIds?: string[], hoursBack: number = 24) => {
  const params: any = { hours_back: hoursBack };
  if (machineIds && machineIds.length > 0 && !machineIds.includes("All")) {
    params.machine_ids = machineIds;
  }
  const response = await apiClient.get("/api/v1/analytics/performance-summary", { params });
  return response.data;
};

export const getTrendsData = async (machineIds?: string[], daysBack: number = 7, interval: string = "daily") => {
  const params: any = { days_back: daysBack, interval };
  if (machineIds && machineIds.length > 0 && !machineIds.includes("All")) {
    params.machine_ids = machineIds;
  }
  const response = await apiClient.get("/api/v1/analytics/trends", { params });
  return response.data;
};

export const getMachineComparison = async (metric: string = "utilization", startTime?: string, endTime?: string) => {
  const params: any = { metric };
  if (startTime) params.start_time = startTime;
  if (endTime) params.end_time = endTime;
  const response = await apiClient.get("/api/v1/analytics/machine-comparison", { params });
  return response.data;
};

export const getEfficiencyInsights = async (machineIds?: string[], hoursBack: number = 168) => {
  const params: any = { hours_back: hoursBack };
  if (machineIds && machineIds.length > 0 && !machineIds.includes("All")) {
    params.machine_ids = machineIds;
  }
  const response = await apiClient.get("/api/v1/analytics/efficiency-insights", { params });
  return response.data;
};

export default apiClient;