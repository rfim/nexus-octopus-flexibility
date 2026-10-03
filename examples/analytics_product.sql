-- Illustrative certified consumer query; the Gold view owns the definition.
SELECT
    event_day,
    SUM(event_count) AS event_count,
    AVG(average_power_kw) AS average_asset_power_kw,
    MAX(latest_event_at) AS latest_event_at
FROM gold_daily_flexibility
GROUP BY event_day
ORDER BY event_day DESC;
