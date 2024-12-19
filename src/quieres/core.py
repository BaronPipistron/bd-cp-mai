from datetime import datetime
from src.db.database import async_session

from sqlalchemy import (
    text,
    insert,
    select,
    update,
    delete
)

from src.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    authenticate_user
)


async def get_all_drivers():
    async with async_session() as session:
        query = text(
            '''
            SELECT 
                driver_id,
                firstname,
                lastname,
                email,
                phone_number,
                birth_date,
                sex,
                driver_rides,
                driver_time_accidents,
                driver_license_number
            FROM 
                users INNER JOIN drivers ON users.user_id = drivers.user_id
            '''
        )
        results = await session.execute(query)
        drivers = [dict(row) for row in results.mappings()]

        return drivers


async def get_all_passengers():
    async with async_session() as session:
        query = text(
            '''
            SELECT 
                passenger_id,
                firstname,
                lastname,
                email,
                phone_number,
                birth_date,
                sex
            FROM 
                users INNER JOIN passengers ON users.user_id = passengers.user_id
            '''
        )
        results = await session.execute(query)
        passengers = [dict(row) for row in results.mappings()]

        return passengers


async def get_all_analysts():
    async with async_session() as session:
        query = text(
            '''
            SELECT
                analyst_id,
                firstname,
                lastname,
                email,
                phone_number,
                grade
            FROM 
                users INNER JOIN analysts ON users.user_id = analysts.user_id
            '''
        )
        results = await session.execute(query)
        analysts = [dict(row) for row in results.mappings()]

        return analysts


async def get_all_cars():
    async with async_session() as session:
        query = text(
            '''
            SELECT 
                cars.car_id,
                car_number,
                status,
                color,
                model,
                car_class,
                year
            FROM 
                cars INNER JOIN car_info ON cars.car_id = car_info.car_id
            '''
        )
        results = await session.execute(query)
        cars = [dict(row) for row in results.mappings()]

        return cars


async def get_all_rides():
    async with async_session() as session:
        query = text(
            '''
            SELECT
                rides.ride_id,
                driver_id,
                passenger_id,
                car_id,
                rate,
                ride_date,
                ride_duration_seconds,
                ride_cost_rubles,
                distance
            FROM rides INNER JOIN ride_info ON rides.ride_id = ride_info.ride_id
            '''
        )
        results = await session.execute(query)
        rides = [dict(row) for row in results.mappings()]

        return rides


async def add_admin(user_data):
    async with async_session() as session:
        async with session.begin():
            try:
                query = text(
                    '''
                    SELECT user_id
                    FROM users
                    WHERE email = :email
                    '''
                )
                result = await session.execute(query, {'email': user_data['email']})
                existing_user = result.scalar()

                if existing_user:
                    raise ValueError('Email already registered')

                user_data['password_hash'] = get_password_hash(user_data['password_hash'])

                user_data['role'] = 'admin'

                add_admin_query = text(
                    '''
                    INSERT INTO users (firstname, lastname, email, password_hash, phone_number, role)
                    VALUES (:firstname, :lastname, :email, :password_hash, :phone_number, :role)
                    RETURNING user_id
                    '''
                )

                result = await session.execute(
                    add_admin_query,
                    {
                        'firstname': user_data['firstname'],
                        'lastname': user_data['lastname'],
                        'email': user_data['email'],
                        'password_hash': user_data['password_hash'],
                        'phone_number': user_data['phone_number'],
                        'role': user_data['role']
                    }
                )

                admin_id = result.scalar()

                await session.commit()
                print("Admin successfully added")

                return admin_id
            except Exception as error:
                print(f'Error while added admin: {error}')

                raise error


