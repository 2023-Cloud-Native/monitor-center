import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy import desc
from api.models import Reservoir, Electricity, Earthquake
from api.database import session_maker_readonly


def process_time(start_time, end_time):
    start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d")
    end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d")

    if end_time < start_time:
        start_time, end_time = end_time, start_time

    end_time = end_time.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start_time, end_time


def process_reservoir():
    areas = ["新竹", "臺中", "臺南"]
    data = {}

    with session_maker_readonly() as db:
        for area in areas:
            reservoir_data = (
                db.query(Reservoir)
                .filter_by(area=area)
                .order_by(desc(Reservoir.updated_time))
                .first()
            )
            if reservoir_data is None:
                data[area] = {}
            else:
                data[area] = {
                    "inflow": reservoir_data.inflow,
                    "outflow": reservoir_data.outflow,
                    "total_capacity": reservoir_data.total_capacity,
                    "current_capacity": reservoir_data.current_capacity,
                    "percentage": reservoir_data.percentage,
                    "updated_time": reservoir_data.updated_time.strftime(
                        r"%Y-%m-%d %H:%M:%S"
                    ),
                }

    return data


def process_electricity():
    with session_maker_readonly() as db:
        electricity_data = (
            db.query(Electricity).order_by(desc(Electricity.updated_time)).first()
        )
        if electricity_data is None:
            return {}
        else:
            return {
                "north_generate": electricity_data.north_generate,
                "north_usage": electricity_data.north_usage,
                "central_generate": electricity_data.central_generate,
                "central_usage": electricity_data.central_usage,
                "south_generate": electricity_data.south_generate,
                "south_usage": electricity_data.south_usage,
                "updated_time": electricity_data.updated_time.strftime(
                    r"%Y-%m-%d %H:%M:%S"
                ),
            }


def process_earthquake():
    data = {"新竹": [], "臺中": [], "臺南": []}
    current_time = datetime.datetime.now()

    with session_maker_readonly() as db:
        earthquakes = (
            db.query(Earthquake).order_by(desc(Earthquake.observed_time)).all()
        )
        for earthquake in earthquakes:
            data_time = earthquake.observed_time
            if current_time - data_time > datetime.timedelta(days=30):
                break
            data[earthquake.area].append(
                {
                    "source": earthquake.source,
                    "earthquake_no": earthquake.number,
                    "pga": earthquake.pga,
                    "pgv": earthquake.pgv,
                    "observed_time": data_time.strftime(r"%Y-%m-%d %H:%M:%S"),
                }
            )
        return data


def get_reservoir_with_time_range(start_time, end_time):
    areas = ["新竹", "臺中", "臺南"]
    data = {}

    with session_maker_readonly() as db:
        reservoir_range_data = db.query(Reservoir).filter(
            Reservoir.updated_time.between(start_time, end_time)
        )

        for area in areas:
            reservoir_range_data_within_area = reservoir_range_data.filter_by(
                area=area
            ).all()
            data[area] = []
            for reservoir_data in reservoir_range_data_within_area:
                data[area].append(
                    {
                        "inflow": reservoir_data.inflow,
                        "outflow": reservoir_data.outflow,
                        "total_capacity": reservoir_data.total_capacity,
                        "current_capacity": reservoir_data.current_capacity,
                        "percentage": reservoir_data.percentage,
                        "updated_time": reservoir_data.updated_time.strftime(
                            r"%Y-%m-%d %H:%M:%S"
                        ),
                    }
                )
    return data


def get_electricity_with_time_range(start_time, end_time):
    data = []

    with session_maker_readonly() as db:
        electricity_range_data = db.query(Electricity).filter(
            Electricity.updated_time.between(start_time, end_time)
        )

        for electricity_data in electricity_range_data:
            data.append(
                {
                    "north_generate": electricity_data.north_generate,
                    "north_usage": electricity_data.north_usage,
                    "central_generate": electricity_data.central_generate,
                    "central_usage": electricity_data.central_usage,
                    "south_generate": electricity_data.south_generate,
                    "south_usage": electricity_data.south_usage,
                    "updated_time": electricity_data.updated_time.strftime(
                        r"%Y-%m-%d %H:%M:%S"
                    ),
                }
            )

    return data


def get_earthquake_with_time_range(start_time, end_time):
    data = {"新竹": [], "臺中": [], "臺南": []}
    with session_maker_readonly() as db:
        earthquake_range_data = db.query(Earthquake).filter(
            Earthquake.observed_time.between(start_time, end_time)
        )
        for earthquake in earthquake_range_data:
            data[earthquake.area].append(
                {
                    "source": earthquake.source,
                    "earthquake_no": earthquake.number,
                    "pga": earthquake.pga,
                    "pgv": earthquake.pgv,
                    "observed_time": earthquake.observed_time.strftime(
                        r"%Y-%m-%d %H:%M:%S"
                    ),
                }
            )
    return data


api = Blueprint("api", __name__)
resources = {
    "Reservoir": process_reservoir,
    "Electricity": process_electricity,
    "Earthquake": process_earthquake,
}


@api.route("/reservoir")
def reservoir():
    start_time, end_time = process_time(
        request.args.get("start"), request.args.get("end")
    )
    return jsonify(get_reservoir_with_time_range(start_time, end_time))


@api.route("/electricity")
def electricity():
    start_time, end_time = process_time(
        request.args.get("start"), request.args.get("end")
    )
    return jsonify(get_electricity_with_time_range(start_time, end_time))


@api.route("/earthquake")
def earthquake():
    start_time, end_time = process_time(
        request.args.get("start"), request.args.get("end")
    )
    return jsonify(get_earthquake_with_time_range(start_time, end_time))


@api.route("/")
def index():
    all_data = {
        resource_name: resource_func()
        for resource_name, resource_func in resources.items()
    }
    return jsonify(all_data)
