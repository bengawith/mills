from datetime import datetime
import requests
import streamlit as st

# Read the backend URL from Streamlit secrets or default to localhost
# In a deployed environment, you would set BACKEND_URL in your secrets.
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://backend:8000")


# --- Authentication Endpoints ---
def login(username, password):
    """Authenticates the user and returns a JWT token."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Login failed: {e}")
        return None


def get_auth_headers():
    """Constructs the authorization headers if a token exists in session state."""
    if "token" not in st.session_state or st.session_state.token is None:
        st.error("You are not logged in.")
        return None
    return {"Authorization": f"Bearer {st.session_state.token}"}


# --- Dashboard Endpoints ---
def get_oee_data(token, params):
    response = requests.get(
        f"{BACKEND_URL}/api/v1/oee",
        headers={"Authorization": f"Bearer {token}"},
        params=params
    )
    return response


def get_utilization_data(token, params):
    response = requests.get(
        f"{BACKEND_URL}/api/v1/utilization",
        headers={"Authorization": f"Bearer {token}"},
        params=params
    )
    return response


def get_downtime_analysis_data(token, params):
    response = requests.get(
        f"{BACKEND_URL}/api/v1/downtime-analysis",
        headers={"Authorization": f"Bearer {token}"},
        params=params
    )
    return response


def get_machines(token):
    response = requests.get(
        f"{BACKEND_URL}/api/v1/machines",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response


def get_shifts(token):
    response = requests.get(
        f"{BACKEND_URL}/api/v1/shifts",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response


def get_days_of_week(token):
    response = requests.get(
        f"{BACKEND_URL}/api/v1/days-of-week",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response


# --- Production Endpoints ---
def get_products():
    """Fetches a list of all products."""
    headers = get_auth_headers()
    if not headers: return []
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/products", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch products: {e}")
        return []


def start_production_run(machine_id: str, product_id: int):
    """Starts a new production run."""
    headers = get_auth_headers()
    if not headers: return None
    try:
        payload = {"machine_id": machine_id, "product_id": product_id}
        response = requests.post(f"{BACKEND_URL}/api/v1/runs", headers=headers, json=payload)
        response.raise_for_status()
        st.success("Successfully started new production run!")
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to start run: {e}")
        return None


def complete_production_run(run_id: int, scrap_length: float):
    """Completes a production run and logs scrap."""
    headers = get_auth_headers()
    if not headers: return None
    try:
        payload = {"status": "COMPLETED", "scrap_length": scrap_length}
        response = requests.put(f"{BACKEND_URL}/api/v1/runs/{run_id}/complete", headers=headers, json=payload)
        response.raise_for_status()
        st.success("Successfully completed production run!")
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to complete run: {e}")
        return None


def get_active_runs():
    """Fetches all currently active production runs."""
    # Note: Your current backend doesn't have a dedicated endpoint for this.
    # We will need to add one. For now, this is a placeholder.
    # A real implementation would be: GET /api/v1/runs?status=ACTIVE
    st.warning("Fetching active runs is not yet implemented in the backend.")
    return []


# --- Maintenance & Inventory Endpoints ---
def get_maintenance_tickets():
    """Fetches all maintenance tickets."""
    headers = get_auth_headers()
    if not headers: return []
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/tickets", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch tickets: {e}")
        return []


def create_maintenance_ticket(payload: dict):
    """Creates a new maintenance ticket."""
    headers = get_auth_headers()
    if not headers: return None
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/tickets", headers=headers, json=payload)
        response.raise_for_status()
        st.success("Successfully created maintenance ticket!")
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to create ticket: {e}")
        return None


def get_inventory_components():
    """Fetches all repair components from inventory."""
    headers = get_auth_headers()
    if not headers: return []
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/inventory/components", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch inventory: {e}")
        return []
    

def get_recent_downtimes(machine_id: str, start_time: datetime, end_time: datetime):
    """Fetches recent FourJaw downtimes for the ticket logging form."""
    headers = get_auth_headers()
    if not headers: return []
    try:
        params = {
            "machine_id": machine_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        response = requests.get(f"{BACKEND_URL}/api/v1/fourjaw/downtimes", headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch downtimes: {e}")
        return []


def upload_ticket_image(ticket_id: int, uploaded_file):
    """Uploads an image for a specific maintenance ticket."""
    headers = get_auth_headers()
    if not headers: return None
    try:
        files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post(f"{BACKEND_URL}/api/v1/tickets/{ticket_id}/upload-image", headers=headers, files=files)
        response.raise_for_status()
        st.success("Image uploaded successfully!")
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to upload image: {e}")
        return None
