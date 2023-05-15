from apps.app import db


class Reservoir(db.Model):
    __tablename__ = "reservoir"
    _id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String, index=True, nullable=False)
    inflow = db.Column(db.Float, nullable=False)
    outflow = db.Column(db.Float, nullable=False)
    total_capacity = db.Column(db.Float, nullable=False)
    current_capacity = db.Column(db.Float, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    updated_time = db.Column(db.DateTime, index=False, nullable=False)

    def __init__(
        self, area, in_flow, out_flow, total_capacity, current_capacity, percentage, updated_time
    ):
        self.area = area
        self.in_flow = in_flow
        self.out_flow = out_flow
        self.total_capacity = total_capacity
        self.current_capacity = current_capacity
        self.percentage = percentage
        self.updated_time = updated_time


class Electricity(db.Model):
    __tablename__ = "electricity"
    _id = db.Column(db.Integer, primary_key=True)
    north_generate = db.Column(db.Float, nullable=False)
    north_usage = db.Column(db.Float, nullable=False)
    central_generate = db.Column(db.Float, nullable=False)
    central_usage = db.Column(db.Float, nullable=False)
    south_generate = db.Column(db.Float, nullable=False)
    south_usage = db.Column(db.Float, nullable=False)
    updated_time = db.Column(db.DateTime, index=False, nullable=False)

    def __init__(
        self,
        north_generate,
        north_usage,
        central_generate,
        central_usage,
        south_generate,
        south_usage,
        updated_time,
    ):
        self.north_generate = north_generate
        self.north_usage = north_usage
        self.central_generate = central_generate
        self.central_usage = central_usage
        self.south_generate = south_generate
        self.south_usage = south_usage
        self.updated_time = updated_time


class Earthquake(db.Model):
    __tablename__ = "earthquake"
    _id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String, index=True, nullable=False)
    source = db.Column(db.String, nullable=False)
    number = db.Column(db.Integer, index=True, nullable=False)
    observed_intensity = db.Column(db.String, nullable=False)
    pga = db.Column(db.Float, nullable=False)
    pgv = db.Column(db.Float, nullable=False)
    observed_time = db.Column(db.DateTime, index=True, nullable=False)

    def __init__(self, area, source, number, observed_intensity, pga, pgv, observed_time):
        self.area = area
        self.source = source
        self.number = number
        self.observed_intensity = observed_intensity
        self.pga = pga
        self.pgv = pgv
        self.observed_time = observed_time
