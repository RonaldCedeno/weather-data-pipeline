-- Weather Data Pipeline Database Schema
-- CockroachDB / PostgreSQL

-- Create weather_data table
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    location VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    temperature DECIMAL(5,2),
    precipitation DECIMAL(6,2),
    wind_speed DECIMAL(6,2),
    humidity INT,
    weather_code INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_weather_timestamp ON weather_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_weather_location ON weather_data(location);
CREATE INDEX IF NOT EXISTS idx_weather_created ON weather_data(created_at);

-- Create alert_log table
CREATE TABLE IF NOT EXISTS alert_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    email_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for alert queries
CREATE INDEX IF NOT EXISTS idx_alert_timestamp ON alert_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_alert_type ON alert_log(alert_type);
CREATE INDEX IF NOT EXISTS idx_alert_created ON alert_log(created_at);

-- Create view for recent weather data
CREATE OR REPLACE VIEW recent_weather AS
SELECT 
    location,
    timestamp,
    temperature,
    precipitation,
    wind_speed,
    humidity,
    weather_code
FROM weather_data
WHERE timestamp > NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;

-- Create view for alert summary
CREATE OR REPLACE VIEW alert_summary AS
SELECT 
    alert_type,
    severity,
    COUNT(*) as alert_count,
    MAX(timestamp) as last_alert,
    SUM(CASE WHEN email_sent THEN 1 ELSE 0 END) as emails_sent
FROM alert_log
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY alert_type, severity
ORDER BY alert_count DESC;

-- Insert sample comment for documentation
COMMENT ON TABLE weather_data IS 'Stores historical weather data collected from Open-Meteo API';
COMMENT ON TABLE alert_log IS 'Logs all weather alerts triggered by the system';
COMMENT ON COLUMN weather_data.weather_code IS 'WMO Weather interpretation code';
COMMENT ON COLUMN alert_log.severity IS 'Alert severity: LOW, MEDIUM, HIGH, CRITICAL';

