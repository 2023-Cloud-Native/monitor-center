from collections import defaultdict
from functools import wraps
import math
from datetime import datetime, timedelta
import os
import requests

import pandas as pd

from api.utils import Base, to_float, county_data


def geo_distance(geo_1, geo_2):
    lat1 = math.radians(geo_1[0])
    lon1 = math.radians(geo_1[1])
    lat2 = math.radians(geo_2[0])
    lon2 = math.radians(geo_2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 6373 * c


def compute_pga_pgv(epi_dist, focal_depth, scale, s):
    r = math.sqrt(epi_dist**2 + focal_depth**2)
    pga = 1.657 * math.exp(1.533 * scale) * r ** (-1.607) * s
    return pga, pga / 8.6561


class ReservoirManager(Base):
    def __init__(self, database=None, instance_cls=None):
        self.reservoir_overall_url = "https://data.wra.gov.tw/OpenAPI/api/OpenData/50C8256D-30C5-4B8D-9B84-2E14D5C6DF71/Data?size=1000&page=1"
        self.reservoir_detail_url = "https://data.wra.gov.tw/OpenAPI/api/OpenData/1602CA19-B224-4CC3-AA31-11B1B124530F/Data?size=1000&page=1"
        self.data = {
            "新竹": {},
            "臺中": {},
            "臺南": {},
        }
        self.require_update_database = False
        self.updated_time = None
        super().__init__(
            time_pattern="%Y-%m-%dT%H:%M:%S",
            database=database,
            instance_cls=instance_cls,
        )

    def get_info(self, type_):
        url = (
            self.reservoir_overall_url
            if type_ == "overall"
            else self.reservoir_detail_url
        )
        try:
            data = requests.get(url)
            if data.status_code == 200:
                return data.json()["responseData"]
            else:
                raise requests.exceptions.RequestException
        except requests.exceptions.RequestException:
            return []

    def update_reservoir_overall(self):
        overall_data = self.get_info("overall")
        if not len(overall_data):
            self.require_update_database = False
            return

        for datum in overall_data:
            id_ = datum["ReservoirIdentifier"]

            if id_ not in county_data["id_to_county"]:
                continue

            town_name = county_data["id_to_county"][id_]
            if "current_capacity" not in self.data[town_name]:
                self.data[town_name]["current_capacity"] = 0.0

            if "inflow" not in self.data[town_name]:
                self.data[town_name]["inflow"] = 0.0

            if "outflow" not in self.data[town_name]:
                self.data[town_name]["outflow"] = 0.0

            self.data[town_name]["current_capacity"] += to_float(
                datum["EffectiveCapacity"]
            )
            self.data[town_name]["inflow"] += to_float(datum["InflowVolume"])
            self.data[town_name]["outflow"] += to_float(datum["OutflowTotal"])
            self.data[town_name]["updated_time"] = datetime.now()
        self.require_update_database = True

    def update_reservoir_details(self):
        detail_data = self.get_info("details")
        if not len(detail_data):
            self.require_update_database = False
            return

        for datum in detail_data:
            id_ = datum["ReservoirIdentifier"]
            if id_ not in county_data["id_to_county"]:
                continue

            town_name = county_data["id_to_county"][id_]

            if "total_capacity" not in self.data[town_name]:
                self.data[town_name]["total_capacity"] = 0.0

            self.data[town_name]["total_capacity"] += to_float(
                datum["EffectiveWaterStorageCapacity"]
            )
            self.data[town_name]["updated_time"] = datetime.now()

        for key in self.data.keys():
            self.data[key]["percentage"] = (
                self.data[key]["current_capacity"] / self.data[key]["total_capacity"]
            )
        self.require_update_database = True

    def update_func(self):
        self.data = {
            "新竹": defaultdict(float),
            "臺中": defaultdict(float),
            "臺南": defaultdict(float),
        }
        self.update_reservoir_overall()
        self.update_reservoir_details()

    def update_database(self):
        if self.database is not None and self.require_update_database:
            with self.database() as db_session:
                for town_name, town_data in self.data.items():
                    db_session.add(
                        self.instance_cls(
                            area=town_name,
                            current_capacity=town_data["current_capacity"],
                            total_capacity=town_data["total_capacity"],
                            percentage=town_data["percentage"],
                            inflow=town_data["inflow"],
                            outflow=town_data["outflow"],
                            updated_time=town_data["updated_time"],
                        )
                    )
                self.require_update_database = False


class ElectricityManager(Base):
    def __init__(self, database=None, instance_cls=None):
        self.gen_use_url = "https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/genloadareaperc.csv"
        self.data = None
        self.updated_time = None
        self.require_update_database = False
        super().__init__(
            time_pattern="%Y-%m-%d %H:%M", database=database, instance_cls=instance_cls
        )

    def update_func(self):
        RETRIES_LIMIT = 3
        success = False

        while RETRIES_LIMIT > 0:
            try:
                data = pd.read_csv(self.gen_use_url, header=None)
                data.columns = [
                    "time",
                    "north_gen",
                    "north_use",
                    "central_gen",
                    "central_use",
                    "south_gen",
                    "south_use",
                    "east_gen",
                    "east_use",
                ]
                success = True
                break
            except Exception as e:
                self.require_update_database = False
                self.data = {
                    "updated_time": "N/A",
                    "north_gen": 0,
                    "north_use": 0,
                    "central_gen": 0,
                    "central_use": 0,
                    "south_gen": 0,
                    "south_use": 0,
                }

        if not success:
            self.logging.error(f"Error: {str(e)} when fetching electricity data")

        if success and self.is_outdated(data.iloc[0, 0]):
            self.require_update_database = True
            self.data = {
                "updated_time": self.updated_time,
                "north_gen": data.iloc[0, 1],
                "north_use": data.iloc[0, 2],
                "central_gen": data.iloc[0, 3],
                "central_use": data.iloc[0, 4],
                "south_gen": data.iloc[0, 5],
                "south_use": data.iloc[0, 6],
            }

    def is_outdated(self, new_time):
        new_time = self.format_time(new_time)
        if self.updated_time is None or new_time > self.updated_time:
            self.updated_time = new_time
            return True
        else:
            return False

    def update_database(self):
        if self.database is not None and self.require_update_database:
            with self.database() as db_session:
                latest_data = db_session.query(self.instance_cls).first()
                if (
                    latest_data is not None
                    and latest_data.updated_time == self.updated_time
                ):
                    return

                instance = self.instance_cls(
                    north_generate=self.data["north_gen"],
                    north_usage=self.data["north_use"],
                    central_generate=self.data["central_gen"],
                    central_usage=self.data["central_use"],
                    south_generate=self.data["south_gen"],
                    south_usage=self.data["south_use"],
                    updated_time=self.data["updated_time"],
                )
                db_session.add(instance)
                self.require_update_database = False


class EarthquakeManager(Base):
    def __init__(self, database=None, instance_cls=None):
        self.large_url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/E-A0015-001"
        self.small_url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/E-A0016-001"
        self.auth = os.environ.get("CWB_AUTH")
        self.require_update_database = False
        self.data = {
            "新竹": [],
            "臺中": [],
            "臺南": [],
        }
        self.updated_time = datetime.now()
        super().__init__(
            time_pattern="%Y-%m-%d %H:%M:%S",
            database=database,
            instance_cls=instance_cls,
        )

    def reset(self):
        self.data = {
            "新竹": [],
            "臺中": [],
            "臺南": [],
        }

    def get_thirty_day_str(self):
        # Reference: 2023-03-03T00:00:00
        return datetime.strftime(
            self.updated_time - timedelta(days=30), "%Y-%m-%dT%H:%M:%S"
        )

    def process_data(self, data):
        for earthquake in data:
            earthquake_info = earthquake["EarthquakeInfo"]
            earthquake_number = earthquake["EarthquakeNo"]
            time = earthquake_info["OriginTime"]
            depth = earthquake_info["FocalDepth"]
            magnitude = earthquake_info["EarthquakeMagnitude"]["MagnitudeValue"]
            center = earthquake_info["Epicenter"]
            latitude = center["EpicenterLatitude"]
            longitude = center["EpicenterLongitude"]
            location = center["Location"]

            for area in self.data:
                pga, pgv = compute_pga_pgv(
                    geo_distance(
                        county_data["county_pos"][area],
                        (latitude, longitude),
                    ),
                    depth,
                    magnitude,
                    county_data["county_pos"][area][2],
                )
                self.data[area].append(
                    {
                        "source": location[:3],
                        "number": earthquake_number,
                        "observed_time": self.format_time(time),
                        "pga": pga,
                        "pgv": pgv,
                    }
                )

    def get_info(self, type_="s"):
        use_url = self.large_url if type_ == "l" else self.small_url
        data = requests.get(
            f"{use_url}?Authorization={self.auth}&format=JSON&timeFrom={self.get_thirty_day_str()}"
        )
        if data.status_code == 200:
            self.require_update_database = True
            return data.json()["records"]["Earthquake"]
        else:
            self.require_update_database = False
            self.logging.error(
                f"Error: {data.status_code} code when fetching earthquake data"
            )
            return {}

    def sort_earthquake_by_time(self):
        for key in self.data.keys():
            self.data[key].sort(key=lambda x: x["observed_time"], reverse=True)

    def update_func(self):
        self.reset()
        self.process_data(self.get_info("l"))
        self.process_data(self.get_info("s"))
        self.sort_earthquake_by_time()

    def update_database(self):
        if self.database is not None and self.require_update_database:
            with self.database() as db_session:
                for town_name, earthquake_data in self.data.items():
                    for earthquake_datum in earthquake_data:
                        earthquake_observed_time = earthquake_datum["observed_time"]
                        if (
                            db_session.query(self.instance_cls)
                            .filter(self.instance_cls.observed_time == earthquake_observed_time)
                            .filter(self.instance_cls.area == town_name)
                            .first()
                            is not None
                        ):
                            continue

                        db_session.add(
                            self.instance_cls(
                                area=town_name,
                                source=earthquake_datum["source"],
                                pga=earthquake_datum["pga"],
                                pgv=earthquake_datum["pgv"],
                                observed_time=earthquake_datum["observed_time"],
                            )
                        )
                self.require_update_database = False
