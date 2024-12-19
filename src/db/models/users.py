from src.db.database import BaseTable

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from sqlalchemy import (
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


class User(BaseTable):
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=False)