async def register_driver(user_data, driver_data):
    async with async_session() as session:
        async with session.begin():
            try:
                query = text(
                    '''
                    SELECT user_id
                    FROM users
                    WHERE email = :email
                    '''
                )
                result = await session.execute(query, {'email': user_data['email']})
                existing_user = result.scalar()

                if existing_user:
                    raise ValueError('Email already registered')

                user_data['password_hash'] = get_password_hash(user_data['password_hash'])

                table_users_insert_query = text(
                    '''
                    INSERT INTO users (firstname, lastname, email, password_hash, phone_number, role)
                    VALUES (:firstname, :lastname, :email, :password_hash, :phone_number, :role)
                    RETURNING user_id
                    '''
                )
                result = await session.execute(
                    table_users_insert_query,
                    {
                        'firstname': user_data['firstname'],
                        'lastname': user_data['lastname'],
                        'email': user_data['email'],
                        'password_hash': user_data['password_hash'],
                        'phone_number': user_data['phone_number'],
                        'role': user_data['role']
                    }
                )
                user_id = result.scalar()

                table_drivers_insert_query = text(
                    '''
                    INSERT INTO drivers (user_id, birth_date, sex, driver_rides, driver_time_accidents, driver_license_number)
                    VALUES (:user_id, :birth_date, :sex, :driver_rides, :driver_time_accidents, :driver_license_number)
                    RETURNING driver_id
                    '''
                )
                result = await session.execute(
                    table_drivers_insert_query,
                    {
                        'user_id': user_id,
                        'birth_date': driver_data['birth_date'],
                        'sex': driver_data['sex'],
                        'driver_rides': driver_data['driver_rides'],
                        'driver_time_accidents': driver_data['driver_time_accidents'],
                        'driver_license_number': driver_data['driver_license_number']
                    }
                )
                driver_id = result.scalar()

                await session.commit()
                print("Driver successfully registered")

                return driver_id

            except Exception as error:
                print(f'Error while registering driver: {error}')

                raise error


async def register_passenger(user_data, passenger_data):
    async with async_session() as session:
        async with session.begin():
            try:
                query = text(
                    '''
                    SELECT user_id
                    FROM users
                    WHERE email = :email
                    '''
                )
                result = await session.execute(query, {'email': user_data['email']})
                existing_user = result.scalar()

                if existing_user:
                    raise ValueError('Email already registered')

                user_data['password_hash'] = get_password_hash(user_data['password_hash'])

                table_users_insert_query = text(
                    '''
                    INSERT INTO users (firstname, lastname, email, password_hash, phone_number, role)
                    VALUES (:firstname, :lastname, :email, :password_hash, :phone_number, :role)
                    RETURNING user_id
                    '''
                )
                result = await session.execute(
                    table_users_insert_query,
                    {
                        'firstname': user_data['firstname'],
                        'lastname': user_data['lastname'],
                        'email': user_data['email'],
                        'password_hash': user_data['password_hash'],
                        'phone_number': user_data['phone_number'],
                        'role': user_data['role']
                    }
                )
                user_id = result.scalar()

                table_passengers_insert_query = text(
                    '''
                    INSERT INTO passengers (user_id, birth_date, sex)
                    VALUES (:user_id, :birth_date, :sex)
                    RETURNING passenger_id
                    '''
                )
                result = await session.execute(
                    table_passengers_insert_query,
                    {
                        'user_id': user_id,
                        'birth_date': passenger_data['birth_date'],
                        'sex': passenger_data['sex'],
                    }
                )
                passenger_id = result.scalar()

                await session.commit()
                print("Passenger successfully registered")

                return passenger_id

            except Exception as error:
                print(f'Error while registering passenger: {error}')

                raise error


