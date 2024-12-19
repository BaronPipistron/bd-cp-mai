from sqlalchemy import text, insert, select, update, delete
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr, Field
import asyncio
from fastapi import HTTPException, Response
from src.quieres.core import *
from src.db.database import async_session

from app.schemas import *


class TaskRepository:
    @classmethod
    async def add_admin(cls, data: SUserAdd):
        user_data_dict = data.model_dump()

        try:
            admin_id = await add_admin(user_data_dict)

            return admin_id
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error))


    @classmethod
    async def make_driver_registration(cls, data: SDriverRegistration):
        user_data_dict = data.user_data.model_dump()
        driver_data_dict = data.driver_data.model_dump()

        try:
            driver_id = await register_driver(user_data_dict, driver_data_dict)

            return driver_id
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error))


    @classmethod
    async def make_passenger_registration(cls, data: SPassengerRegistration):
        user_data_dict = data.user_data.model_dump()
        passenger_data_dict = data.passenger_data.model_dump()

        try:
            passenger_id = await register_passenger(user_data_dict, passenger_data_dict)

            return passenger_id
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error))


    @classmethod
    async def make_analyst_registration(cls, data: SAnalystRegistration):
        user_data_dict = data.user_data.model_dump()
        analyst_data_dict = data.analyst_data.model_dump()

        try:
            analyst_id = await register_analyst(user_data_dict, analyst_data_dict)

            return analyst_id
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error))


    @classmethod
    async def add_new_car(cls, data: SCarAdd):
        car_data_dict = data.model_dump()

        try:
            car_id = await add_car(car_data_dict)

            return car_id
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error))


    @classmethod
    async def add_new_ride(cls, data: SRideAdd):
        ride_data_dict = data.model_dump()

        try:
            ride_id = await add_ride(ride_data_dict)

            return ride_id
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error))


    @classmethod
    async def get_all_drivers(cls):
        drivers = await get_all_drivers()

        return drivers


    @classmethod
    async def get_all_passengers(cls):
        passengers = await get_all_passengers()

        return passengers


    @classmethod
    async def get_all_analysts(cls):
        analysts = await get_all_analysts()

        return analysts


    @classmethod
    async def get_all_cars(cls):
        cars = await get_all_cars()

        return cars


    @classmethod
    async def get_all_rides(cls):
        rides = await get_all_rides()

        return rides

