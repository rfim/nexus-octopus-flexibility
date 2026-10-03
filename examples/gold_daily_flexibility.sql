-- Illustrative Databricks SQL model over a validated Delta Silver table.
-- Interval energy needs measured interval width; this model shows a daily
-- event-count and average-power product without claiming measured energy.
CREATE OR REPLACE VIEW gold_daily_flexibility AS
SELECT
    asset_id,
    DATE(to_timestamp(event_time)) AS event_day,
    COUNT(*) AS event_count,
    AVG(power_kw) AS average_power_kw,
    MAX(to_timestamp(event_time)) AS latest_event_at
FROM silver_events
GROUP BY asset_id, DATE(to_timestamp(event_time));
