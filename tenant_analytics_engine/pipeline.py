import os
import json
import sqlite3
from datetime import datetime
import pandas as pd
import math
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Dict, List
from sklearn.ensemble import IsolationForest
import numpy as np

# 1. PYDANTIC SCHEMAS FOR CONFIG & VALIDATION

class TenantConfig(BaseModel):
    tenant_name: str
    column_mapping: Dict[str, str]
    date_format: str
    max_allowed_delay_hours: float

class MasterConfig(BaseModel):
    tenants: Dict[str, TenantConfig]

# The standardized master internal schema
class UnifiedRecord(BaseModel):
    tenant_id: str
    asset_id: str
    event_timestamp: datetime
    delay_hours: float

    @field_validator('delay_hours')
    @classmethod
    def check_not_nan(cls, v: float) -> float:
        if math.isnan(v):
            raise ValueError("Value cannot be NaN (Not a Number)")
        return v

# 2. SQLITE DATABASE SCHEMA SETUP


DB_PATH = "database.db"

def init_db():
    """Initializes the SQLite schema if tables do not exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Unified tracking table for all valid records across tenants
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS unified_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT NOT NULL,
            asset_id TEXT NOT NULL,
            event_timestamp TEXT NOT NULL,
            delay_hours REAL NOT NULL,
            ingested_at TEXT NOT NULL,
            threshold_exceeded INTEGER DEFAULT 0,
            is_anomaly INTEGER DEFAULT 0
        )
    """)
    
    # Audit log to capture pipeline validation and schema incidents
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenant_incident_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT NOT NULL,
            raw_row_data TEXT NOT NULL,
            error_type TEXT NOT NULL,
            error_details TEXT NOT NULL,
            logged_at TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


# 3. PIPELINE ENGINE PROCESSING LOGIC
def check_for_anomaly_ml(tenant_id: str, current_value: float, current_time: datetime) -> int:
    """
    Uses an Isolation Forest to detect multi-dimensional operational outliers
    based on delay length, hour of day, and day of the week.
    """
    conn = sqlite3.connect(DB_PATH)
    # Pull history for this specific client
    query = "SELECT delay_hours, event_timestamp FROM unified_events WHERE tenant_id = ?"
    df_hist = pd.read_sql_query(query, conn, params=(tenant_id,))
    conn.close()
    
    # Cold-start rule: Isolation Forest requires baseline historical data to learn patterns
    if len(df_hist) < 10:
        return 0
        
    # 1. Feature Engineering: Extract time-of-day features from history
    df_hist['datetime'] = pd.to_datetime(df_hist['event_timestamp'])
    df_hist['hour'] = df_hist['datetime'].dt.hour
    df_hist['day_of_week'] = df_hist['datetime'].dt.dayofweek
    
    # Prepare training feature array: Shape (N, 3)
    X_train = df_hist[['delay_hours', 'hour', 'day_of_week']].values
    
    # 2. Current Record Feature Engineering
    current_hour = current_time.hour
    current_day = current_time.weekday()
    X_current = np.array([[current_value, current_hour, current_day]])
    
    # 3. Train the Isolation Forest Model
    # contamination=0.05 targets a roughly 5% expected outlier rate
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X_train)
    
    # 4. Predict anomaly status (-1 = outlier, 1 = normal)
    prediction = model.predict(X_current)[0]
    
    if prediction == -1:
        print(f"  [ML ANOMALY ALERT] Outlier patterns detected for {tenant_id}!")
        return 1
        
    return 0


def log_incident(tenant_id: str, row_dict: dict, error_type: str, details: str):
    """Safely logs structural and content failures into the incident table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tenant_incident_log (tenant_id, raw_row_data, error_type, error_details, logged_at)
        VALUES (?, ?, ?, ?, ?)
    """, (tenant_id, json.dumps(row_dict), error_type, details, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def save_unified_record(record: UnifiedRecord, threshold_exceeded: int, is_anomaly: int):
    """Inserts standardized records seamlessly into the centralized table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Update both the column list and the placeholders (?) to handle 3 flags/metrics
    cursor.execute("""
        INSERT INTO unified_events (
            tenant_id, 
            asset_id, 
            event_timestamp, 
            delay_hours, 
            ingested_at, 
            threshold_exceeded,
            is_anomaly
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        record.tenant_id,
        record.asset_id,
        record.event_timestamp.isoformat(),
        record.delay_hours,
        datetime.now().isoformat(),
        threshold_exceeded,
        is_anomaly
    ))
    conn.commit()
    conn.close()

