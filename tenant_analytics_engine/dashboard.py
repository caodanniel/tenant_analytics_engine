import streamlit as st
import sqlite3
import pandas as pd
import json
import plotly.express as px
from datetime import datetime

# Page Configuration for an enterprise feel
st.set_page_config(
    page_title="Ingestion Control Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = "database.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH)

# Cache data with a short TTL to simulate live database polling
@st.cache_data(ttl=5)
def load_pipeline_data():
    conn = get_db_connection()
    # Read both tables cleanly
    df_events = pd.read_sql_query("SELECT * FROM unified_events", conn)
    df_incidents = pd.read_sql_query("SELECT * FROM tenant_incident_log", conn)
    conn.close()
    
    # Ensure datetime parsing for proper timeline rendering
    if not df_events.empty:
        df_events['event_timestamp'] = pd.to_datetime(df_events['event_timestamp'])
        df_events['ingested_at'] = pd.to_datetime(df_events['ingested_at'])
    if not df_incidents.empty:
        df_incidents['logged_at'] = pd.to_datetime(df_incidents['logged_at'])
        
    return df_events, df_incidents

# Initialize and load data
df_events, df_incidents = load_pipeline_data()

# ==========================================
# SIDEBAR NAVIGATION & CUSTOM BRANDING
# ==========================================
st.sidebar.markdown("## 🏢 Operational Command")
st.sidebar.markdown("Use this portal to cross-examine pipeline health, audit customer data anomalies, and track schema violations.")
st.sidebar.divider()

# Extract client profiles dynamically
all_tenants = list(set(df_events['tenant_id'].unique()).union(set(df_incidents['tenant_id'].unique()))) if not df_events.empty or not df_incidents.empty else []

selected_tenant = st.sidebar.selectbox(
    "🎯 Select Customer Environment",
    options=["All Global Environments"] + [t for t in all_tenants]
)

# Apply dynamic filters based on sidebar selection
if selected_tenant != "All Global Environments":
    display_events = df_events[df_events['tenant_id'] == selected_tenant]
    display_incidents = df_incidents[df_incidents['tenant_id'] == selected_tenant]
else:
    display_events = df_events
    display_incidents = df_incidents

st.sidebar.divider()
st.sidebar.caption(f"Last UI Sync: {datetime.now().strftime('%H:%M:%S')} (Auto-refresh active)")

# ==========================================
# HEADER SECTION
# ==========================================
st.title("🛡️ Multi-Tenant Ingestion & Quality Control Center")
st.markdown(f"**Active Monitoring Scope:** `{selected_tenant}`")
st.divider()

# ==========================================
# REAL-TIME KPI METRIC CARDS
# ==========================================
total_clean = len(display_events)
total_failed = len(display_incidents)
total_processed = total_clean + total_failed
success_rate = (total_clean / total_processed * 100) if total_processed > 0 else 100.0

# Count anomalies based on our new ML Isolation Forest flag column
anomaly_count = display_events['is_anomaly'].sum() if 'is_anomaly' in display_events.columns else 0
threshold_count = display_events['threshold_exceeded'].sum() if 'threshold_exceeded' in display_events.columns else 0

# Create 4 columns for modern KPI cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        label="Total Records Processed", 
        value=f"{total_processed:,}", 
        delta=f"+{total_processed} items" if total_processed > 0 else None
    )

with kpi2:
    # Colors automatically green if positive, red if dropping
    st.metric(
        label="Pipeline Success Rate", 
        value=f"{success_rate:.2f}%", 
        delta=f"{(success_rate - 95.0):.2f}% vs SLA Target" if total_processed > 0 else None,
        delta_color="normal" if success_rate >= 95.0 else "inverse"
    )

with kpi3:
    st.metric(
        label="Quarantined Incidents", 
        value=f"{total_failed:,}", 
        delta=f"{total_failed} blocks waiting" if total_failed > 0 else "0 structural flags",
        delta_color="inverse" if total_failed > 0 else "normal"
    )

with kpi4:
    st.metric(
        label="ML Statistical Anomalies", 
        value=f"{int(anomaly_count)}", 
        delta="Review Required" if anomaly_count > 0 else "Behavior Stable",
        delta_color="inverse" if anomaly_count > 0 else "off"
    )

st.markdown("###") # Adding comfortable vertical whitespace

