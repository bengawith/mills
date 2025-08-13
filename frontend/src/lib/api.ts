const API_BASE_URL = 'http://localhost:8000'; // Your FastAPI backend URL

// Function to handle login
export const loginUser = async (username, password) => {
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
export const getMachineData = async (token, params) => {
  const query = new URLSearchParams(params).toString();
  const response = await fetch(`${API_BASE_URL}/api/v1/machine-data?${query}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch machine data');
  }
  return response.json();
};