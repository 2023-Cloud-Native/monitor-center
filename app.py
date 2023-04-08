import threading
import time
from flask import Flask, jsonify

from api import ReservoirManager, ElectricityManager, EarthquakeManager

# Set up update thread before app to avoid errors
data_manager = {
    "reservoir": [ReservoirManager(), 3600],
    "electricity": [ElectricityManager(), 60],
    "earthquake": [EarthquakeManager(), 100],
}


def update(data, update_cycle):
    while True:
        data.update()
        time.sleep(update_cycle)


thread_manager = [
    threading.Thread(target=update, args=(*data,), daemon=True)
    for data in data_manager.values()
]
for thread in thread_manager:
    thread.start()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route("/", methods=["GET"])
def hello_world():
    all_data = {
        resource_name: resource_val[0].data
        for resource_name, resource_val in data_manager.items()
    }
    return jsonify(all_data)


if __name__ == "__main__":
    app.run()