def process_tenant(tenant_id: str, file_path: str, config: TenantConfig):
    print(f"\n--- Processing Stream for {config.tenant_name} ({tenant_id}) ---")
    
    if not os.path.exists(file_path):
        print(f"Error: Target file {file_path} missing.")
        return
        
    df = pd.read_csv(file_path)
    
    # Day 1 Target: Structural column mapping validation
    reverse_mapping = {v: k for k, v in config.column_mapping.items()}
    expected_source_cols = list(config.column_mapping.keys())
    
    # Verify columns exist before touching lines
    if not all(col in df.columns for col in expected_source_cols):
        missing = [c for c in expected_source_cols if c not in df.columns]
        print(f"Critical schema mismatch for {tenant_id}. Missing columns: {missing}")
        log_incident(tenant_id, {"headers": list(df.columns)}, "CRITICAL_SCHEMA_MISMATCH", f"Missing structural items: {missing}")
        return

    success_count = 0
    incident_count = 0

    # Iterative processing through configuration rules
    for _, row in df.iterrows():
        raw_row = row.to_dict()
        
        # 1. Map column names dynamically to internal standard labels
        mapped_row = {config.column_mapping[k]: v for k, v in raw_row.items() if k in config.column_mapping}
        mapped_row['tenant_id'] = tenant_id
        
        # 2. Format specific Date string to datetime object using config guidelines
        try:
            mapped_row['event_timestamp'] = datetime.strptime(
                str(raw_row[reverse_mapping['event_timestamp']]), 
                config.date_format
            )
        except ValueError as date_err:
            log_incident(tenant_id, raw_row, "DATE_FORMAT_ERROR", f"Expected {config.date_format}, structural failure: {str(date_err)}")
            incident_count += 1
            continue

        # 3. Pydantic validation for casting boundaries
        try:
            clean_record = UnifiedRecord(**mapped_row)
        except ValidationError as val_err:
            log_incident(tenant_id, raw_row, "DATA_VALIDATION_ERROR", val_err.json())
            incident_count += 1
            continue
            
        # 4. Check for Statistical Anomalies (NEW STRETCH STEP)
        anomaly_flag = check_for_anomaly_ml(
            tenant_id=tenant_id,
            current_value=clean_record.delay_hours,
            current_time=clean_record.event_timestamp
        )
            
        # 5. Check client threshold metrics
        threshold_flag = 1 if clean_record.delay_hours > config.max_allowed_delay_hours else 0
        
        # Pass the new anomaly flag into your modified database save utility
        save_unified_record(clean_record, threshold_flag, anomaly_flag)
        success_count += 1

    print(f"Results Summary -> Standardized Ingestions: {success_count} | Incidents Captured: {incident_count}")

# ==========================================
# 4. ORCHESTRATION LAYER EXECUTOR
# ==========================================

def run_pipeline():
    init_db()
    
    # Load multi-tenant master file configuration mapping 
    with open("config.json", "r") as f:
        config_data = json.load(f)
    
    master_config = MasterConfig(**config_data)
    
    # Cycle and execute across all tenants dynamically defined
    for tenant_id, tenant_rules in master_config.tenants.items():
        target_file = f"data/{tenant_id}_raw.csv"
        process_tenant(tenant_id, target_file, tenant_rules)



def generate_audit_report():
    """Queries SQLite database to compile an execution summary markdown report."""
    conn = sqlite3.connect(DB_PATH)
    
    total_clean = pd.read_sql_query("SELECT COUNT(*) as count FROM unified_events", conn).iloc[0]['count']
    total_incidents = pd.read_sql_query("SELECT COUNT(*) as count FROM tenant_incident_log", conn).iloc[0]['count']
    alerts = pd.read_sql_query("SELECT * FROM unified_events WHERE threshold_exceeded = 1", conn)
    incidents = pd.read_sql_query("SELECT tenant_id, error_type, error_details FROM tenant_incident_log", conn)
    
    conn.close()
    
    report_md = f"""# Multi-Tenant Pipeline Health Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## High-Level Execution Telemetry
* **Successfully Standardized Records:** {total_clean} rows
* **Quarantined Incidents Captured:** {total_incidents} instances

## Client Threshold Triggers (Alerts Flags)
Total instances where client-specific maximum latency threshold constraints were broken:
"""
    for _, row in alerts.iterrows():
        report_md += f"- **[{row['tenant_id']}]** Asset `{row['asset_id']}` logged a delay of **{row['delay_hours']} hours** (Ingested at: {row['ingested_at']})\n"
        
    report_md += "\n## Data Quality Audit Log Breakdowns\n"
    for _, row in incidents.iterrows():
        report_md += f"### Tenant: `{row['tenant_id']}` | Type: `{row['error_type']}`\n- Details: *{row['error_details']}*\n"
        
    with open("tenant_health_snapshot.md", "w") as f:
        f.write(report_md)
    print("\n[Report Generated] Saved summary updates to 'tenant_health_snapshot.md'.")

# Append to run execution step in main
if __name__ == "__main__":
    init_db()
    run_pipeline()
    generate_audit_report()