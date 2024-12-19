from src.db.database import BaseTable

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from sqlalchemy import (
    DATE,
    TIMESTAMP,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Boolean,
    MetaData,
    PrimaryKeyConstraint,
    String,
    Table,
    text,
    DateTime, Float
)


class Ride(BaseTable):
    ride_id = Column(Integer, primary_key=True, autoincrement=True)
    driver_id = Column(
        Integer,
        ForeignKey('drivers.driver_id'),
        nullable=False
    )
    passenger_id = Column(
        Integer,
        ForeignKey('passengers.passenger_id'),
        nullable=False
    )
    car_id = Column(
        Integer,
        ForeignKey('cars.car_id'),
        nullable=False
    )
    rate = Column(Float, nullable=False, default=5.0)
