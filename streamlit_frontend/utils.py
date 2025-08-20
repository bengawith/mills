import pandas as pd
from typing import Dict, Any, List
import plotly.express as px
from config import Config


def clean_utilization_data(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        k.strip().removesuffix("_seconds").replace("_", " ").title() + " (hours)": round(v / 3600, 2) 
        for k, v in data.items() 
        if k not in ["utilization_percentage", "total_time_seconds"]
    }


def clean_downtime_data(data: List[Dict[str, Any]], machine_id: str = "All") -> pd.DataFrame:
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
    if machine_id != "All":
        renamed_data = [dt_data for dt_data in renamed_data if dt_data["Machine ID"] == machine_id]
    renamed_data = pd.DataFrame(renamed_data, columns=name_map.values())
    renamed_data["Start Time"] = pd.to_datetime(renamed_data["Start Time"], format="ISO8601", utc=True)
    renamed_data["End Time"] = pd.to_datetime(renamed_data["End Time"], format="ISO8601", utc=True)
    return renamed_data

# --- NEW PLOTTING FUNCTIONS ---

def plot_timeline(df):
    """
    Generates an interactive timeline plot that now includes product and maintenance info.
    """
    # Create a new column for more descriptive hover text
    df['hover_text'] = df.apply(
        lambda row: f"Product: {row['product_name']}" if pd.notna(row['product_name'])
        else f"Incident: {row['incident_category']}" if pd.notna(row['incident_category'])
        else row['utilisation_category'],
        axis=1
    )
    
    # Create a new column for coloring, prioritizing product and incident information
    df['color_label'] = df.apply(
        lambda row: row['product_name'] if pd.notna(row['product_name'])
        else f"MAINT: {row['incident_category']}" if pd.notna(row['incident_category'])
        else row['utilisation_category'],
        axis=1
    )

    fig = px.timeline(
        df,
        x_start="start_timestamp",
        x_end="end_timestamp",
        y="name",
        color="color_label", # Use the new label for coloring
        title="Machine Status Timeline",
        hover_name="hover_text", # Show the detailed hover text
        color_discrete_map=Config.PLOTLY_COLOR_MAP
    )
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(legend_title_text='Activity Type')
    return fig

def plot_utilisation_bar(df):
    """Generates a bar chart for machine utilisation."""
    if df.empty or 'duration_seconds' not in df.columns:
        return px.bar(title="Not enough data for Utilisation Chart")

    utilisation_by_machine = df.groupby('name').apply(
        lambda x: (x[x['utilisation_category'] == 'PRODUCTIVE UPTIME']['duration_seconds'].sum() / x['duration_seconds'].sum()) * 100 if x['duration_seconds'].sum() > 0 else 0
    ).reset_index(name='utilisation')

    fig = px.bar(
        utilisation_by_machine,
        x='name',
        y='utilisation',
        title='Utilisation % by Machine',
        labels={'name': 'Machine', 'utilisation': 'Utilisation (%)'},
        text='utilisation'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_yaxes(range=[0, 100])
    return fig

def plot_downtime_pareto(df):
    """Generates a Pareto chart for downtime reasons."""
    downtime_df = df[df['classification'] == 'DOWNTIME'].copy()
    
    if downtime_df.empty:
        return px.bar(title="No Downtime Data Available for Selected Filters")

    # Prioritize the maintenance incident category for more accurate reason logging
    downtime_df['reason'] = downtime_df['incident_category'].fillna(downtime_df['downtime_reason_name'])

    reason_counts = downtime_df['reason'].value_counts().reset_index()
    reason_counts.columns = ['reason', 'count']
    
    fig = px.bar(
        reason_counts,
        x='reason',
        y='count',
        title='Downtime Reasons Pareto',
        labels={'reason': 'Downtime Reason', 'count': 'Frequency'}
    )
    return fig

# --- NEW PLOTTING FUNCTIONS ---

def plot_scrap_by_product(df):
    """Generates a bar chart showing total scrap length by product."""
    # This requires data from the ProductionRun table, which is now correlated
    scrap_df = df[df['scrap_length'].notna()].drop_duplicates(subset=['id']).copy() # Use FourJaw ID to count unique runs
    
    if scrap_df.empty:
        return px.bar(title="No Scrap Data Available for Selected Filters")

    scrap_by_product = scrap_df.groupby('product_name')['scrap_length'].sum().reset_index()

    fig = px.bar(
        scrap_by_product,
        x='product_name',
        y='scrap_length',
        title='Total Scrap Length (m) by Product',
        labels={'product_name': 'Product', 'scrap_length': 'Total Scrap (m)'}
    )
    return fig

def plot_tickets_by_category(df):
    """Generates a pie chart of maintenance tickets by incident category."""
    tickets_df = df[df['maintenance_ticket_id'].notna()].drop_duplicates(subset=['maintenance_ticket_id'])

    if tickets_df.empty:
        return px.pie(title="No Maintenance Tickets for Selected Filters")

    category_counts = tickets_df['incident_category'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']

    fig = px.pie(
        category_counts,
        names='category',
        values='count',
        title='Maintenance Tickets by Category'
    )
    return fig
