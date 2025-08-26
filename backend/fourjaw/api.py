import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from const import Config

class FourJaw:
    """
    A client for interacting with the FourJaw API.
    """
    def __init__(self):
        self._api_key: str = config.API_KEY
        self.base_url: str = config.BASE_URL
        self.client: httpx.Client = httpx.Client(
            headers=config.SECURE_HEADER,
            base_url=self.base_url
        )


    def make_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """
        Method for making requests to the FourJaw API.
        """
        url = f"{self.base_url}{endpoint}"
        response = self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response


    def get_machines(self) -> dict:
        """Gets all machines from the /machines endpoint."""
        response = self.client.get("/machines")
        response.raise_for_status()
        return response.json()


    def get_machine_count(self) -> int:
        """Gets the number of machines from the /machines/count endpoint."""
        response = self.client.get("/machines/count")
        response.raise_for_status()
        return response.json()


    def get_n_machines(self, machine_id: str) -> dict:
        """Gets len(machine_id) machines by their FourJaw machine ID."""
        params = {"machine_ids": machine_id}
        response = self.client.get("/machines", params=params)
        response.raise_for_status()
        return response.json()


    def get_status_periods(self, start_time: str, end_time: str, machine_ids: list[str] | str = None, page_size: int = 1000, page: int = 1) -> dict:
        """
        Gets time entries between a specified start and end time.
        """
        if isinstance(machine_ids, list):
            formatted_machine_ids = ",".join(machine_ids)
        else:
            formatted_machine_ids = machine_ids

        params = {
            "asset_ids": formatted_machine_ids,
            "start_timestamp": start_time,
            "end_timestamp": end_time,
            "page_size": page_size
        }
        
        response = self.client.get("/status-periods", params=params)
        response.raise_for_status()
        return response.json()


    def get_settings(self) -> dict:
        """Gets all settings from the /settings endpoint."""
        response = self.client.get("/settings")
        response.raise_for_status()
        return response.json()
