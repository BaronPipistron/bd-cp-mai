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


class CarInfo(BaseTable):
    car_id = Column(
        Integer,
        ForeignKey(
            'cars.car_id',
            ondelete='CASCADE'
        ),
        primary_key=True
    )
    color = Column(String, nullable=False)
    model = Column(String, nullable=False)
    car_class = Column(String, nullable=False)
    year = Column(Integer, nullable=False)

