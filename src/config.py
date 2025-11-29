"""
Configuration management for Weather Data Pipeline
Loads environment variables from .env file
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class that loads settings from environment variables"""

    def __init__(self):
        # Database configuration
        self.DATABASE_URL = os.getenv("DATABASE_URL", "")

        # Email configuration
        self.EMAIL_FROM = os.getenv("EMAIL_FROM", "")
        self.EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
        self.EMAIL_TO = os.getenv("EMAIL_TO", "")

        # Location configuration
        self.LOCATION = os.getenv("LOCATION", "Vancouver")
        self.LATITUDE = float(os.getenv("LATITUDE", "49.2827"))
        self.LONGITUDE = float(os.getenv("LONGITUDE", "-123.1207"))

        # Alert thresholds
        self.HEAVY_RAIN_THRESHOLD = float(os.getenv("HEAVY_RAIN_THRESHOLD", "10.0"))
        self.STRONG_WIND_THRESHOLD = float(os.getenv("STRONG_WIND_THRESHOLD", "50.0"))
        self.EXTREME_TEMP_LOW = float(os.getenv("EXTREME_TEMP_LOW", "0.0"))
        self.EXTREME_TEMP_HIGH = float(os.getenv("EXTREME_TEMP_HIGH", "35.0"))

        # Scheduler configuration
        self.SCHEDULE_INTERVAL_MINUTES = int(os.getenv("SCHEDULE_INTERVAL_MINUTES", "60"))
        self.ALERT_COOLDOWN_HOURS = int(os.getenv("ALERT_COOLDOWN_HOURS", "6"))

    def validate(self):
        """Validate that required configuration is present"""
        required = [
            self.DATABASE_URL,
            self.EMAIL_FROM,
            self.EMAIL_PASSWORD,
            self.EMAIL_TO,
        ]
        return all(required)
