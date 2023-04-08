from datetime import datetime
import json


def to_float(capacity):
    if capacity == "":
        return 0
    return float(capacity)


def get_json_file(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)


class Base:
    def __init__(self, time_pattern):
        self.time_pattern = time_pattern
        self.update()

    def format_time(self, datetime_str):
        return datetime.strptime(datetime_str, self.time_pattern)

    def update(self):
        raise NotImplementedError

    @property
    def last_updated_time(self):
        return datetime.strftime(self.update_time, "%Y-%m-%d %H:%M:%S")


reservoir_data = get_json_file("reservoir.json")
