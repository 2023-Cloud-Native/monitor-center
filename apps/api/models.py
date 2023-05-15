from apps.app import db


class Reservoir(db.Model):
    __tablename__ = "reservoir"
    _id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String, index=True, nullable=False)
    in_flow = db.Column(db.Float, nullable=False)
    out_flow = db.Column(db.Float, nullable=False)
    total_capacity = db.Column(db.Float, nullable=False)
    current_capacity = db.Column(db.Float, nullable=False)
    update_time = db.Column(db.DateTime, index=False, nullable=False)

    def __init__(
        self, area, in_flow, out_flow, total_capacity, current_capacity, update_time
    ):
        self.area = area
        self.in_flow = in_flow
        self.out_flow = out_flow
        self.total_capacity = total_capacity
        self.current_capacity = current_capacity
        self.update_time = update_time


class Electricity(db.Model):
    __tablename__ = "electricity"
    _id = db.Column(db.Integer, primary_key=True)
    north_generate = db.Column(db.Float, nullable=False)
    north_usage = db.Column(db.Float, nullable=False)
    central_generate = db.Column(db.Float, nullable=False)
    central_usage = db.Column(db.Float, nullable=False)
    south_generate = db.Column(db.Float, nullable=False)
    south_usage = db.Column(db.Float, nullable=False)
    update_time = db.Column(db.DateTime, index=False, nullable=False)

    def __init__(
        self,
        north_generate,
        north_usage,
        central_generate,
        central_usage,
        south_generate,
        south_usage,
        update_time,
    ):
        self.north_generate = north_generate
        self.north_usage = north_usage
        self.central_generate = central_generate
        self.central_usage = central_usage
        self.south_generate = south_generate
        self.south_usage = south_usage
        self.update_time = update_time


class Earthquake(db.Model):
    __tablename__ = "earthquake"
    _id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String, index=True, nullable=False)
    source = db.Column(db.String, nullable=False)
    observe_intensity = db.Column(db.Float, nullable=False)
    pga = db.Column(db.Float, nullable=False)
    pgv = db.Column(db.Float, nullable=False)
    observe_time = db.Column(db.DateTime, index=True, nullable=False)

    def __init__(self, area, source, observe_intensity, pga, pgv, observe_time):
        self.area = area
        self.source = source
        self.observe_intensity = observe_intensity
        self.pga = pga
        self.pgv = pgv
        self.observe_time = observe_time
