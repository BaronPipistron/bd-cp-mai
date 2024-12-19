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


class Car(BaseTable):
    car_id = Column(Integer, primary_key=True, autoincrement=True)
    car_number = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)

