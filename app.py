import os
import threading
import time
from flask import Flask, jsonify
from flask_pymongo import PyMongo
import dotenv
from api import ReservoirManager, ElectricityManager, EarthquakeManager

# Requires to load the .env file
dotenv.load_dotenv()

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
monitor_db = PyMongo(
    app,
    uri=f"mongodb://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@{os.environ['MONGO_HOSTNAME']}:27017/{os.environ['MONGODB_DATABASE']}?authSource=monitor",
).db

# Set up update thread before app to avoid errors
data_manager = {
    "reservoir": [ReservoirManager(monitor_db.reservoir), 3600],
    "electricity": [ElectricityManager(monitor_db.electricity), 60],
    "earthquake": [EarthquakeManager(monitor_db.earthquake), 100],
}


def update(data, update_cycle):
    while True:
        time.sleep(update_cycle)
        data.update()


thread_manager = [
    threading.Thread(target=update, args=(*data,), daemon=True)
    for data in data_manager.values()
]
for thread in thread_manager:
    thread.start()


@app.route("/", methods=["GET"])
def index():
    all_data = {
        resource_name: resource_val[0].data
        for resource_name, resource_val in data_manager.items()
    }
    return jsonify(all_data)


if __name__ == "__main__":
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    app.run(host="0.0.0.0", port=ENVIRONMENT_PORT)
