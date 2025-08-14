const API_BASE_URL = 'http://localhost:8000'; // Your FastAPI backend URL

// Function to handle login
export const loginUser = async (username: string, password: string) => {
  const response = await fetch(`${API_BASE_URL}/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username, password }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to login');
  }
  return response.json();
};

// Function to fetch protected data
export const getMachineData = async (token: string, params: Record<string, string>) => {
  const query = new URLSearchParams(params).toString();
  const response = await fetch(`${API_BASE_URL}/api/v1/machine-data?${query}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (response.status === 401) {
    throw new Error('Unauthorized');
  }
  if (!response.ok) {
    throw new Error('Failed to fetch machine data');
  }
  return response.json();
};

// Function to fetch OEE data
export const getOeeData = async (token: string, params: Record<string, any>) => {
  const query = new URLSearchParams(params).toString();
  const response = await fetch(`${API_BASE_URL}/api/v1/oee?${query}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (response.status === 401) {
    throw new Error('Unauthorized');
  }
  if (!response.ok) {
    throw new Error('Failed to fetch OEE data');
  }
  return response.json();
};

// Function to fetch Utilization data
export const getUtilizationData = async (token: string, params: Record<string, any>) => {
  const query = new URLSearchParams(params).toString();
  const response = await fetch(`${API_BASE_URL}/api/v1/utilization?${query}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (response.status === 401) {
    throw new Error('Unauthorized');
  }
  if (!response.ok) {
    throw new Error('Failed to fetch utilization data');
  }
  return response.json();
};

// Function to fetch Downtime Analysis data
export const getDowntimeAnalysisData = async (token: string, params: Record<string, any>) => {
  const query = new URLSearchParams(params).toString();
  const response = await fetch(`${API_BASE_URL}/api/v1/downtime-analysis?${query}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (response.status === 401) {
    throw new Error('Unauthorized');
  }
  if (!response.ok) {
    throw new Error('Failed to fetch downtime analysis data');
  }
  return response.json();
};