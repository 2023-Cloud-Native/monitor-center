import datetime
from flask import Blueprint, jsonify
from sqlalchemy import desc
from apps.app import db
from api.models import Reservoir, Electricity, Earthquake


def process_reservoir():
    areas = ["新竹", "臺中", "臺南"]
    data = {}

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
    earthquakes = db.query(Earthquake).order_by(desc(Earthquake.observed_time)).all()
    data = {"新竹": [], "臺中": [], "臺南": []}
    current_time = datetime.datetime.now()
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


api = Blueprint("api", __name__)
resources = {
    "Reservoir": process_reservoir,
    "Electricity": process_electricity,
    "Earthquake": process_earthquake,
}


@api.route("/")
def index():
    all_data = {
        resource_name: resource_func()
        for resource_name, resource_func in resources.items()
    }
    return jsonify(all_data)
