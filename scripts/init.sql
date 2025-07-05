-- Create database if not exists
SELECT 'CREATE DATABASE smartcity'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'smartcity')\gexec

-- Connect to smartcity database
\c smartcity;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE severity_level AS ENUM ('low', 'medium', 'high', 'critical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('user', 'admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_measurements_location_timestamp 
ON measurements(location_name, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_measurements_timestamp 
ON measurements(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_measurements_pm25 
ON measurements(pm25) 
WHERE pm25 IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_predictions_location_target 
ON predictions(location_name, target_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_active 
ON alerts(is_active, created_at DESC) 
WHERE is_active = true;

-- Create materialized view for hourly aggregates
CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_measurements AS
SELECT 
    location_name,
    date_trunc('hour', timestamp) as hour,
    AVG(temperature) as avg_temperature,
    AVG(humidity) as avg_humidity,
    AVG(pm25) as avg_pm25,
    AVG(pm10) as avg_pm10,
    MAX(pm25) as max_pm25,
    MIN(pm25) as min_pm25,
    COUNT(*) as measurement_count
FROM measurements
GROUP BY location_name, date_trunc('hour', timestamp);

CREATE INDEX IF NOT EXISTS idx_hourly_measurements 
ON hourly_measurements(location_name, hour DESC);

-- Create function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_hourly_measurements()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY hourly_measurements;
END;
$$ LANGUAGE plpgsql;

-- Create function to auto-update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_users_updated_at') THEN
        CREATE TRIGGER update_users_updated_at 
        BEFORE UPDATE ON users 
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_alert_configs_updated_at') THEN
        CREATE TRIGGER update_alert_configs_updated_at 
        BEFORE UPDATE ON alert_configs 
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- Create partitioning for measurements table (optional, for large datasets)
-- This creates monthly partitions for better performance
DO $$ 
DECLARE
    start_date date := '2024-01-01';
    end_date date := '2025-12-31';
    partition_date date;
    partition_name text;
BEGIN
    partition_date := start_date;
    
    WHILE partition_date < end_date LOOP
        partition_name := 'measurements_' || to_char(partition_date, 'YYYY_MM');
        
        -- Check if partition exists
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = partition_name
        ) THEN
            EXECUTE format(
                'CREATE TABLE %I PARTITION OF measurements 
                FOR VALUES FROM (%L) TO (%L)',
                partition_name,
                partition_date,
                partition_date + interval '1 month'
            );
        END IF;
        
        partition_date := partition_date + interval '1 month';
    END LOOP;
END $$;

-- Insert default alert configurations
INSERT INTO alert_configs (parameter, threshold_value, severity, is_enabled)
VALUES 
    ('pm25', 35.0, 'medium', true),
    ('pm25', 55.0, 'high', true),
    ('pm25', 150.0, 'critical', true),
    ('pm10', 50.0, 'medium', true),
    ('pm10', 100.0, 'high', true),
    ('aqi', 100, 'medium', true),
    ('aqi', 150, 'high', true),
    ('aqi', 200, 'critical', true)
ON CONFLICT DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;