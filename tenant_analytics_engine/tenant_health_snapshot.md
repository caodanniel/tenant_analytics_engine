# Multi-Tenant Pipeline Health Report
Generated: 2026-06-04 15:41:00

## High-Level Execution Telemetry
* **Successfully Standardized Records:** 10 rows
* **Quarantined Incidents Captured:** 2 instances

## Client Threshold Triggers (Alerts Flags)
Total instances where client-specific maximum latency threshold constraints were broken:
- **[client_alpha]** Asset `P-102` logged a delay of **34.0 hours** (Ingested at: 2026-06-04T15:41:00.194605)
- **[client_beta]** Asset `TRK-ERROR` logged a delay of **72.5 hours** (Ingested at: 2026-06-04T15:41:00.215692)
- **[client_alpha]** Asset `P-102` logged a delay of **34.0 hours** (Ingested at: 2026-06-04T15:41:00.235542)
- **[client_beta]** Asset `TRK-ERROR` logged a delay of **72.5 hours** (Ingested at: 2026-06-04T15:41:00.257827)

## Data Quality Audit Log Breakdowns
### Tenant: `client_beta` | Type: `DATE_FORMAT_ERROR`
- Details: *Expected %Y-%m-%d %H:%M:%S, structural failure: time data 'INVALID_DATE' does not match format '%Y-%m-%d %H:%M:%S'*
### Tenant: `client_beta` | Type: `DATE_FORMAT_ERROR`
- Details: *Expected %Y-%m-%d %H:%M:%S, structural failure: time data 'INVALID_DATE' does not match format '%Y-%m-%d %H:%M:%S'*