# ==========================================
# DATA VISUALIZATION SECTION
# ==========================================
chart_col1, chart_col2 = st.columns([2, 1]) # 2:1 ratio layout for visual balance

with chart_col1:
    st.subheader("⏱️ Multi-Dimensional Operational Latency Timeline")
    st.markdown("This timeline maps incoming data events. Red points highlight anomalies flagged by the unsupervised **Isolation Forest model** based on contextual deviations.")
    
    if not display_events.empty:
        # Guarantee historical chronological order
        plot_df = display_events.sort_values(by='event_timestamp')
        
        # Mapping numerical integers to explicit readable categories for the user legend
        plot_df['System Status'] = plot_df['is_anomaly'].map({1: '⚠️ ML Behavioral Anomaly', 0: '✅ Normal Operation'})
        
        fig = px.scatter(
            plot_df,
            x="event_timestamp",
            y="delay_hours",
            color="System Status",
            size=plot_df['delay_hours'].clip(lower=5), # Keeps points legible even if delay is 0
            hover_data=["asset_id", "delay_hours", "threshold_exceeded"],
            color_discrete_map={'⚠️ ML Behavioral Anomaly': '#EF553B', '✅ Normal Operation': '#00CC96'},
            labels={"delay_hours": "Delay Time (Hours)", "event_timestamp": "Log Timestamp"}
        )
        fig.update_layout(legend_title_text="Engine Classification")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No standardized historical events available to visualize inside this environment context.")

with chart_col2:
    st.subheader("🚨 Incident Root Causes")
    st.markdown("Distribution breakdown of hard validation failures captured at the Pydantic structural layer.")
    
    if not display_incidents.empty:
        incident_counts = display_incidents['error_type'].value_counts().reset_index()
        incident_counts.columns = ['Error Category', 'Frequency']
        
        fig_pie = px.pie(
            incident_counts,
            names='Error Category',
            values='Frequency',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.YlOrRd_r
        )
        fig_pie.update_layout(showlegend=False) # Hide legend on tight spaces to look cleaner
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.success("🎉 Outstanding Quality! Zero structural errors logged in this queue sequence.")

st.divider()

# ==========================================
# INTERACTIVE DATA DEEP-DIVES
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "🛠️ Quarantine Review Station", 
    "📋 Standardized Core Database", 
    "📊 Raw Tenant Performance Summaries"
])

with tab1:
    st.subheader("Isolated Exception Logs")
    st.markdown("The following records broke strict schemas or date parameters. They were safely quarantined to preserve the execution uptime of downstream analytics.")
    
    if not display_incidents.empty:
        # Order logs chronologically by execution time
        log_view = display_incidents.sort_values(by='logged_at', ascending=False)[
            ['id', 'tenant_id', 'error_type', 'error_details', 'logged_at', 'raw_row_data']
        ]
        st.dataframe(log_view, use_container_width=True, hide_index=True)
    else:
        st.info("Quarantine queue is empty.")

with tab2:
    st.subheader("Unified Event Architecture View")
    st.markdown("This table contains production-ready records that successfully cleared all defensive structural blocks and machine learning loops.")
    
    if not display_events.empty:
        event_view = display_events.sort_values(by='ingested_at', ascending=False)[
            ['id', 'tenant_id', 'asset_id', 'event_timestamp', 'delay_hours', 'threshold_exceeded', 'is_anomaly', 'ingested_at']
        ]
        # Utilize color highlights if columns have flags
        st.dataframe(
            event_view, 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("No unified database elements exist yet.")

with tab3:
    st.subheader("Aggregated Customer Metrics")
    st.markdown("High-level system summaries grouped by customer environments.")
    
    if not df_events.empty:
        summary_metrics = df_events.groupby('tenant_id').agg(
            Valid_Records=('id', 'count'),
            Average_Delay_Hours=('delay_hours', 'mean'),
            Max_Delay_Hours=('delay_hours', 'max'),
            Total_ML_Anomalies=('is_anomaly', 'sum')
        ).reset_index()
        
        # Format columns cleanly
        summary_metrics['Average_Delay_Hours'] = summary_metrics['Average_Delay_Hours'].round(2)
        st.dataframe(summary_metrics, use_container_width=True, hide_index=True)
    else:
        st.info("Data source unavailable.")