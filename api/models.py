from pathlib import Path
import sys
from sqlalchemy import Column, Integer, String, Float, DateTime

sys.path.append(Path(__file__).resolve().parent.parent.__str__())
from api.database import Base


class Reservoir(Base):
    __tablename__ = "reservoir"
    _id = Column(Integer, primary_key=True)
    area = Column(String(30), index=True, nullable=False)
    inflow = Column(Float, nullable=False)
    outflow = Column(Float, nullable=False)
    total_capacity = Column(Float, nullable=False)
    current_capacity = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    updated_time = Column(DateTime, index=True, nullable=False)

    def __init__(
        self,
        area,
        inflow,
        outflow,
        total_capacity,
        current_capacity,
        percentage,
        updated_time,
    ):
        self.area = area
        self.inflow = inflow
        self.outflow = outflow
        self.total_capacity = total_capacity
        self.current_capacity = current_capacity
        self.percentage = percentage
        self.updated_time = updated_time


class Electricity(Base):
    __tablename__ = "electricity"
    _id = Column(Integer, primary_key=True)
    north_generate = Column(Float, nullable=False)
    north_usage = Column(Float, nullable=False)
    central_generate = Column(Float, nullable=False)
    central_usage = Column(Float, nullable=False)
    south_generate = Column(Float, nullable=False)
    south_usage = Column(Float, nullable=False)
    updated_time = Column(DateTime, index=True, nullable=False)

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


class Earthquake(Base):
    __tablename__ = "earthquake"
    _id = Column(Integer, primary_key=True)
    area = Column(String(20), index=True, nullable=False)
    source = Column(String(20), nullable=False)
    pga = Column(Float, nullable=False)
    pgv = Column(Float, nullable=False)
    observed_time = Column(DateTime, index=True, nullable=False)

    def __init__(self, area, source, pga, pgv, observed_time):
        self.area = area
        self.source = source
        self.pga = pga
        self.pgv = pgv
        self.observed_time = observed_time
