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

export const getOeeData = async (rawParams: any) => {
  const params = {
    start_time: rawParams.start_time,
    end_time: rawParams.end_time,
    machine_ids: rawParams.machine_ids === "All" ? undefined : rawParams.machine_ids,
    shift: rawParams.shift === "All" ? undefined : rawParams.shift,
    day_of_week: rawParams.day_of_week === "All" ? undefined : rawParams.day_of_week,
  };
  const response = await apiClient.get("/api/v1/oee", { params });
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
  const response = await apiClient.get("/api/v1/utilization", { params });
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
  const response = await apiClient.get("/api/v1/downtime-analysis", { params });
  return response.data;
};

export const getMachines = async () => {
  const response = await apiClient.get("/api/v1/machines");
  return response.data;
};

export default apiClient;