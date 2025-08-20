import streamlit as st
import pandas as pd
import plotly.express as px
from api import login, get_oee_data, get_utilization_data, get_downtime_analysis_data, get_machines, get_shifts, get_days_of_week
from utils import clean_utilization_data, clean_downtime_data
import requests
from config import Config

def get_color(value: float) -> str:
    color_scale: list[str] = px.colors.diverging.RdYlGn
    normalised_percentage = min(1, max(0, value / 70))
    color_index = int(normalised_percentage * (len(color_scale) - 1))
    return color_scale[color_index]

st.set_page_config(page_title="Mill Dash", layout="wide", page_icon="🏭")
st.title("📊 Mill Production Dashboard")

# Check for login token
if 'token' not in st.session_state or st.session_state.token is None:
    st.warning("Please log in to access this page.")
    st.page_link("app.py", label="Go to Login")
    st.stop()

else:
    st.sidebar.title("Mill Dash")
    st.sidebar.markdown("------")
    st.sidebar.header("Filters")

    # Fetch filter data
    machines_response = get_machines(st.session_state.token)
    machines = ["All"] + (machines_response.json() if machines_response.status_code == 200 else [])
    shifts_response = get_shifts(st.session_state.token)
    shifts = ["All"] + (shifts_response.json() if shifts_response.status_code == 200 else [])
    days_of_week_response = get_days_of_week(st.session_state.token)
    days_of_week = ["All"] + (days_of_week_response.json() if days_of_week_response.status_code == 200 else [])

    start_date = st.sidebar.date_input("Start Date")
    end_date = st.sidebar.date_input("End Date")
    machine = st.sidebar.selectbox(
        "Machine",
        machines,
        format_func=lambda m: Config.MACHINE_ID_MAP.get(m, "All")
    )
    shift = st.sidebar.selectbox("Shift", shifts)
    day_of_week = st.sidebar.selectbox("Day of Week", days_of_week)

    if st.sidebar.button("Refresh"):
        st.rerun()

    params = {
        "start_time": start_date.isoformat(),
        "end_time": end_date.isoformat(),
        "machine_ids": [machine] if machine != "All" else None,
        "shift": shift if shift != "All" else None,
        "day_of_week": day_of_week if day_of_week != "All" else None
    }

    st.subheader("Dashboard")

    # OEE Data
    oee_response = get_oee_data(st.session_state.token, params)
    if oee_response.status_code == 200:
        oee_data = oee_response.json()
        st.write("### OEE (Overall Equipment Effectiveness)")
        df = pd.DataFrame(oee_data, index=[0])
        df = df.T.reset_index()
        df.columns = ['metric', 'value']
        fig = px.bar(df, x='metric', y='value', color='metric', color_discrete_map={
            'oee': get_color(df[df['metric'] == 'oee']['value'].values[0]),
            'availability': get_color(df[df['metric'] == 'availability']['value'].values[0]),
            'performance': get_color(df[df['metric'] == 'performance']['value'].values[0]),
            'quality': get_color(df[df['metric'] == 'quality']['value'].values[0])
        })
        st.plotly_chart(fig)

    # Utilization Data
    utilization_response = get_utilization_data(st.session_state.token, params)
    if utilization_response.status_code == 200 and utilization_response.json():
        utilization_data = utilization_response.json()
        st.write("### Utilization")
        df = pd.DataFrame.from_dict(clean_utilization_data(utilization_data), orient='index', columns=['value'])
        fig = px.pie(
            df,
            values='value',
            names=df.index,
            color=df.index,
            color_discrete_map={
                'Productive Uptime (hours)': "forestgreen",
                'Productive Downtime (hours)': "dodgerblue",
                'Unproductive Downtime (hours)': "red"
            }
        )
        st.plotly_chart(fig)
        st.write(f"Total Time: {utilization_data['total_time_seconds'] / 3600:.2f} (hours)")
        st.write(f"Productive Uptime: {utilization_data['productive_uptime_seconds'] / 3600:.2f} (hours)")
        st.write(f"Productive Downtime: {utilization_data['productive_downtime_seconds'] / 3600:.2f} (hours)")
        st.write(f"Unproductive Downtime: {utilization_data['unproductive_downtime_seconds'] / 3600:.2f} (hours)")            
        st.write(
            f"<span style='color: {get_color(utilization_data['utilization_percentage'])}; font-size: 18px;'>Utilization Percentage: {utilization_data['utilization_percentage']:.2f}%</span>",
            unsafe_allow_html=True
        )
    else:
        st.write("### Utilization")
        st.write("No data available for the selected filters.")


    # Downtime Analysis Data
    downtime_response = get_downtime_analysis_data(st.session_state.token, params)
    if downtime_response.status_code == 200 and downtime_response.json():
        downtime_data = downtime_response.json()
        st.write("### Downtime Analysis")
        st.write("#### Excessive Downtimes")
        with st.container(height=300):
            st.table(clean_downtime_data(downtime_data["excessive_downtimes"]))
        st.write("#### Recurring Downtime Reasons")
        df = pd.DataFrame.from_dict({k: round(v / 3600, 2) for k, v in downtime_data["recurring_downtime_reasons"].items()}, orient='index', columns=['value'])
        fig = px.bar(df, x=df.index, y='value')
        st.plotly_chart(fig)

    else:
        st.write("### Downtime Analysis")
        st.write("No data available for the selected filters.")