# Multi-Tenant Pipeline Health Report
Generated: 2026-06-05 08:54:12

## High-Level Execution Telemetry
* **Successfully Standardized Records:** 238 rows
* **Quarantined Incidents Captured:** 9 instances

## Client Threshold Triggers (Alerts Flags)
Total instances where client-specific maximum latency threshold constraints were broken:
- **[client_alpha]** Asset `P-102` logged a delay of **34.0 hours** (Ingested at: 2026-06-04T15:41:00.194605)
- **[client_beta]** Asset `TRK-ERROR` logged a delay of **72.5 hours** (Ingested at: 2026-06-04T15:41:00.215692)
- **[client_alpha]** Asset `P-102` logged a delay of **34.0 hours** (Ingested at: 2026-06-04T15:41:00.235542)
- **[client_beta]** Asset `TRK-ERROR` logged a delay of **72.5 hours** (Ingested at: 2026-06-04T15:41:00.257827)
- **[client_alpha]** Asset `P-102` logged a delay of **34.0 hours** (Ingested at: 2026-06-05T08:41:32.156597)
- **[client_beta]** Asset `TRK-ERROR` logged a delay of **72.5 hours** (Ingested at: 2026-06-05T08:41:32.185504)
- **[client_alpha]** Asset `P-102` logged a delay of **34.0 hours** (Ingested at: 2026-06-05T08:42:19.717559)
- **[client_beta]** Asset `TRK-ERROR` logged a delay of **72.5 hours** (Ingested at: 2026-06-05T08:42:19.739476)
- **[client_alpha]** Asset `P-102` logged a delay of **34.0 hours** (Ingested at: 2026-06-05T08:42:19.761114)
- **[client_beta]** Asset `TRK-ERROR` logged a delay of **72.5 hours** (Ingested at: 2026-06-05T08:42:19.784096)
- **[client_alpha]** Asset `P-102` logged a delay of **34.0 hours** (Ingested at: 2026-06-05T08:47:53.809437)
- **[client_beta]** Asset `TRK-ERROR` logged a delay of **72.5 hours** (Ingested at: 2026-06-05T08:47:54.087028)
- **[client_alpha]** Asset `P-115` logged a delay of **26.5 hours** (Ingested at: 2026-06-05T08:51:31.103828)
- **[client_alpha]** Asset `P-130` logged a delay of **29.0 hours** (Ingested at: 2026-06-05T08:51:32.442921)
- **[client_alpha]** Asset `P-145` logged a delay of **310.0 hours** (Ingested at: 2026-06-05T08:51:33.788576)
- **[client_alpha]** Asset `P-155` logged a delay of **425.0 hours** (Ingested at: 2026-06-05T08:51:34.707074)
- **[client_alpha]** Asset `P-115` logged a delay of **26.5 hours** (Ingested at: 2026-06-05T08:54:03.048350)
- **[client_alpha]** Asset `P-130` logged a delay of **29.0 hours** (Ingested at: 2026-06-05T08:54:04.418236)
- **[client_alpha]** Asset `P-145` logged a delay of **310.0 hours** (Ingested at: 2026-06-05T08:54:05.763567)
- **[client_alpha]** Asset `P-155` logged a delay of **425.0 hours** (Ingested at: 2026-06-05T08:54:06.673085)
- **[client_beta]** Asset `TRK-8035` logged a delay of **52.0 hours** (Ingested at: 2026-06-05T08:54:10.141393)
- **[client_beta]** Asset `TRK-8050` logged a delay of **615.0 hours** (Ingested at: 2026-06-05T08:54:11.615763)

## Data Quality Audit Log Breakdowns
### Tenant: `client_beta` | Type: `DATE_FORMAT_ERROR`
- Details: *Expected %Y-%m-%d %H:%M:%S, structural failure: time data 'INVALID_DATE' does not match format '%Y-%m-%d %H:%M:%S'*
### Tenant: `client_beta` | Type: `DATE_FORMAT_ERROR`
- Details: *Expected %Y-%m-%d %H:%M:%S, structural failure: time data 'INVALID_DATE' does not match format '%Y-%m-%d %H:%M:%S'*
### Tenant: `client_beta` | Type: `DATE_FORMAT_ERROR`
- Details: *Expected %Y-%m-%d %H:%M:%S, structural failure: time data 'INVALID_DATE' does not match format '%Y-%m-%d %H:%M:%S'*
### Tenant: `client_beta` | Type: `DATE_FORMAT_ERROR`
- Details: *Expected %Y-%m-%d %H:%M:%S, structural failure: time data 'INVALID_DATE' does not match format '%Y-%m-%d %H:%M:%S'*
### Tenant: `client_beta` | Type: `DATE_FORMAT_ERROR`
- Details: *Expected %Y-%m-%d %H:%M:%S, structural failure: time data 'INVALID_DATE' does not match format '%Y-%m-%d %H:%M:%S'*
### Tenant: `client_beta` | Type: `DATE_FORMAT_ERROR`
- Details: *Expected %Y-%m-%d %H:%M:%S, structural failure: time data 'INVALID_DATE' does not match format '%Y-%m-%d %H:%M:%S'*
### Tenant: `client_beta` | Type: `DATE_FORMAT_ERROR`
- Details: *Expected %Y-%m-%d %H:%M:%S, structural failure: time data 'INVALID_TIMESTAMP_STRING' does not match format '%Y-%m-%d %H:%M:%S'*
### Tenant: `client_beta` | Type: `DATE_FORMAT_ERROR`
- Details: *Expected %Y-%m-%d %H:%M:%S, structural failure: time data 'INVALID_TIMESTAMP_STRING' does not match format '%Y-%m-%d %H:%M:%S'*
### Tenant: `client_beta` | Type: `DATA_VALIDATION_ERROR`
- Details: *[{"type":"value_error","loc":["delay_hours"],"msg":"Value error, Value cannot be NaN (Not a Number)","input":NaN,"ctx":{"error":"Value cannot be NaN (Not a Number)"},"url":"https://errors.pydantic.dev/2.13/v/value_error"}]*
