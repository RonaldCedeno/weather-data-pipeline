# Weather Data Pipeline Project

Automated weather monitoring system with real-time alerts and historical data storage.

## Project Overview

This project implements an end-to-end data pipeline that:

- Extracts weather data from Open-Meteo API (free, open-source)
- Sends email alerts for severe weather conditions
- Stores historical data in CockroachDB for analysis
- Runs continuously on scheduled intervals

**Built for:** Data Warehouse Course - Project Choice 1  
**Technologies:** Python, CockroachDB, Open-Meteo API, Gmail SMTP

---

## Project Structure

```
weather-pipeline/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── api_client.py      # Open-Meteo API integration
│   ├── database.py        # Database operations
│   ├── alert_engine.py    # Alert logic and email
│   └── scheduler.py       # Task scheduling
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
├── setup_database.sql     # Database schema
├── main.py                # Application entry point
└── README.md             # This file
```

---

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- CockroachDB account (free tier)
- Gmail account with App Password enabled

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/weather-pipeline.git
cd weather-pipeline
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure CockroachDB

1. Create a free account at [cockroachlabs.cloud](https://cockroachlabs.cloud)
2. Create a new serverless cluster
3. Download the CA certificate
4. Get your connection string (looks like: `postgresql://user:pass@host:26257/defaultdb`)
5. Run the database setup script:

```bash
# Connect to your database and run
psql "your-connection-string" < setup_database.sql
```

### Step 4: Configure Gmail SMTP

1. Enable 2-Factor Authentication in your Gmail account
2. Go to Google Account → Security → App Passwords
3. Generate a new app password for "Mail"
4. Save this 16-character password

### Step 5: Configure Environment Variables

1. Copy the example file:

```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:

```bash
DATABASE_URL=postgresql://your-user:your-pass@your-host:26257/defaultdb
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
EMAIL_TO=recipient@example.com
LOCATION=YourCity
LATITUDE=your-latitude
LONGITUDE=your-longitude
```

### Step 6: Test the Application

```bash
python main.py
```

You should see logs indicating:

- Database connection successful
- Weather data fetched
- Data stored in database
- Scheduler started

---

## Configuration Options

Edit `.env` file to customize:

| Variable                    | Description               | Default |
| --------------------------- | ------------------------- | ------- |
| `HEAVY_RAIN_THRESHOLD`      | Rain threshold (mm/h)     | 10      |
| `STRONG_WIND_THRESHOLD`     | Wind threshold (km/h)     | 50      |
| `EXTREME_TEMP_LOW`          | Low temp alert (°C)       | 0       |
| `EXTREME_TEMP_HIGH`         | High temp alert (°C)      | 35      |
| `SCHEDULE_INTERVAL_MINUTES` | Data collection frequency | 60      |
| `ALERT_COOLDOWN_HOURS`      | Hours between same alerts | 6       |

---

## Database Schema

### weather_data table

- `id`: Auto-incrementing primary key
- `timestamp`: Weather observation time
- `location`: Location name
- `latitude`, `longitude`: Coordinates
- `temperature`: Temperature in °C
- `precipitation`: Rain in mm/hour
- `wind_speed`: Wind speed in km/h
- `humidity`: Relative humidity (%)
- `weather_code`: WMO weather code

### alert_log table

- `id`: Auto-incrementing primary key
- `timestamp`: Alert time
- `alert_type`: Type of alert
- `severity`: LOW, MEDIUM, HIGH, CRITICAL
- `message`: Alert description
- `email_sent`: Whether email was delivered

---

## Deployment to PythonAnywhere

### 1. Create Account

- Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
- Choose the free "Beginner" plan

### 2. Upload Files

```bash
# From your local terminal
scp -r weather-pipeline/* yourusername@ssh.pythonanywhere.com:~/weather-pipeline/
```

Or use the PythonAnywhere web interface to upload files.

### 3. Install Dependencies

In PythonAnywhere bash console:

```bash
cd ~/weather-pipeline
pip3 install --user -r requirements.txt
```

### 4. Set Environment Variables

Create `.env` file in PythonAnywhere:

```bash
nano .env
# Paste your configuration
# Press Ctrl+X, then Y, then Enter to save
```

### 5. Create Scheduled Task

1. Go to "Tasks" tab
2. Create a new scheduled task
3. Set frequency: Hourly (or your preferred interval)
4. Command: `python3 /home/yourusername/weather-pipeline/main.py`

### 6. Monitor Logs

Check logs in PythonAnywhere:

```bash
cat ~/weather-pipeline/weather_pipeline.log
```

---

## Email Alert Example

```
Subject: Weather Alert: Heavy Rain Detected
Location: Vancouver, Canada
Time: 2024-11-28 15:30 UTC
Alert Type: HEAVY_RAIN
Severity: HIGH
Current Conditions:
- Temperature: 7.8°C
- Precipitation: 14.2 mm/h
- Wind Speed: 32 km/h
- Humidity: 92%
Action Required: Heavy rainfall detected. Take necessary precautions.
This is an automated message from Weather Pipeline System.
```

---

## Testing

### Test Database Connection

```python
from src.config import Config
from src.database import Database

config = Config()
db = Database(config)
print("Connection test:", db.test_connection())
```

### Test API Client

```python
from src.config import Config
from src.api_client import WeatherAPIClient

config = Config()
client = WeatherAPIClient(config)
data = client.get_current_weather(config.LATITUDE, config.LONGITUDE)
print("Weather data:", data)
```

### Test Alert System

```python
from src.config import Config
from src.database import Database
from src.alert_engine import AlertEngine

config = Config()
db = Database(config)
alert_engine = AlertEngine(config, db)

# Simulate bad weather
test_data = {
    'timestamp': datetime.now(),
    'temperature': 30,
    'precipitation': 15,  # Above threshold
    'wind_speed': 60,     # Above threshold
    'humidity': 85
}

alert_engine.check_and_send_alerts(test_data)
```

---

## Querying Historical Data

### Recent Weather Data

```sql
SELECT * FROM recent_weather LIMIT 10;
```

### Alert Summary

```sql
SELECT * FROM alert_summary;
```

### Weather Trends

```sql
SELECT
    DATE(timestamp) as date,
    AVG(temperature) as avg_temp,
    MAX(precipitation) as max_rain,
    MAX(wind_speed) as max_wind
FROM weather_data
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

---

## Troubleshooting

### Database Connection Fails

- Verify `DATABASE_URL` is correct
- Check CockroachDB cluster is running
- Ensure firewall allows connection on port 26257

### Email Not Sending

- Verify Gmail App Password is correct (16 characters, no spaces)
- Check 2FA is enabled on Gmail account
- Verify `EMAIL_FROM` matches the Gmail account

### API Requests Failing

- Check internet connection
- Verify coordinates are valid (-90 to 90 for lat, -180 to 180 for lon)
- Open-Meteo API requires no authentication

### Scheduler Not Running

- Check logs for errors
- Verify `SCHEDULE_INTERVAL_MINUTES` is set correctly
- Ensure no other process is blocking execution

---

## Team Work Distribution

| Team Member | Tasks                                                                   | Hours |
| ----------- | ----------------------------------------------------------------------- | ----- |
| [Your Name] | - API integration<br>- Database design<br>- Alert system implementation | 15h   |
| [Your Name] | - Deployment setup<br>- Documentation<br>- Testing<br>- Video demo      | 10h   |

**Total Time:** 25 hours

---

## Resources

- **Open-Meteo API:** https://open-meteo.com/en/docs
- **CockroachDB Docs:** https://www.cockroachlabs.com/docs/
- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **APScheduler Docs:** https://apscheduler.readthedocs.io/

---

## License

This project is created for educational purposes as part of a Data Warehouse course.

---

## Demo Video

[Link to video demo will be added here]

Demo includes:

- Live data fetching from API
- Database storage verification
- Alert triggering demonstration
- Email notification showcase
- Historical data queries

---

## Contact

For questions or issues:

- Email: [your-email@example.com]
- GitHub: [your-github-username]
- Project Report: See `project_report.md`

---

**Last Updated:** November 28, 2024

