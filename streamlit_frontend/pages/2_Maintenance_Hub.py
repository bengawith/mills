import streamlit as st
import pandas as pd
from api import get_maintenance_tickets
from config import Config

st.set_page_config(layout="wide")

st.title("🔧 Maintenance Hub")

# --- Authentication Check ---
if 'token' not in st.session_state or st.session_state.token is None:
    st.warning("Please log in to access this page.")
    st.page_link("app.py", label="Go to Login")
    st.stop()

# --- Page Content ---

# Button to navigate to the form for logging a new ticket
st.page_link("pages/3_Log_New_Ticket.py", label="Log New Incident", icon="➕")

st.divider()

# --- Fetch and Display Tickets ---
st.header("All Maintenance Tickets")

try:
    with st.spinner("Fetching maintenance tickets..."):
        tickets_data = get_maintenance_tickets()

    if not tickets_data:
        st.info("No maintenance tickets found.")
        st.stop()

    # Convert to DataFrame for easier manipulation and display
    df = pd.DataFrame(tickets_data)

    # --- Interactive Filters ---
    st.sidebar.header("Filter Tickets")
    
    # Filter by Status
    status_options = ["All"] + df['status'].unique().tolist()
    selected_status = st.sidebar.selectbox("Filter by Status", options=status_options)

    # Filter by Machine
    machine_options = ["All"] + list(Config.MACHINE_ID_MAP.values())
    selected_machine_name = st.sidebar.selectbox("Filter by Machine", options=machine_options)

    # Apply filters to the DataFrame
    filtered_df = df.copy()
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df['status'] == selected_status]

    if selected_machine_name != "All":
        # Map machine name back to ID for filtering
        machine_id = next((mid for mid, mname in Config.MACHINE_ID_MAP.items() if mname == selected_machine_name), None)
        if machine_id:
            filtered_df = filtered_df[filtered_df['machine_id'] == machine_id]

    # --- Display Table ---
    if filtered_df.empty:
        st.write("No tickets match the current filters.")
    else:
        # Improve display by mapping machine_id to name
        filtered_df['machine_name'] = filtered_df['machine_id'].map(Config.MACHINE_ID_MAP)
        
        # Select and reorder columns for a cleaner view
        display_columns = [
            'id', 'status', 'priority', 'machine_name', 
            'incident_category', 'description', 'logged_time'
        ]
        st.dataframe(
            filtered_df[display_columns],
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("Ticket ID"),
                "logged_time": st.column_config.DatetimeColumn(
                    "Logged Time",
                    format="DD/MM/YYYY HH:mm"
                ),
            }
        )

except Exception as e:
    st.error(f"An error occurred while fetching data: {e}")

