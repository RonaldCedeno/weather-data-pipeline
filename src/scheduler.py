"""
Scheduler for Weather Data Pipeline
Uses APScheduler to run pipeline at regular intervals
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class WeatherScheduler:
    """Scheduler for automated weather data collection"""

    def __init__(self, pipeline_function):
        """
        Initialize scheduler
        
        Args:
            pipeline_function: Function to execute on schedule
        """
        self.pipeline_function = pipeline_function
        self.scheduler = BackgroundScheduler()
        self.job = None

    def start(self):
        """Start the scheduler"""
        try:
            # Import config to get interval
            from src.config import Config
            config = Config()

            # Add job to scheduler
            self.job = self.scheduler.add_job(
                func=self.pipeline_function,
                trigger=IntervalTrigger(minutes=config.SCHEDULE_INTERVAL_MINUTES),
                id="weather_pipeline",
                name="Weather Data Pipeline",
                replace_existing=True,
            )

            self.scheduler.start()
            logger.info(
                f"Scheduler started. Running every {config.SCHEDULE_INTERVAL_MINUTES} minutes"
            )

        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise

    def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")

    def is_running(self):
        """Check if scheduler is running"""
        return self.scheduler.running
