import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Set random seed for reproducible "normal" business distributions
np.random.seed(42)

print("Generating expanded enterprise datasets...")

# 1. GENERATE EXPANDED CLIENT ALPHA DATA

# Baseline: Alpha usually has small delays averaging around 12 hours
alpha_records = 60
alpha_base_time = datetime(2026, 5, 1)

alpha_part_ids = [f"P-{100 + i}" for i in range(alpha_records)]
# Generate timestamps spreading across consecutive days at roughly 10:00 AM
alpha_timestamps = [(alpha_base_time + timedelta(days=i, hours=10)).strftime('%m/%d/%Y') for i in range(alpha_records)]
# Normal distribution of durations: Mean=12 hrs, StdDev=1.5 hrs
alpha_durations = np.random.normal(loc=12.0, scale=1.5, size=alpha_records).tolist()

# Inject Alpha Alerts / Threshold breaches (> 24 hrs based on config.json)
alpha_durations[15] = 26.5
alpha_durations[30] = 29.0

# Inject extreme ML Statistical Anomalies (e.g., massive spikes completely out of character)
alpha_durations[45] = 310.0  
alpha_durations[55] = 425.0

df_alpha = pd.DataFrame({
    'part_id': alpha_part_ids,
    'timestamp': alpha_timestamps,
    'duration': [round(d, 1) for d in alpha_durations]
})
df_alpha.to_csv('data/client_alpha_raw.csv', index=False)
print(f"-> Successfully generated {alpha_records} rows for Client Alpha.")


# 2. GENERATE EXPANDED CLIENT BETA DATA
# Baseline: Beta runs a 3PL logistics setup, average delays are around 20 hours
beta_records = 65
beta_base_time = datetime(2026, 5, 1)

beta_tracking_nos = [f"TRK-{8000 + i}" for i in range(beta_records)]
# Generate timestamps passing at different hours of the day
beta_timestamps = [(beta_base_time + timedelta(days=i, hours=i % 24)).strftime('%Y-%m-%d %H:%M:%S') for i in range(beta_records)]
# Normal distribution of elapsed hours: Mean=20 hrs, StdDev=3 hrs
beta_hours = np.random.normal(loc=20.0, scale=3.0, size=beta_records).tolist()

# Inject Structural Data Quality Incidents (Will trigger Pydantic / Date Format crashes)
beta_timestamps[10] = "INVALID_TIMESTAMP_STRING" 
beta_tracking_nos[25] = "TRK-ERROR-MISSING"
beta_hours[25] = float('nan') # Pydantic will catch a NaN float rule mismatch

# Inject Beta Threshold breaches (> 48 hrs based on config.json)
beta_hours[35] = 52.0

# Inject extreme ML Statistical Anomalies 
# (e.g., An operational tracking value that passes Pydantic floats but is massive)
beta_hours[50] = 615.0

df_beta = pd.DataFrame({
    'tracking_no': beta_tracking_nos,
    'event_date': beta_timestamps,
    'hours_elapsed': [round(h, 1) if not np.isnan(h) else h for h in beta_hours]
})
df_beta.to_csv('data/client_beta_raw.csv', index=False)
print(f"-> Successfully generated {beta_records} rows for Client Beta.")

print("\nAll mock environments ready. Run 'python pipeline.py' to process and populate your dashboard dynamically.")