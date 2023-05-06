from datetime import datetime, timedelta
import os
import requests

import pandas as pd

from api.utils import Base, to_float, reservoir_data


class ReservoirManager(Base):
    def __init__(self, database=None):
        self.reservoir_overall_url = "https://data.wra.gov.tw/OpenAPI/api/OpenData/50C8256D-30C5-4B8D-9B84-2E14D5C6DF71/Data?size=1000&page=1"
        self.reservoir_detail_url = "https://data.wra.gov.tw/OpenAPI/api/OpenData/1602CA19-B224-4CC3-AA31-11B1B124530F/Data?size=1000&page=1"
        self.data = {
            "桃園": dict(),
            "新竹": dict(),
            "臺中": dict(),
            "臺南": dict(),
        }
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

            if (
                id_ not in reservoir_data["id_to_name"]
                or reservoir_data["id_to_town_name"][id_][:2] not in self.data.keys()
            ):
                continue

            town_name = reservoir_data["id_to_town_name"][id_][:2]
            reservoir_name = reservoir_data["id_to_name"][id_]
            self.data[town_name][reservoir_name] = {
                "total_capacity": to_float(datum["EffectiveCapacity"]),
                "inflow": to_float(datum["InflowVolume"]),
                "outflow": to_float(datum["OutflowTotal"]),
                "updated_time": self.format_time(datum["RecordTime"]),
            }

    def update_reservoir_details(self):
        detail_data = self.get_info("details")
        for datum in detail_data:
            id_ = datum["ReservoirIdentifier"]
            if (id_ not in reservoir_data["id_to_name"]) or (
                reservoir_data["id_to_town_name"][id_][:2] not in self.data.keys()
            ):
                continue

            town_name = reservoir_data["id_to_town_name"][id_][:2]
            reservoir_name = reservoir_data["id_to_name"][id_]
            if reservoir_name not in self.data[town_name]:
                continue

            observed_time = self.format_time(datum["ObservationTime"])
            if (
                "updated_time" not in self.data[town_name][reservoir_name]
                or self.data[town_name][reservoir_name]["updated_time"] < observed_time
            ):
                self.data[town_name][reservoir_name]["updated_time"] = observed_time
                self.data[town_name][reservoir_name]["current_capacity"] = to_float(
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
            self.logging.error(f"Error: {str(e)} when fetching electricity data")
            self.data = {
                "updated_time": "N/A",
                "north_gen": 0,
                "north_use": 0,
                "central_gen": 0,
                "central_use": 0,
                "south_gen": 0,
                "south_use": 0,
                "east_gen": 0,
                "east_use": 0,
            }
            return

        if self.is_outdated(data.iloc[0, 0]):
            self.data = {
                "updated_time": self.update_time,
                "north_gen": data.iloc[0, 1],
                "north_use": data.iloc[0, 2],
                "central_gen": data.iloc[0, 3],
                "central_use": data.iloc[0, 4],
                "south_gen": data.iloc[0, 5],
                "south_use": data.iloc[0, 6],
                "east_gen": data.iloc[0, 7],
                "east_use": data.iloc[0, 8],
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
        if self.database is not None:
            self.database.insert_one({"time": self.update_time, "data": self.data})


class EarthquakeManager(Base):
    def __init__(self, database=None):
        self.large_url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/E-A0015-001"
        self.small_url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/E-A0016-001"
        self.auth = os.environ.get("CWB_AUTH")
        self.data = {
            "桃園": [],
            "新竹": [],
            "臺中": [],
            "臺南": [],
        }
        self.update_time = datetime.now()
        super().__init__(time_pattern="%Y-%m-%d %H:%M:%S", database=database)

    def reset(self):
        self.data = {
            "桃園": [],
            "新竹": [],
            "臺中": [],
            "臺南": [],
        }

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
            
            magnitude = earthquake_info["EarthquakeMagnitude"]["MagnitudeValue"]
            """
            center = earthquake_info["Epicenter"]["Location"]
            shaking_areas = earthquake["Intensity"]["ShakingArea"]
            for area in shaking_areas:
                area_names = area["CountyName"].split("、")
                if len(area["EqStation"]) == 0:
                    continue
                for area_name in area_names:
                    if area_name[:2] not in self.data.keys():
                        continue

                    observe_intensity = area["AreaIntensity"]

                    self.data[area_name[:2]].append(
                        {
                            "source": center[:3],
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
            self.logging.error(
                f"Error: {data.status_code} code when fetching earthquake data"
            )
            return {}

    def sort_earthquake_by_time(self):
        for key in self.data.keys():
            self.data[key].sort(key=lambda x: x["time"], reverse=True)

    def update_func(self):
        self.reset()
        self.process_data(self.get_info("l"), "l")
        self.process_data(self.get_info("s"), "s")
        self.sort_earthquake_by_time()

    def update_database(self):
        # Insert data by Flask_mongo
        pass
        # self.database.insert_one({"time": self.update_time, "data": self.data})
