import streamlit as st
from api import login
import requests
from config import Config


st.set_page_config(
    page_title="Mill Dash Home",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': f'{Config.BASE_URL}/docs/help',
        'Report a bug': f"{Config.BASE_URL}/bug",
    }
)


def show_login_form():
    """Displays the login form."""
    with st.form("login_form"):
        if "token" not in st.session_state:
            st.subheader("Login")
            username = st.text_input("Username", value="testuser")
            password = st.text_input("Password", type="password", value="testpassword")
            submitted = st.form_submit_button("Login")

            if submitted:
                try:
                    response: requests.Response | None = login(username, password)
                    if response:
                        if response.status_code == 200:
                            st.session_state.token = response.json()["access_token"]
                            st.rerun()
                        elif response.status_code == 401:
                            st.error("Invalid username or password")
                        else:
                            st.error(f"An error occurred: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    st.error(f"A network error occurred: {e}")

def show_landing_page():
    """Displays the main landing page after login."""
    st.title(f"Welcome to the Mill Dashboard, {st.session_state.get('username', 'User')}!")
    
    st.markdown("""
        This is the central hub for monitoring and managing production at CSS Support Systems.
        
        Please use the navigation sidebar on the left to access the different sections of the application:

        - **Dashboard:** View live and historical performance metrics for all mills.
        - **Operator Terminal:** Log the start and end of production runs.
        - **Maintenance Hub:** View and manage maintenance tickets.
    """)

    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Main App Logic ---
if 'token' not in st.session_state or st.session_state.token is None:
    st.title("Mill Dash Login")
    show_login_form()
else:
    show_landing_page()
