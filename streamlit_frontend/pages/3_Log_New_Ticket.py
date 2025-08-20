import streamlit as st
import pandas as pd
from api import create_maintenance_ticket, get_recent_downtimes, upload_ticket_image
from config import Config
from datetime import datetime, timedelta

st.set_page_config(page_title="Maintenance Hub", layout="wide", page_icon="🔧")

st.title("➕ Log New Maintenance Incident")

# --- Authentication Check ---
if 'token' not in st.session_state or st.session_state.token is None:
    st.warning("Please log in to access this page.")
    st.page_link("app.py", label="Go to Login")
    st.stop()

# --- Form for Logging a New Ticket ---
with st.form("log_ticket_form", clear_on_submit=True):
    st.header("Incident Details")

    # --- Input Fields ---
    col1, col2 = st.columns(2)
    with col1:
        machine_name = st.selectbox(
            "Machine*",
            options=[""] + list(Config.MACHINE_ID_MAP.values()),
            index=0,
            key="selected_machine" # Use a key to access the value outside the form if needed
        )
        incident_category = st.selectbox(
            "Incident Category*",
            options=["", "Mechanical", "Electrical", "Tooling", "Hydraulic", "Software", "Other"]
        )
        priority = st.selectbox(
            "Priority*",
            options=["Low", "Medium", "High"],
            index=1 # Default to Medium
        )

    with col2:
        description = st.text_area("Description of Incident*", height=150)

    st.info("To link this ticket to a specific downtime, select a machine above. Recent downtimes will appear below.")

    # --- Dynamic Downtime Linking ---
    downtime_events = []
    if machine_name:
        machine_id = next((mid for mid, mname in Config.MACHINE_ID_MAP.items() if mname == machine_name), None)
        if machine_id:
            with st.spinner(f"Fetching recent downtimes for {machine_name}..."):
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=1)
                downtime_events = get_recent_downtimes(machine_id, start_time, end_time)
    
    selected_downtime_id = None
    
    # --- FIX #1: Check if downtime_events is a valid list of dictionaries ---
    # This prevents the TypeError if the API returns an error or an empty list.
    if isinstance(downtime_events, list) and downtime_events:
        # Create a mapping from a user-friendly display string to the event ID
        downtime_options = {
            f"{evt.get('start_timestamp', 'N/A')} ({int(evt.get('duration_seconds', 0)/60)} mins) - {evt.get('downtime_reason_name', 'N/A')}": evt.get('id')
            for evt in downtime_events
        }
        
        # Add a "None" option to allow users to not link any event
        downtime_display_options = ["None"] + list(downtime_options.keys())
        
        selected_downtime_display = st.selectbox(
            "Link to FourJaw Downtime Event (Optional)",
            options=downtime_display_options
        )
        if selected_downtime_display != "None":
            selected_downtime_id = downtime_options[selected_downtime_display]
    elif machine_name:
        st.write("No recent downtime events found for the selected machine.")

    # --- Image Upload ---
    uploaded_image = st.file_uploader("Upload Image (Optional)", type=["png", "jpg", "jpeg"])

    # --- FIX #2: Add the required st.form_submit_button ---
    submitted = st.form_submit_button("Submit Ticket", type="primary")

    if submitted:
        # Validation
        if not machine_name or not incident_category or not description:
            st.error("Please fill out all required fields (*).")
        else:
            machine_id_to_submit = next((mid for mid, mname in Config.MACHINE_ID_MAP.items() if mname == machine_name), None)
            
            payload = {
                "incident_category": incident_category,
                "description": description,
                "priority": priority,
                "status": "Open", # Default status
                "machine_id": machine_id_to_submit,
                "fourjaw_downtime_id": selected_downtime_id
            }
            
            with st.spinner("Creating ticket..."):
                new_ticket = create_maintenance_ticket(payload)
            
            if new_ticket and uploaded_image:
                with st.spinner("Uploading image..."):
                    # Pass the actual ticket ID from the response
                    upload_ticket_image(new_ticket['id'], uploaded_image)

            if new_ticket:
                st.success(f"Successfully created Ticket #{new_ticket['id']}!")
                st.balloons()


st.page_link("pages/2_Maintenance_Hub.py", label="Back to Maintenance Hub", icon="⬅️")
