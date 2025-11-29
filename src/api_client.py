"""
Open-Meteo API Client
Fetches current weather data from Open-Meteo API
"""

import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WeatherAPIClient:
    """Client for fetching weather data from Open-Meteo API"""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, config):
        self.config = config

    def get_current_weather(self, latitude, longitude):
        """
        Fetch current weather data for given coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            dict: Weather data with temperature, precipitation, wind_speed, humidity, weather_code
                  Returns None if request fails
        """
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,precipitation,wind_speed_10m,relative_humidity_2m,weather_code",
                "timezone": "auto",
            }

            logger.info(f"Fetching weather data for coordinates: {latitude}, {longitude}")
            response = requests.get(self.BASE_URL, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})

                weather_data = {
                    "timestamp": datetime.utcnow(),
                    "temperature": current.get("temperature_2m"),
                    "precipitation": current.get("precipitation", 0),
                    "wind_speed": current.get("wind_speed_10m"),
                    "humidity": current.get("relative_humidity_2m"),
                    "weather_code": current.get("weather_code"),
                }

                logger.info(f"Weather data fetched successfully: {weather_data}")
                return weather_data
            else:
                logger.error(f"API request failed with status {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None
