from typing import Dict
from datetime import time
import os
import streamlit as st
import plotly.express as px



ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



class Config:
    # ===== STREAMLIT CONFIGURATION =====
    BASE_URL = st.secrets.get("BASE_URL", "http://backend:8000")

    PLOTLY_COLOR_MAP = px.colors.qualitative.Plotly
    
    # ===== DATA PROCESSOR CONFIGURATION =====
    DAY_SHIFT_START = time(6, 0)
    DAY_SHIFT_END = time(18, 0)

    # Define how FourJaw statuses map to our utilisation categories
    FOURJAW_STATUS_MAP = {
        "production": "Productive Uptime",
        "changeover": "Productive Downtime",
        "setting": "Productive Downtime",
        "idle": "Unproductive Downtime",
        "maintenance": "Unproductive Downtime",
        "breakdown": "Unproductive Downtime"
    }

    FOURJAW_POLLING_INTERVAL_SECONDS = 5
    FOURJAW_HISTORICAL_FETCH_DAYS = 30


    # ===== MACHINE IDENTIFICATION =====
    MACHINE_IDS = [
        '6809f67ffc54c40ff1b489cf', 
        '6809f8df20e024b627b489eb', 
        '6809f8df20e024b627b489ed', 
        '6809f8df20e024b627b489f0', 
        '6809f8df20e024b627b489f2'
    ]
    MACHINE_ID_MAP = {
        '6809f67ffc54c40ff1b489cf': 'Mill 1',
        '6809f8df20e024b627b489eb': 'Mill 2',
        '6809f8df20e024b627b489ed': 'Mill 3',
        '6809f8df20e024b627b489f0': 'Spot 1 (TBC)', 
        '6809f8df20e024b627b489f2': 'Spot 2 (TBC)'
    }
        