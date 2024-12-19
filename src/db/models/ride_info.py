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
    DateTime
)

from datetime import datetime


class RideInfo(BaseTable):
    ride_id = Column(
        Integer,
        ForeignKey(
            'rides.ride_id',
            ondelete='CASCADE'
        ),
        primary_key=True
    )
    ride_date = Column(DateTime, nullable=False, default=datetime.now())
    ride_duration_seconds = Column(Integer, nullable=False)
    ride_cost_rubles = Column(Integer, nullable=False)
    distance = Column(Integer, nullable=False)

