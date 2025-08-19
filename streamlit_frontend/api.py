import requests

BACKEND_URL = "http://backend:8000"

def login(username, password):
    response = requests.post(
        f"{BACKEND_URL}/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response

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