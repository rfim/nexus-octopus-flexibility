-- Illustrative PostgreSQL source contract for the portfolio diagram.
CREATE TABLE source_events (
    id BIGINT PRIMARY KEY,
    revision INTEGER NOT NULL CHECK (revision >= 0),
    asset_id TEXT NOT NULL,
    power_watts DOUBLE PRECISION NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX source_events_updated_at_idx ON source_events (updated_at);
