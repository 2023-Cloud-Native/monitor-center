import time
import threading

from api.models import DBSession, Reservoir, Electricity, Earthquake
from api.manager import ReservoirManager, ElectricityManager, EarthquakeManager


def update(data, update_cycle):
    global run
    while run:
        time.sleep(update_cycle)
        data.update()


if __name__ == "__main__":
    run = True

    # Create database session
    session = DBSession()
    data_manager = {
        "reservoir": [ReservoirManager(session, Reservoir), 24 * 60 * 60],
        "electricity": [ElectricityManager(session, Electricity), 600],
        "earthquake": [EarthquakeManager(session, Earthquake), 300],
    }

    thread_manager = [
        threading.Thread(target=update, args=(*data,), daemon=True)
        for data in data_manager.values()
    ]

    for thread in thread_manager:
        thread.start()

    for thread in thread_manager:
        thread.join()
