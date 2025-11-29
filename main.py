"""
Weather Data Pipeline - Main Application
Data Warehouse Project
"""

import os
import time
import logging
from datetime import datetime
from src.config import Config
from src.api_client import WeatherAPIClient
from src.database import Database
from src.alert_engine import AlertEngine
from src.scheduler import WeatherScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("weather_pipeline.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def run_pipeline():
    """Execute one cycle of the weather data pipeline"""
    try:
        logger.info("=" * 50)
        logger.info("Starting weather pipeline execution")

        # Initialize components
        config = Config()
        api_client = WeatherAPIClient(config)
        database = Database(config)
        alert_engine = AlertEngine(config, database)

        # Step 1: Fetch weather data
        logger.info("Step 1: Fetching weather data from API")
        weather_data = api_client.get_current_weather(
            latitude=config.LATITUDE, longitude=config.LONGITUDE
        )

        if not weather_data:
            logger.error("Failed to fetch weather data")
            return False

        logger.info(f"Weather data fetched successfully: {weather_data}")

        # Step 2: Store data in database
        logger.info("Step 2: Storing data in database")
        success = database.insert_weather_data(
            location=config.LOCATION,
            latitude=config.LATITUDE,
            longitude=config.LONGITUDE,
            weather_data=weather_data,
        )

        if not success:
            logger.error("Failed to store weather data")
            return False

        logger.info("Data stored successfully")

        # Step 3: Check for alerts
        logger.info("Step 3: Checking for weather alerts")
        alert_engine.check_and_send_alerts(weather_data)

        logger.info("Pipeline execution completed successfully")
        logger.info("=" * 50)
        return True

    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
        return False


def main():
    """Main entry point"""
    logger.info("Weather Data Pipeline Starting...")
    logger.info(f"Current time: {datetime.now()}")

    # Load configuration
    config = Config()
    logger.info(f"Monitoring location: {config.LOCATION}")
    logger.info(f"Coordinates: {config.LATITUDE}, {config.LONGITUDE}")

    # Test database connection
    db = Database(config)
    if not db.test_connection():
        logger.error("Database connection failed. Please check configuration.")
        return

    logger.info("Database connection successful")

    # Run once immediately
    logger.info("Running initial pipeline execution...")
    run_pipeline()

    # Start scheduler
    logger.info("Starting scheduler for automated runs...")
    scheduler = WeatherScheduler(run_pipeline)
    scheduler.start()

    # Keep the program running
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down weather pipeline...")
        scheduler.stop()
        logger.info("Pipeline stopped successfully")


if __name__ == "__main__":
    main()

