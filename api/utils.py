from datetime import datetime
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s {%(pathname)s:%(lineno)d} %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M",
    handlers=[logging.FileHandler("logs/db/db.log", "a", "utf-8")],
)


def to_float(capacity):
    if capacity == "":
        return 0
    return float(capacity)


def get_json_file(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)


class Base:
    def __init__(self, time_pattern, database, instance_cls):
        self.time_pattern = time_pattern
        self.database = database
        self.instance_cls = instance_cls
        self.logging = logging  # Force the binding
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
        return datetime.strftime(self.updated_time, "%Y-%m-%d %H:%M:%S")


county_data = get_json_file("county_data.json")
