import streamlit as st
import pandas as pd
from api import (
    get_maintenance_tickets, 
    get_ticket_details,
    get_inventory_components,
    update_ticket_status,
    add_work_note,
    add_component_to_ticket
)
from config import Config
from datetime import datetime

st.set_page_config(layout="wide")

st.title("📝 Manage Maintenance Ticket")

# --- Authentication Check ---
if 'token' not in st.session_state or st.session_state.token is None:
    st.warning("Please log in to access this page.")
    st.page_link("app.py", label="Go to Login")
    st.stop()

# --- Ticket Selection ---
st.header("1. Select a Ticket to Manage")

try:
    with st.spinner("Fetching open tickets..."):
        all_tickets = get_maintenance_tickets()
    
    if not all_tickets:
        st.info("No maintenance tickets found.")
        st.stop()

    # Filter for tickets that are not resolved yet
    open_tickets = [t for t in all_tickets if t.get('status') != 'Resolved']

    if not open_tickets:
        st.success("🎉 No open maintenance tickets!")
        st.stop()

    # Create a user-friendly display for the selectbox
    ticket_options = {
        f"#{t.get('id')} - {Config.MACHINE_ID_MAP.get(t.get('machine_id'))} - {t.get('description', 'No Description')[:50]}...": t.get('id')
        for t in open_tickets
    }
    
    selected_ticket_display = st.selectbox(
        "Choose an open ticket",
        options=list(ticket_options.keys())
    )
    
    selected_ticket_id = ticket_options[selected_ticket_display]

except Exception as e:
    st.error(f"An error occurred while fetching tickets: {e}")
    st.stop()


st.divider()

# --- Ticket Details Display & Interaction ---
if selected_ticket_id:
    st.header(f"2. Viewing and Updating Ticket #{selected_ticket_id}")

    # Fetch the full details for the selected ticket
    ticket_details: dict = get_ticket_details(selected_ticket_id)

    if not ticket_details:
        st.error("Could not fetch details for the selected ticket.")
        st.stop()

    # --- Layout for Ticket Details ---
    col1, col2 = st.columns([2, 1]) # Make the first column wider

    with col1:
        st.subheader("Ticket Information")
        # Display key details in a metric-like format
        info_col1, info_col2, info_col3, info_col4 = st.columns(4)
        info_col1.metric("Status", ticket_details.get('status'))
        info_col2.metric("Priority", ticket_details.get('priority'))
        info_col3.metric("Machine", Config.MACHINE_ID_MAP.get(ticket_details.get('machine_id')))
        info_col4.metric("Category", ticket_details.get('incident_category'))
        
        st.markdown("**Description:**")
        st.info(ticket_details.get('description'))

        # --- Display Work Notes ---
        st.subheader("Work Notes Log")
        work_notes = ticket_details.get('work_notes', [])
        if not work_notes:
            st.write("No work notes yet.")
        else:
            for note in sorted(work_notes, key=lambda x: x['created_at'], reverse=True):
                st.markdown(f"**{note['author']}** ({pd.to_datetime(note['created_at']).strftime('%d/%m/%Y %H:%M')}):")
                st.text(note['note'])
        
        # --- Display Images ---
        st.subheader("Attached Images")
        images = ticket_details.get('images', [])
        if not images:
            st.write("No images attached.")
        else:
            # Create columns for a nice gallery view
            image_cols = st.columns(len(images))
            for idx, img in enumerate(images):
                with image_cols[idx]:
                    st.write(f"Image #{idx+1} {img}")
                    # IMPORTANT: In production, you'd serve these images from a static file server (like Nginx)
                    # For local development with Docker, we need to construct the correct URL to the backend service.
                    image_url = f"http://localhost:8000/{img['image_url']}"
                    uploaded_at = img.get('uploaded_at')
                    caption = f"Uploaded: {pd.to_datetime(uploaded_at).strftime('%d/%m/%Y')}" if uploaded_at else "Uploaded date unknown"
                    st.image(image_url, caption=caption, use_column_width=True)

    with col2:
        st.subheader("Actions")

        # --- Update Status ---
        with st.container(border=True):
            st.markdown("**Update Status**")
            new_status = st.selectbox(
                "New Status",
                options=["Open", "In Progress", "Resolved"],
                index=["Open", "In Progress", "Resolved"].index(ticket_details.get('status'))
            )
            if st.button("Save Status", type="primary"):
                update_ticket_status(selected_ticket_id, new_status)
                st.rerun()

        # --- Add Work Note ---
        with st.container(border=True):
            st.markdown("**Add Work Note**")
            with st.form("add_note_form"):
                note_text = st.text_area("New Note")
                note_author = st.text_input("Your Name", value=st.session_state.get('username', ''))
                submitted_note = st.form_submit_button("Add Note")
                if submitted_note and note_text:
                    add_work_note(selected_ticket_id, note_text, note_author)
                    st.rerun()

        # --- Log Component Used ---
        with st.container(border=True):
            st.markdown("**Log Component Used**")
            inventory = get_inventory_components()
            if inventory:
                component_options = {c['component_name']: c['id'] for c in inventory}
                with st.form("add_component_form"):
                    selected_comp_name = st.selectbox("Component", options=list(component_options.keys()))
                    quantity = st.number_input("Quantity Used", min_value=1, step=1)
                    submitted_comp = st.form_submit_button("Log Component")
                    if submitted_comp:
                        component_id = component_options[selected_comp_name]
                        add_component_to_ticket(selected_ticket_id, component_id, quantity)
                        st.rerun()

st.divider()
st.page_link("pages/1_Maintenance_Hub.py", label="Back to Maintenance Hub", icon="⬅️")
