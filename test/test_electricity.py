from api import ElectricityManager


def test_electricity_fail():
    electricity_manager = ElectricityManager()
    electricity_manager.gen_use_url = "nowhere"

    electricity_manager.update_func()
    assert isinstance(electricity_manager.data, dict)
    assert electricity_manager.data["updated_time"] == "N/A"
    assert electricity_manager.data["north"] == (0, 0)
    assert electricity_manager.data["central"] == (0, 0)
    assert electricity_manager.data["south"] == (0, 0)
    assert electricity_manager.data["east"] == (0, 0)


def test_electricity_outdated():
    electricity_manager = ElectricityManager()
    assert electricity_manager.is_outdated("2100-01-01 00:00")
    assert electricity_manager.update_time == electricity_manager.format_time(
        "2100-01-01 00:00"
    )
    assert not electricity_manager.is_outdated("2001-01-01 00:00")


def test_electricity_normal():
    electricity_manager = ElectricityManager()

    if electricity_manager.data["updated_time"] != "N/A":
        import datetime

        assert isinstance(electricity_manager.data, dict)
        assert isinstance(electricity_manager.data["updated_time"], datetime.datetime)
        assert isinstance(electricity_manager.data["north"], tuple)
        assert isinstance(electricity_manager.data["central"], tuple)
        assert isinstance(electricity_manager.data["south"], tuple)
        assert isinstance(electricity_manager.data["east"], tuple)
