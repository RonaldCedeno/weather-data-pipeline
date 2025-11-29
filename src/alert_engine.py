"""
Alert Engine for Weather Data Pipeline
Checks weather conditions and sends email alerts
"""

import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class AlertEngine:
    """Handles weather alert detection and email notifications"""

    def __init__(self, config, database):
        self.config = config
        self.database = database

    def check_and_send_alerts(self, weather_data):
        """
        Check weather conditions and send alerts if thresholds are exceeded
        
        Args:
            weather_data: Dictionary with current weather data
        """
        alerts = []

        # Check heavy rain
        precipitation = weather_data.get("precipitation", 0)
        if precipitation and precipitation >= self.config.HEAVY_RAIN_THRESHOLD:
            alerts.append(
                {
                    "type": "HEAVY_RAIN",
                    "severity": "HIGH",
                    "message": f"Heavy rainfall detected: {precipitation} mm/h (Threshold: {self.config.HEAVY_RAIN_THRESHOLD} mm/h)",
                }
            )

        # Check strong wind
        wind_speed = weather_data.get("wind_speed", 0)
        if wind_speed and wind_speed >= self.config.STRONG_WIND_THRESHOLD:
            alerts.append(
                {
                    "type": "STRONG_WIND",
                    "severity": "HIGH",
                    "message": f"Strong wind detected: {wind_speed} km/h (Threshold: {self.config.STRONG_WIND_THRESHOLD} km/h)",
                }
            )

        # Check extreme temperatures
        temperature = weather_data.get("temperature")
        if temperature is not None:
            if temperature <= self.config.EXTREME_TEMP_LOW:
                alerts.append(
                    {
                        "type": "EXTREME_COLD",
                        "severity": "MEDIUM",
                        "message": f"Extreme cold detected: {temperature}°C (Threshold: {self.config.EXTREME_TEMP_LOW}°C)",
                    }
                )
            elif temperature >= self.config.EXTREME_TEMP_HIGH:
                alerts.append(
                    {
                        "type": "EXTREME_HEAT",
                        "severity": "HIGH",
                        "message": f"Extreme heat detected: {temperature}°C (Threshold: {self.config.EXTREME_TEMP_HIGH}°C)",
                    }
                )

        # Process each alert
        for alert in alerts:
            self._process_alert(alert, weather_data)

    def _process_alert(self, alert, weather_data):
        """
        Process a single alert (check cooldown and send if needed)
        
        Args:
            alert: Alert dictionary with type, severity, and message
            weather_data: Current weather data
        """
        alert_type = alert["type"]

        # Check if alert was sent recently (cooldown period)
        recent_alerts = self.database.get_recent_alerts(
            alert_type, self.config.ALERT_COOLDOWN_HOURS
        )

        if recent_alerts:
            logger.info(
                f"Alert {alert_type} is in cooldown period. Skipping notification."
            )
            # Still log the alert
            self.database.insert_alert_log(
                alert_type, alert["severity"], alert["message"], email_sent=False
            )
            return

        # Send email alert
        email_sent = self._send_email_alert(alert, weather_data)

        # Log alert to database
        self.database.insert_alert_log(
            alert_type, alert["severity"], alert["message"], email_sent=email_sent
        )

    def _send_email_alert(self, alert, weather_data):
        """
        Send email alert via Gmail SMTP
        
        Args:
            alert: Alert dictionary
            weather_data: Current weather data
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create email message
            msg = MIMEMultipart()
            msg["From"] = self.config.EMAIL_FROM
            msg["To"] = self.config.EMAIL_TO
            msg["Subject"] = f"Weather Alert: {alert['type'].replace('_', ' ').title()}"

            # Create email body
            body = f"""Subject: Weather Alert: {alert['type'].replace('_', ' ').title()} Detected
Location: {self.config.LOCATION}, Canada
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
Alert Type: {alert['type']}
Severity: {alert['severity']}
Current Conditions:
- Temperature: {weather_data.get('temperature', 'N/A')}°C
- Precipitation: {weather_data.get('precipitation', 0)} mm/h
- Wind Speed: {weather_data.get('wind_speed', 0)} km/h
- Humidity: {weather_data.get('humidity', 'N/A')}%
Action Required: {alert['message']}
This is an automated message from Weather Pipeline System.
"""

            msg.attach(MIMEText(body, "plain"))

            # Send email via Gmail SMTP
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.config.EMAIL_FROM, self.config.EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(self.config.EMAIL_FROM, self.config.EMAIL_TO, text)
            server.quit()

            logger.info(f"Email alert sent successfully: {alert['type']}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
            return False
