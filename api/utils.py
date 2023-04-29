from datetime import datetime
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M",
    handlers=[logging.FileHandler("data.log", "w", "utf-8")],
)


def to_float(capacity):
    if capacity == "":
        return 0
    return float(capacity)


def get_json_file(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)


class Base:
    def __init__(self, time_pattern, database):
        self.time_pattern = time_pattern
        self.database = database
        self.update()

    def format_time(self, datetime_str):
        return datetime.strptime(datetime_str, self.time_pattern)

    def update_database():
        raise NotImplementedError

    def update(self):
        self.update_func()
        self.update_database()
        logging.info(
            f"Update {self.__class__.__name__.replace('Manager', '').lower()} data"
        )

    @property
    def last_updated_time(self):
        return datetime.strftime(self.update_time, "%Y-%m-%d %H:%M:%S")


reservoir_data = get_json_file("reservoir.json")
