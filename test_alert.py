from datetime import datetime
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
