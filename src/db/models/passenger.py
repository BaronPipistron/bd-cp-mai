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


class Passenger(BaseTable):
    passenger_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey(
            'users.user_id',
            ondelete='CASCADE'
        ),
        nullable=False
    )
    birth_date = Column(DATE, nullable=False)
    sex = Column(String, nullable=False)