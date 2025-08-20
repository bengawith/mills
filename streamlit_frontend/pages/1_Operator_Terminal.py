import streamlit as st
import pandas as pd
from api import get_products, start_production_run, complete_production_run, get_active_runs
from config import Config

st.set_page_config(layout="wide")

st.title("👨‍🏭 Operator Terminal")

# Check for login token
if 'token' not in st.session_state or st.session_state.token is None:
    st.warning("Please log in to access this page.")
    st.page_link("app.py", label="Go to Login")
    st.stop()

# --- Page Layout ---
col1, col2 = st.columns(2, gap="large")


# --- Column 1: Start a New Production Run ---
with col1:
    st.header("Start New Job")
    
    # Fetch data needed for the forms
    try:
        products = get_products()
        machines = Config.MACHINE_ID_MAP
    except Exception as e:
        st.error(f"Could not load initial data: {e}")
        products = []
        machines = {}

    if not products or not machines:
        st.warning("No products or machines found. Please add them via the API or check configuration.")
    else:
        with st.form("start_run_form"):
            # Form fields
            machine_name = st.selectbox(
                "Select Machine",
                options=list(machines.values()),
                key="start_machine"
            )
            product_name = st.selectbox(
                "Select Product",
                options=[p['product_name'] for p in products],
                key="start_product"
            )
            
            submitted = st.form_submit_button("Start Job", type="primary")

            if submitted:
                # Find the corresponding IDs from the names
                machine_id = next((mid for mid, mname in machines.items() if mname == machine_name), None)
                product_id = next((p['id'] for p in products if p['product_name'] == product_name), None)

                if machine_id and product_id:
                    with st.spinner("Starting run..."):
                        start_production_run(machine_id=machine_id, product_id=product_id)
                        # We would ideally refresh the active runs list here
                else:
                    st.error("Could not find ID for selected machine or product.")


# --- Column 2: Complete an Active Job ---
with col2:
    st.header("End Active Job")
    
    # Fetch active runs to populate the dropdown
    # NOTE: This is a placeholder until the backend endpoint is created
    active_runs = get_active_runs() 

    if not active_runs:
        st.info("No active production runs found.")
    else:
        # Create a display name for the selectbox
        run_options = {f"{run['id']}: {Config.MACHINE_ID_MAP.get(run['machine_id'])} - {run['product']['product_name']}": run['id'] for run in active_runs}
        
        with st.form("end_run_form"):
            selected_run_display = st.selectbox(
                "Select Active Run to Complete",
                options=list(run_options.keys())
            )
            scrap_length = st.number_input("Enter Scrap Length (meters)", min_value=0.0, step=0.1, format="%.2f")
            
            end_submitted = st.form_submit_button("End Job & Log Scrap", type="primary")

            if end_submitted:
                run_id_to_complete = run_options[selected_run_display]
                with st.spinner("Completing run..."):
                    complete_production_run(run_id=run_id_to_complete, scrap_length=scrap_length)
                    # Refresh the page or active runs list
                    st.rerun()


st.divider()
st.subheader("Current Active Runs")
# Display a table of active runs
if active_runs:
    df = pd.DataFrame(active_runs)
    st.dataframe(df, use_container_width=True)
else:
    st.write("No active jobs.")
