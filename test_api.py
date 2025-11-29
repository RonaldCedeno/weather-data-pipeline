from src.config import Config
from src.api_client import WeatherAPIClient

config = Config()
client = WeatherAPIClient(config)

data = client.get_current_weather(config.LATITUDE, config.LONGITUDE)

if data:
    print("Weather data obtained successfully!")
    print(f"Temperature: {data['temperature']}°C")
    print(f"Precipitation: {data['precipitation']} mm/h")
    print(f"Wind: {data['wind_speed']} km/h")
else:
    print("Error retrieving weather data")

