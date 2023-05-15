import time
import signal
import threading

from api.models import DBSession, Reservoir, Electricity, Earthquake
from api import ReservoirManager, ElectricityManager, EarthquakeManager


def exit_thread(signum, frame):
    global run
    run = False


def update(data, update_cycle):
    global run
    while run:
        time.sleep(update_cycle)
        data.update()


if __name__ == "__main__":
    run = True
    signal.signal(signal.SIGINT, exit_thread)

    # Create database session
    session = DBSession()
    data_manager = {
        "reservoir": [ReservoirManager(session, Reservoir), 3600],
        "electricity": [ElectricityManager(session, Electricity), 60],
        "earthquake": [EarthquakeManager(session, Earthquake), 100],
    }

    thread_manager = [
        threading.Thread(target=update, args=(*data,), daemon=True)
        for data in data_manager.values()
    ]

    for thread in thread_manager:
        thread.start()

    for thread in thread_manager:
        thread.join()
