# generate_mock_data.py
import pandas as pd
import os

os.makedirs('data', exist_ok=True)

# Client Alpha: Uses 'duration', 'part_id', and MM/DD/YYYY format
alpha_data = pd.DataFrame({
    'part_id': ['P-101', 'P-102', 'P-103', 'P-104', 'P-105', 'P-106'],
    'timestamp': ['05/12/2026', '05/13/2026', '05/14/2026', '05/15/2026', '05/16/2026', '05/17/2026'],
    'duration': [12.0, 11.5, 13.0, 12.2, 11.8, 450.0]  # 450.0 is an extreme statistical anomaly!
})
alpha_data.to_csv('data/client_alpha_raw.csv', index=False)

# Client Beta: Uses 'hours_elapsed', 'tracking_no', and standard timestamps
beta_data = pd.DataFrame({
    'tracking_no': ['TRK-99', 'TRK-ERROR', 'TRK-88'],
    'event_date': ['2026-05-12 14:30:00', '2026-05-13 11:15:00', 'INVALID_DATE'], # Row 3 triggers date incident
    'hours_elapsed': [18.0, 72.5, 10.0] # Row 2 (72.5) triggers a threshold incident
})
beta_data.to_csv('data/client_beta_raw.csv', index=False)

print("Mock tenant datasets successfully generated in /data.")