import threading
import time
from flask import Flask, jsonify
from flask_pymongo import PyMongo

from api import ReservoirManager, ElectricityManager, EarthquakeManager


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
mongo = PyMongo(app, uri="mongodb://localhost:27017/monitor")

# Set up update thread before app to avoid errors
data_manager = {
    "reservoir": [ReservoirManager(mongo.db.reservoir), 3600],
    "electricity": [ElectricityManager(mongo.db.electricity), 60],
    "earthquake": [EarthquakeManager(mongo.db.earthquake), 100],
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
    app.run()
