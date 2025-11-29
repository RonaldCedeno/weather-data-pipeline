"""
Database operations for Weather Data Pipeline
Handles connections to CockroachDB and data insertion
"""

import psycopg2
import logging
from datetime import datetime
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class Database:
    """Database connection and operations handler"""

    def __init__(self, config):
        self.config = config
        self.connection = None

    def _get_connection(self):
        """Get database connection"""
        if self.connection is None or self.connection.closed:
            try:
                self.connection = psycopg2.connect(self.config.DATABASE_URL)
                logger.info("Database connection established")
            except Exception as e:
                logger.error(f"Failed to connect to database: {str(e)}")
                raise
        return self.connection

    def test_connection(self):
        """
        Test database connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

    def insert_weather_data(self, location, latitude, longitude, weather_data):
        """
        Insert weather data into database
        
        Args:
            location: Location name
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            weather_data: Dictionary with weather data
            
        Returns:
            bool: True if insertion successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO weather_data 
                (timestamp, location, latitude, longitude, temperature, precipitation, wind_speed, humidity, weather_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                weather_data.get("timestamp"),
                location,
                latitude,
                longitude,
                weather_data.get("temperature"),
                weather_data.get("precipitation"),
                weather_data.get("wind_speed"),
                weather_data.get("humidity"),
                weather_data.get("weather_code"),
            )

            cursor.execute(query, values)
            conn.commit()
            cursor.close()

            logger.info(f"Weather data inserted successfully for {location}")
            return True

        except Exception as e:
            logger.error(f"Failed to insert weather data: {str(e)}")
            if conn:
                conn.rollback()
            return False

    def insert_alert_log(self, alert_type, severity, message, email_sent=False):
        """
        Insert alert log entry
        
        Args:
            alert_type: Type of alert
            severity: Alert severity (LOW, MEDIUM, HIGH, CRITICAL)
            message: Alert message
            email_sent: Whether email was sent
            
        Returns:
            bool: True if insertion successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO alert_log (timestamp, alert_type, severity, message, email_sent)
                VALUES (%s, %s, %s, %s, %s)
            """

            values = (datetime.utcnow(), alert_type, severity, message, email_sent)

            cursor.execute(query, values)
            conn.commit()
            cursor.close()

            logger.info(f"Alert log inserted: {alert_type} - {severity}")
            return True

        except Exception as e:
            logger.error(f"Failed to insert alert log: {str(e)}")
            if conn:
                conn.rollback()
            return False

    def get_recent_alerts(self, alert_type, hours):
        """
        Get recent alerts of a specific type within the last N hours
        
        Args:
            alert_type: Type of alert to check
            hours: Number of hours to look back
            
        Returns:
            list: List of alert records
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT * FROM alert_log
                WHERE alert_type = %s 
                AND timestamp > NOW() - INTERVAL '%s hours'
                ORDER BY timestamp DESC
            """

            cursor.execute(query, (alert_type, hours))
            results = cursor.fetchall()
            cursor.close()

            return results

        except Exception as e:
            logger.error(f"Failed to get recent alerts: {str(e)}")
            return []

    def close(self):
        """Close database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            logger.info("Database connection closed")

