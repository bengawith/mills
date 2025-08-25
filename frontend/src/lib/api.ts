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
export const getAnalyticalData = async (params: any) => {
  const response = await apiClient.get("/api/v1/dashboard/analytical-data", { params });
  return response.data;
};

export const getMachines = async () => {
  const response = await apiClient.get("/api/v1/machines");
  return response.data;
};

export default apiClient;