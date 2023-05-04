from datetime import datetime, timedelta
from collections import namedtuple, defaultdict
import os
import requests

import pandas as pd

from api.utils import Base, to_float, reservoir_data


class ReservoirManager(Base):
    def __init__(self, database=None):
        self.reservoir_overall_url = "https://data.wra.gov.tw/OpenAPI/api/OpenData/50C8256D-30C5-4B8D-9B84-2E14D5C6DF71/Data?size=1000&page=1"
        self.reservoir_detail_url = "https://data.wra.gov.tw/OpenAPI/api/OpenData/1602CA19-B224-4CC3-AA31-11B1B124530F/Data?size=1000&page=1"
        self.data = defaultdict(dict)
        self.update_time = None
        super().__init__(time_pattern="%Y-%m-%dT%H:%M:%S", database=database)

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
        for datum in overall_data:
            id_ = datum["ReservoirIdentifier"]

            if id_ not in reservoir_data["id_to_name"]:
                continue

            id_ = reservoir_data["id_to_name"][id_]

            self.data[id_]["total_capacity"] = to_float(datum["EffectiveCapacity"])
            self.data[id_]["inflow"] = to_float(datum["InflowVolume"])
            self.data[id_]["outflow"] = to_float(datum["OutflowTotal"])
            self.data[id_]["updated_time"] = self.format_time(datum["RecordTime"])

    def update_reservoir_details(self):
        detail_data = self.get_info("details")
        for datum in detail_data:
            if datum["ReservoirIdentifier"] not in reservoir_data["id_to_name"]:
                continue
            
            id_ = reservoir_data["id_to_name"][datum["ReservoirIdentifier"]]
            if id_ not in self.data:
                continue

            observed_time = self.format_time(datum["ObservationTime"])
            if (
                "updated_time" not in self.data[id_]
                or self.data[id_]["updated_time"] < observed_time
            ):
                self.data[id_]["updated_time"] = observed_time
                self.data[id_]["current_capacity"] = to_float(
                    datum["EffectiveWaterStorageCapacity"]
                )

    def update_func(self):
        self.update_reservoir_overall()
        self.update_reservoir_details()

    def update_database(self):
        pass
        # self.database.insert_one({"data": self.data})


class ElectricityManager(Base):
    def __init__(self, database=None):
        self.gen_use_url = "https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/genloadareaperc.csv"
        self.data = None
        self.update_time = None
        self.prototype = namedtuple("Elec", ["gen", "use"])
        super().__init__(time_pattern="%Y-%m-%d %H:%M", database=database)

    def update_func(self):
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
        except Exception as e:
            print(str(e))
            self.data = {
                "updated_time": "N/A",
                "north": self.prototype(0, 0),
                "central": self.prototype(0, 0),
                "south": self.prototype(0, 0),
                "east": self.prototype(0, 0),
            }
            return

        if self.is_outdated(data.iloc[0, 0]):
            self.data = {
                "updated_time": self.last_updated_time,
                "north": self.prototype(data.iloc[0, 1], data.iloc[0, 2]),
                "central": self.prototype(data.iloc[0, 3], data.iloc[0, 4]),
                "south": self.prototype(data.iloc[0, 5], data.iloc[0, 6]),
                "east": self.prototype(data.iloc[0, 7], data.iloc[0, 8]),
            }

    def is_outdated(self, new_time):
        new_time = self.format_time(new_time)
        if self.update_time is None or new_time > self.update_time:
            self.update_time = new_time
            return True
        else:
            return False

    def update_database(self):
        # Insert data by Flask_mongo
        self.database.insert_one({"time": self.update_time, "data": self.data})


class EarthquakeManager(Base):
    def __init__(self, database=None):
        self.large_url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/E-A0015-001"
        self.small_url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/E-A0016-001"
        self.auth = os.environ.get("CWB_AUTH")
        self.data = {"northen": [], "central": [], "southen": []}
        self.update_time = datetime.now()
        super().__init__(time_pattern="%Y-%m-%d %H:%M:%S", database=database)

    def get_thirty_day_str(self):
        # Reference: 2023-03-03T00:00:00
        return datetime.strftime(
            self.update_time - timedelta(days=30), "%Y-%m-%dT%H:%M:%S"
        )

    def process_data(self, data, type):
        for earthquake in data:
            earthquake_info = earthquake["EarthquakeInfo"]
            time = earthquake_info["OriginTime"]
            # TODO: pga and pgv can be calculated here, left for future work
            """
            depth = earthquake_info["FocalDepth"]
            center = earthquake_info["Epicenter"]["Location"]
            magnitude = earthquake_info["EarthquakeMagnitude"]["MagnitudeValue"]
            """

            shaking_areas = earthquake["Intensity"]["ShakingArea"]
            for area in shaking_areas:
                area_names = area["CountyName"].split("、")

                for area_name in area_names:
                    if area_name not in reservoir_data["county_to_area"]:
                        continue

                    observe_intensity = area["AreaIntensity"]

                    self.data[reservoir_data["county_to_area"][area_name]].append(
                        {
                            "area": area_name,
                            "time": self.format_time(time),
                            "type": type,
                            "observe_intensity": observe_intensity,
                        }
                    )

    def get_info(self, type_="s"):
        use_url = self.large_url if type_ == "l" else self.small_url
        data = requests.get(
            f"{use_url}?Authorization={self.auth}&format=JSON&timeFrom={self.get_thirty_day_str()}"
        )
        if data.status_code == 200:
            return data.json()["records"]["Earthquake"]
        else:
            print(data.status_code)
            return []

    def sort_earthquake_by_time(self):
        for key in self.data.keys():
            self.data[key].sort(key=lambda x: x["time"], reverse=True)

    def update_func(self):
        self.process_data(self.get_info("l"), "l")
        self.process_data(self.get_info("s"), "s")
        self.sort_earthquake_by_time()

    def update_database(self):
        # Insert data by Flask_mongo
        pass
        # self.database.insert_one({"time": self.update_time, "data": self.data})
