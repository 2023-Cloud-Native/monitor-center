import time
import threading

from flask import Blueprint, jsonify
from api import ReservoirManager, ElectricityManager, EarthquakeManager
from apps.app import db
from apps.api.models import Reservoir, Electricity, Earthquake

api = Blueprint("api", __name__)


def update(data, update_cycle):
    while True:
        time.sleep(update_cycle)
        data.update()


data_manager = {
    "reservoir": [ReservoirManager(db, Reservoir), 3600],
    "electricity": [ElectricityManager(db, Electricity), 60],
    "earthquake": [EarthquakeManager(db, Earthquake), 100],
    "start": False,
}

thread_manager = [
    threading.Thread(target=update, args=(*data,), daemon=True)
    for data in data_manager.values()
    if isinstance(data, list)
]


@api.route("/")
def index():
    if not data_manager.get("start", False):
        data_manager["start"] = True
        for thread in thread_manager:
            thread.start()

    all_data = {
        resource_name: resource_val[0].data
        for resource_name, resource_val in data_manager.items()
        if resource_name != "start"
    }
    return jsonify(all_data)
