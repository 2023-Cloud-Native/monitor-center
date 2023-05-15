import os
from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import dotenv

dotenv.load_dotenv()

Base = declarative_base()


class Reservoir(Base):
    __tablename__ = "reservoir"
    _id = Column(Integer, primary_key=True)
    area = Column(String, index=True, nullable=False)
    in_flow = Column(Float, nullable=False)
    out_flow = Column(Float, nullable=False)
    total_capacity = Column(Float, nullable=False)
    current_capacity = Column(Float, nullable=False)
    update_time = Column(DateTime, index=False, nullable=False)

    def __init__(
        self, area, in_flow, out_flow, total_capacity, current_capacity, update_time
    ):
        self.area = area
        self.in_flow = in_flow
        self.out_flow = out_flow
        self.total_capacity = total_capacity
        self.current_capacity = current_capacity
        self.update_time = update_time


class Electricity(Base):
    __tablename__ = "electricity"
    _id = Column(Integer, primary_key=True)
    north_generate = Column(Float, nullable=False)
    north_usage = Column(Float, nullable=False)
    central_generate = Column(Float, nullable=False)
    central_usage = Column(Float, nullable=False)
    south_generate = Column(Float, nullable=False)
    south_usage = Column(Float, nullable=False)
    update_time = Column(DateTime, index=False, nullable=False)

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


class Earthquake(Base):
    __tablename__ = "earthquake"
    _id = Column(Integer, primary_key=True)
    area = Column(String, index=True, nullable=False)
    source = Column(String, nullable=False)
    observe_intensity = Column(Float, nullable=False)
    pga = Column(Float, nullable=False)
    pgv = Column(Float, nullable=False)
    observe_time = Column(DateTime, index=True, nullable=False)

    def __init__(self, area, source, observe_intensity, pga, pgv, observe_time):
        self.area = area
        self.source = source
        self.observe_intensity = observe_intensity
        self.pga = pga
        self.pgv = pgv
        self.observe_time = observe_time


engine = create_engine(os.getenv("DATABASE_URL"))
DBSession = sessionmaker(bind=engine)
