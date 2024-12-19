import re

from datetime import datetime, date
from typing import (
    Optional,
    List,
    Dict
)

from pydantic import (
    BaseModel,
    ValidationError,
    EmailStr,
    Field,
    field_validator
)


class RestoreRequest(BaseModel):
    backup_file: str


class CreateBackupRequest(BaseModel):
    backup_file: str


class SUserGet(BaseModel):
    user_id: int
    firstname: str
    lastname: str
    email: EmailStr
    role: str


class SAdminGet(BaseModel):
    user_id: int
    firstname: str
    lastname: str
    email: EmailStr
    phone_number: str

class SDriverGet(BaseModel):
    driver_id: int
    firstname: str
    lastname: str
    email: EmailStr
    phone_number: str
    birth_date: date
    sex: str
    driver_rides: int
    driver_time_accidents: int
    driver_license_number: str


class SPassengerGet(BaseModel):
    passenger_id: int
    firstname: str
    lastname: str
    email: EmailStr
    phone_number: str
    birth_date: date
    sex: str


class SAnalystGet(BaseModel):
    analyst_id: int
    firstname: str
    lastname: str
    email: EmailStr
    phone_number: str
    grade: str


class SCarGet(BaseModel):
    car_id: int
    car_number: str
    status: str
    color: str
    model: str
    car_class: str
    year: int


class SRideGet(BaseModel):
    ride_id: int
    driver_id: int
    passenger_id: int
    car_id: int
    rate: float
    ride_date: datetime
    ride_duration_seconds: int
    ride_cost_rubles: int
    distance: int


class SUserAdd(BaseModel):
    firstname: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description='Email address')
    password_hash: str = Field(..., min_length=8, description='Password from 8 symbols')
    phone_number: str = Field(..., max_length=12, description='Phone number')
    role: str


    @classmethod
    @field_validator('firstname')
    def validate_firstname(cls, firstname: str):
        if not firstname.isalpha():
            raise ValueError('Firstname should only contain letters')

        return firstname


    @classmethod
    @field_validator('lastname')
    def validate_lastname(cls, lastname: str):
        if not lastname.isalpha():
            raise ValueError('Lastname should only contain letters')

        return lastname


    @classmethod
    @field_validator('email')
    def validate_email(cls, email: str):
        valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

        if email and not valid:
            raise ValueError('Email address is not valid')

        return email


class SDriverAdd(BaseModel):
    birth_date: None | date = Field(..., description='Date of birth')
    sex: None| str = Field(..., min_length=1, max_length=1, description='M or F')
    driver_rides: int
    driver_time_accidents: int
    driver_license_number: str


class SPassengerAdd(BaseModel):
    birth_date: None | date = Field(..., description='Date of birth')
    sex: None | str = Field(..., min_length=1, max_length=1, description='M or F')


class SAnalystAdd(BaseModel):
    grade: str


class SCarAdd(BaseModel):
    car_number: str
    status: str | None = None
    color: str
    model: str
    car_class: str
    year: int


class SRideAdd(BaseModel):
    driver_id: int
    passenger_id: int
    car_id: int
    rate: float | None = None
    ride_date: datetime
    ride_duration_seconds: int
    ride_cost_rubles: int
    distance: int


class SDriverRegistration(BaseModel):
    user_data: SUserAdd
    driver_data: SDriverAdd


class SPassengerRegistration(BaseModel):
    user_data: SUserAdd
    passenger_data: SPassengerAdd


class SAnalystRegistration(BaseModel):
    user_data: SUserAdd
    analyst_data: SAnalystAdd


class SUserAuth(BaseModel):
    email: EmailStr = Field(..., description='Email address')
    password: str = Field(..., min_length=8, description='Password from 8 symbols')


class SUserUpdate(BaseModel):
    firstname: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description='Email address')
    phone_number: str = Field(..., max_length=12, description='Phone number')


class DriverUpdate(BaseModel):
    birth_date: date = Field(..., description='Date of birth')
    driver_rides: int
    driver_time_accidents: int
    driver_license_number: str


class SDriverUpdate(BaseModel):
    user_data: SUserUpdate
    driver_data: DriverUpdate


class PassengerUpdate(BaseModel):
    birth_date: date = Field(..., description='Date of birth')


class SPassengerUpdate(BaseModel):
    user_data: SUserUpdate
    passenger_data: PassengerUpdate


class AnalystUpdate(BaseModel):
    grade: str


class SAnalystUpdate(BaseModel):
    user_data: SUserUpdate
    analyst_data: AnalystUpdate


class SCarUpdate(BaseModel):
    car_number: str
    status: str
    color: str
    car_class: str


class SQLQuery(BaseModel):
    query: str
