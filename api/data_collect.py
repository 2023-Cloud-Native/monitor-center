from pathlib import Path
import os
import time
import threading
import sys

sys.path.append(Path(__file__).resolve().parent.parent.__str__())
os.environ["USE_WRITE_DB"] = "True"

from api.database import init_db, session_maker_modify
from api.models import Reservoir, Electricity, Earthquake
from api.manager import ReservoirManager, ElectricityManager, EarthquakeManager


def update(data, update_cycle):
    global run
    while run:
        time.sleep(update_cycle)
        data.update()


if __name__ == "__main__":
    run = True

    # Create database session
    init_db()
    data_manager = {
        "reservoir": [ReservoirManager(session_maker_modify, Reservoir), 60 * 60],
        "electricity": [ElectricityManager(session_maker_modify, Electricity), 60 * 10],
        "earthquake": [EarthquakeManager(session_maker_modify, Earthquake), 60 * 5],
    }

    thread_manager = [
        threading.Thread(target=update, args=(*data,), daemon=True)
        for data in data_manager.values()
    ]

    for thread in thread_manager:
        thread.start()

    for thread in thread_manager:
        thread.join()
