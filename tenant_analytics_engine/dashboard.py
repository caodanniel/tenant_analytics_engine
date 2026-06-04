import streamlit as st
import sqlite3
import pandas as pd
import json
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Multi-Tenant Operations Portal",
    page_icon="📊",
    layout="wide"
)

DB_PATH = "database.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH)

# ==========================================
# DATA LOADING UTILITIES
# ==========================================
@st.cache_data(ttl=10) # Refresh cache every 10 seconds to mimic real-time updates
def load_pipeline_metrics():
    conn = get_db_connection()
    
    # Load all valid processed events
    df_events = pd.read_sql_query("SELECT * FROM unified_events", conn)
    
    # Load all quarantined incidents
    df_incidents = pd.read_sql_query("SELECT * FROM tenant_incident_log", conn)
    
    conn.close()
    return df_events, df_incidents

# ==========================================
# SIDEBAR / GLOBAL FILTERS
# ==========================================
st.sidebar.title("🏢 Control Center")
st.sidebar.markdown("Navigate and manage customer data feeds.")

# Load raw frames
df_events, df_incidents = load_pipeline_metrics()

# Extract available tenants dynamically from data
all_tenants = list(set(df_events['tenant_id'].unique()).union(set(df_incidents['tenant_id'].unique())))

# Tenant Filter
selected_tenant = st.sidebar.selectbox(
    "Select Tenant Context",
    options=["All Tenants"] + all_tenants
)

# Filter global dataframes based on selection
if selected_tenant != "All Tenants":
    display_events = df_events[df_events['tenant_id'] == selected_tenant]
    display_incidents = df_incidents[df_incidents['tenant_id'] == selected_tenant]
else:
    display_events = df_events
    display_incidents = df_incidents

# ==========================================
# MAIN DASHBOARD INTERFACE
# ==========================================
st.title("📊 Multi-Tenant Ingestion & Quality Portal")
st.markdown(f"**Viewing Scope:** `{selected_tenant}` | System Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.divider()

# 1. KPI Metric Cards
total_clean = len(display_events)
total_failed = len(display_incidents)
total_processed = total_clean + total_failed
success_rate = (total_clean / total_processed * 100) if total_processed > 0 else 100.0
anomaly_count = display_events['is_anomaly'].sum() if 'is_anomaly' in display_events.columns else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Records Processed", f"{total_processed:,}")
m2.metric("Pipeline Success Rate", f"{success_rate:.1f}%", delta=f"{success_rate - 90:.1f}% vs Target" if total_processed > 0 else None)
m3.metric("Quarantined Incidents", f"{total_failed:,}", delta="- Alerts Pending" if total_failed > 0 else None, delta_color="inverse")
m4.metric("Statistical Anomalies", f"{int(anomaly_count)}", delta="Review Recommended" if anomaly_count > 0 else None, delta_color="off")

st.markdown("###")

# 2. Charts and Visualization Row
col1, col2 = st.columns(2)

with col1:
    st.subheader("⏱️ Asset Operational Latency Trend")
    if not display_events.empty:
        # Sort values by time for chronological plotting
        plot_df = display_events.sort_values(by='event_timestamp')
        fig = px.scatter(
            plot_df,
            x="event_timestamp",
            y="delay_hours",
            color="tenant_id" if selected_tenant == "All Tenants" else "is_anomaly",
            size="delay_hours",
            hover_data=["asset_id"],
            labels={"delay_hours": "Delay (Hours)", "event_timestamp": "Timestamp"},
            color_discrete_map={1: "#EF553B", 0: "#636EFA"} # Red for anomalies, blue for standard records
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No clean record data found for this scope.")

with col2:
    st.subheader("🚨 Incident Type Breakdowns")
    if not display_incidents.empty:
        incident_counts = display_incidents['error_type'].value_counts().reset_index()
        incident_counts.columns = ['Incident Type', 'Count']
        fig_pie = px.pie(
            incident_counts,
            names='Incident Type',
            values='Count',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.OrRd_r
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.success("🎉 Perfect operations! Zero structural exceptions caught.")

st.divider()

# 3. Data Tables Room (Deep-Dive Sections)
st.subheader("🛠️ The Quarantine Review Station")
st.markdown("These rows broke structural constraints or date validations and were isolated to preserve downstream uptime.")

if not display_incidents.empty:
    # Re-arrange columns for cleaner enterprise presentation
    clean_incident_view = display_incidents[['id', 'tenant_id', 'error_type', 'error_details', 'logged_at', 'raw_row_data']]
    st.dataframe(clean_incident_view, use_container_width=True)
else:
    st.info("No quarantined records found.")

st.markdown("###")

st.subheader("📋 Unified Standardized Event Data")
st.markdown("Cleanly mapped data running through the central pipeline framework.")

if not display_events.empty:
    st.dataframe(display_events.sort_values(by='ingested_at', ascending=False), use_container_width=True)
else:
    st.info("No unified events found in database layer.")