async def register_analyst(user_data, analyst_data):
    async with async_session() as session:
        async with session.begin():
            try:
                query = text(
                    '''
                    SELECT user_id
                    FROM users
                    WHERE email = :email
                    '''
                )
                result = await session.execute(query, {'email': user_data['email']})
                existing_user = result.scalar()

                if existing_user:
                    raise ValueError('Email already registered')

                user_data['password_hash'] = get_password_hash(user_data['password_hash'])

                table_users_insert_query = text(
                    '''
                    INSERT INTO users (firstname, lastname, email, password_hash, phone_number, role)
                    VALUES (:firstname, :lastname, :email, :password_hash, :phone_number, :role)
                    RETURNING user_id
                    '''
                )
                result = await session.execute(
                    table_users_insert_query,
                    {
                        'firstname': user_data['firstname'],
                        'lastname': user_data['lastname'],
                        'email': user_data['email'],
                        'password_hash': user_data['password_hash'],
                        'phone_number': user_data['phone_number'],
                        'role': user_data['role']
                    }
                )
                user_id = result.scalar()

                table_analysts_insert_query = text(
                    '''
                    INSERT INTO analysts (user_id, grade)
                    VALUES (:user_id, :grade)
                    RETURNING analyst_id
                    '''
                )
                result = await session.execute(
                    table_analysts_insert_query,
                    {
                        'user_id': user_id,
                        'grade': analyst_data['grade']
                    }
                )
                analyst_id = result.scalar()

                await session.commit()
                print("Analyst successfully registered")

                return analyst_id

            except Exception as error:
                print(f'Error while registering analyst: {error}')

                raise error


async def add_car(car_data):
    async with async_session() as session:
        async with session.begin():
            try:
                query = text(
                    '''
                    SELECT car_id
                    FROM cars
                    WHERE car_number = :car_number
                    '''
                )
                result = await session.execute(query, {'car_number': car_data['car_number']})
                existing_car = result.scalar()

                if existing_car:
                    raise ValueError('Car number already registered')

                table_cars_insert_query = text(
                    '''
                    INSERT INTO cars (car_number, status)
                    VALUES (:car_number, :status)
                    RETURNING car_id
                    '''
                )
                result = await session.execute(
                    table_cars_insert_query,
                    {
                        'car_number': car_data['car_number'],
                        'status': car_data['status']
                    }
                )
                car_id = result.scalar()

                table_car_info_insert_query = text(
                    '''
                    INSERT INTO car_info (car_id, color, model, car_class, year)
                    VALUES (:car_id, :color, :model, :car_class, :year)
                    RETURNING car_id
                    '''
                )
                result = await session.execute(
                    table_car_info_insert_query,
                    {
                        'car_id': car_id,
                        'color': car_data['color'],
                        'model': car_data['model'],
                        'car_class': car_data['car_class'],
                        'year': car_data['year']
                    }
                )
                car_id = result.scalar()

                await session.commit()
                print("Car successfully registered")

                return car_id

            except Exception as error:
                print(f'Error while registering car: {error}')

                raise error


async def add_ride(ride_data):
    async with async_session() as session:
        async with session.begin():
            try:
                table_rides_insert_query = text(
                    '''
                    INSERT INTO rides (driver_id, passenger_id, car_id, rate)
                    VALUES (:driver_id, :passenger_id, :car_id, :rate)
                    RETURNING ride_id
                    '''
                )
                result = await session.execute(
                    table_rides_insert_query,
                    {
                        'driver_id': ride_data['driver_id'],
                        'passenger_id': ride_data['passenger_id'],
                        'car_id': ride_data['car_id'],
                        'rate': ride_data['rate']
                    }
                )
                ride_id = result.scalar()

                table_ride_info_insert_query = text(
                    '''
                    INSERT INTO ride_info (ride_id, ride_date, ride_duration_seconds, ride_cost_rubles, distance)
                    VALUES (:ride_id, :ride_date, :ride_duration_seconds, :ride_cost_rubles, :distance)
                    RETURNING ride_id
                    '''
                )
                result = await session.execute(
                    table_ride_info_insert_query,
                    {
                        'ride_id': ride_id,
                        'ride_date': ride_data['ride_date'].replace(tzinfo=None),
                        'ride_duration_seconds': ride_data['ride_duration_seconds'],
                        'ride_cost_rubles': ride_data['ride_cost_rubles'],
                        'distance': ride_data['distance']
                    }
                )
                ride_id = result.scalar()

                await session.commit()
                print("Ride successfully registered")

                return ride_id

            except Exception as error:
                print(f'Error while registering ride: {error}')

                raise error