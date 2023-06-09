from api import EarthquakeManager
import dotenv

dotenv.load_dotenv()


def test_earthquake_fail():
    earthquake_manager = EarthquakeManager()
    earthquake_manager.auth = "nowhere"
    earthquake_manager.data = {}
    earthquake_manager.get_info()
    assert earthquake_manager.data == {}


def test_earthquake_time():
    earthquake_manager = EarthquakeManager()
    earthquake_manager.updated_time = earthquake_manager.format_time(
        "2100-01-31 00:00:00"
    )
    assert earthquake_manager.get_thirty_day_str() == "2100-01-01T00:00:00"


def test_earthquake_normal():
    import datetime

    earthquake_manager = EarthquakeManager()
    assert isinstance(earthquake_manager.data, dict)
    assert "新竹" in earthquake_manager.data
    assert "臺中" in earthquake_manager.data
    assert "臺南" in earthquake_manager.data

    # Check sort time
    for key in earthquake_manager.data:
        for data in earthquake_manager.data[key]:
            assert isinstance(data["source"], str)
            assert isinstance(data["observed_time"], datetime.datetime)
            assert isinstance(data["pga"], float) and data["pga"] >= 0
            assert isinstance(data["pgv"], float) and data["pgv"] >= 0

        for cur_time, prev_time in zip(
            earthquake_manager.data[key][:-1], earthquake_manager.data[key][1:]
        ):
            assert cur_time["observed_time"] >= prev_time["observed_time"]
