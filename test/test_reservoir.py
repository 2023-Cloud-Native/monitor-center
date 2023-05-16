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
    import datetime

    reservoir_manager = ReservoirManager()
    assert isinstance(reservoir_manager.data, dict)
    for area in reservoir_manager.data:
        if reservoir_manager.data[area]["updated_time"] == "N/A":
            continue

        assert isinstance(
            reservoir_manager.data[area]["updated_time"], datetime.datetime
        )
        assert (
            isinstance(reservoir_manager.data[area]["inflow"], float)
            and reservoir_manager.data[area]["inflow"] >= 0
        )
        assert (
            isinstance(reservoir_manager.data[area]["outflow"], float)
            and reservoir_manager.data[area]["outflow"] >= 0
        )
        assert (
            isinstance(reservoir_manager.data[area]["percentage"], float)
            and reservoir_manager.data[area]["percentage"] >= 0
            and reservoir_manager.data[area]["percentage"] <= 100
        )
        assert (
            isinstance(reservoir_manager.data[area]["total_capacity"], float)
            and reservoir_manager.data[area]["total_capacity"] >= 0
        )
        assert (
            isinstance(reservoir_manager.data[area]["current_capacity"], float)
            and reservoir_manager.data[area]["current_capacity"] >= 0
        )
        assert (
            abs(
                reservoir_manager.data[area]["percentage"]
                - (
                    reservoir_manager.data[area]["current_capacity"]
                    / reservoir_manager.data[area]["total_capacity"]
                )
            )
            < 1e-5
        )
