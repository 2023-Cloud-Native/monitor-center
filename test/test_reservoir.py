from api import ReservoirManager


def test_reservoir_fail():
    reservoir_manager = ReservoirManager()
    reservoir_manager.reservoir_overall_url = "nowhere"
    reservoir_manager.reservoir_detail_url = "nowhere"

    overall_data = reservoir_manager.get_info("overall")
    assert overall_data == []

    detail_data = reservoir_manager.get_info("details")
    assert detail_data == []


def test_reservoir_normal():
    reservoir_manager = ReservoirManager()
    assert isinstance(reservoir_manager.data, dict)
