import pandas as pd
from typing import Dict, Any, List


def clean_utilization_data(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        k.strip().removesuffix("_seconds").replace("_", " ").title() + " (hours)": round(v / 3600, 2) 
        for k, v in data.items() 
        if k not in ["utilization_percentage", "total_time_seconds"]
    }


def clean_downtime_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
    name_map: Dict[str, str] = {
        "name": "Name",
        "machine_id": "Machine ID",
        "downtime_reason_name": "Downtime Reason",
        "duration_seconds": "Duration (hours)",
        "start_timestamp": "Start Time",
        "end_timestamp": "End Time"
    }
    renamed_data = [
    {
        name_map[k]: v
        for k, v in dt_data.items()
        if k in name_map
    }
    for dt_data in data
    ]
    renamed_data = pd.DataFrame(renamed_data)
    renamed_data["Start Time"] = pd.to_datetime(renamed_data["Start Time"], format="ISO8601", utc=True)
    renamed_data["End Time"] = pd.to_datetime(renamed_data["End Time"], format="ISO8601", utc=True)
    renamed_data["Duration (hours)"] = round(renamed_data["Duration (hours)"] / 3600, 2)
    return renamed_data