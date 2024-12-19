from typing import Union

from fastapi import APIRouter,  HTTPException, Response, status, Depends, Header, UploadFile, File
import subprocess
import os
from app.repository import TaskRepository
from src.auth import authenticate_user
import random, string
from src.config import settings
from app.schemas import *
from src.auth import *
from app.dependencies import *


router = APIRouter(tags= ["Что-то делаем"])

BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backups"))
DB_CONTAINER_NAME = "taxi_db"

@router.post("/backup/restore")
async def restore_backup(request: RestoreRequest):
    try:
        # Путь к папке backups
        BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backups"))
        file_name = request.backup_file

        # Полный путь к файлу
        backup_file_path = os.path.join(BACKUP_DIR, file_name)

        if not os.path.exists(backup_file_path):
            raise HTTPException(status_code=404, detail="Backup file not found")

        # Имя временного файла внутри контейнера
        container_file_path = f"/tmp/{file_name}"

        # Копирование файла в контейнер
        subprocess.run(
            ["docker", "cp", backup_file_path, f"taxi_db:{container_file_path}"],
            check=True
        )

        # Восстановление базы данных
        command = [
            "docker", "exec", "taxi_db",
            "pg_restore", "--verbose", "--clean", "--no-owner", "-U", "taxi_db_user",
            "-d", "taxi_db", container_file_path
        ]
        subprocess.run(command, check=True)

        # Удаление временного файла из контейнера
        subprocess.run(["docker", "exec", "taxi_db", "rm", container_file_path], check=True)

        return {"message": "Database successfully restored"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.post("/backup/create")
def create_backup(request: CreateBackupRequest):
    BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backups"))
    os.makedirs(BACKUP_DIR, exist_ok=True)

    try:
        # Имя файла бэкапа
        backup_name = request.backup_file
        container_backup_path = f"/tmp/{backup_name}"
        local_backup_path = os.path.join(BACKUP_DIR, backup_name)

        # Команда для создания бэкапа в контейнере
        dump_command = [
            "docker", "exec", DB_CONTAINER_NAME,
            "pg_dump", "-Fc",
            "-U", os.getenv("DB_USER", "taxi_db_user"),
            os.getenv("DB_NAME", "taxi_db"),
            "-f", container_backup_path
        ]

        # Выполнение команды в контейнере
        subprocess.run(dump_command, check=True)

        # Копирование файла бэкапа из контейнера на локальный диск
        copy_command = ["docker", "cp", f"{DB_CONTAINER_NAME}:{container_backup_path}", local_backup_path]
        subprocess.run(copy_command, check=True)

        # Удаление временного бэкапа из контейнера
        cleanup_command = ["docker", "exec", DB_CONTAINER_NAME, "rm", container_backup_path]
        subprocess.run(cleanup_command, check=True)

        return {"message": "Backup successfully created", "file": local_backup_path}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.post("/login")
async def login(response: Response, user_data: SUserAuth):
    user_info = await authenticate_user(email=user_data.email, password=user_data.password)

    if user_info is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token({"sub": str(user_info["user_id"])})
    response.set_cookie(key="user_access_token", value=access_token, httponly=True, secure=False)
    response.set_cookie(key="user_id", value=str(user_info["user_id"]), httponly=True, secure=False)
    response.set_cookie(key="role", value=str(user_info["role"]), httponly=True, secure=False)

    return {"access_token": access_token, "refresh_token": None, "role": str(user_info["role"])}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="user_access_token")

    return {"message": "User successfully logged out"}


@router.get("/profile", response_model=Union[SAdminGet, SDriverGet, SPassengerGet, SAnalystGet])
async def get_profile(user_data: Union[SAdminGet, SDriverGet, SPassengerGet, SAnalystGet] = Depends(get_current_user)):
    return user_data


@router.get("/drivers/get_all")
async def get_users():
    drivers = await TaskRepository.get_all_drivers()

    return drivers


@router.get("/passengers/get_all")
async def get_passengers():
    passengers = await TaskRepository.get_all_passengers()

    return passengers


@router.get("/analysts/get_all")
async def get_analysts():
    analysts = await TaskRepository.get_all_analysts()

    return analysts


@router.get("/cars/get_all")
async def get_cars():
    cars = await TaskRepository.get_all_cars()

    return cars


@router.get("/rides/get_all")
async def get_rides():
    rides = await TaskRepository.get_all_rides()

    return rides


@router.get("/passenger/get_rides")
async def get_passenger_rides(user: SPassengerGet = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            try:
                passenger_id = user.passenger_id

                get_ride_query = text(
                    '''
                    SELECT 
                        driver_id,
                        passenger_id,
                        car_id,
                        rate,
                        ride_date,
                        ride_duration_seconds,
                        ride_cost_rubles,
                        distance
                    FROM rides INNER JOIN ride_info ON rides.ride_id = ride_info.ride_id
                    WHERE passenger_id = :passenger_id
                    '''
                )
                results = await session.execute(get_ride_query, {"passenger_id": passenger_id})
                rides = [dict(row) for row in results.mappings()]

                return rides
            except Exception as error:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)


@router.get("/driver/get_rides")
async def get_driver_rides(user: SDriverGet = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            try:
                driver_id = user.driver_id

                get_ride_query = text(
                    '''
                    SELECT 
                        driver_id,
                        passenger_id,
                        car_id,
                        rate,
                        ride_date,
                        ride_duration_seconds,
                        ride_cost_rubles,
                        distance
                    FROM rides INNER JOIN ride_info ON rides.ride_id = ride_info.ride_id
                    WHERE driver_id = :driver_id
                    '''
                )
                results = await session.execute(get_ride_query, {"driver_id": driver_id})
                rides = [dict(row) for row in results.mappings()]

                return rides
            except Exception as error:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)


@router.post("/admin/add_admin")
async def add_admin(data: SUserAdd):
    admin_id = await TaskRepository.add_admin(data)

    return {"message": "Admin successfully added", "admin_id": admin_id}


@router.post("/driver/registration")
async def make_driver_registration(data: SDriverRegistration):
    driver_id = await TaskRepository.make_driver_registration(data)

    return {"message": "Driver registered successful", "driver_id": driver_id}


@router.post("/passenger/registration")
async def make_passenger_registration(data: SPassengerRegistration):
    passenger_id = await TaskRepository.make_passenger_registration(data)

    return {"message": "Passenger registered successful", "passenger_id": passenger_id}


@router.post("/analyst/registration")
async def make_analyst_registration(data: SAnalystRegistration):
    analyst_id = await TaskRepository.make_analyst_registration(data)

    return {"message": "Analyst registered successful", "analyst_id": analyst_id}


@router.post("/cars/add")
async def add_new_car(data: SCarAdd):
    car_id = await TaskRepository.add_new_car(data)

    return {"message": "New car added successfully", "car_id": car_id}


@router.post("/rides/add")
async def add_new_ride(data: SRideAdd):
    ride_id = await TaskRepository.add_new_ride(data)

    return {"message": "New ride added successfully", "ride_id": ride_id}


@router.put("/driver/update")
async def update_driver(data_to_update: SDriverUpdate, user: SDriverGet = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            try:
                get_user_id_query = text(
                    '''
                    SELECT user_id
                    FROM drivers
                    WHERE driver_id = :driver_id
                    '''
                )
                result = await session.execute(get_user_id_query, {"driver_id": user.driver_id})
                user_id = result.scalar()

                user_data = data_to_update.user_data.model_dump()
                driver_data = data_to_update.driver_data.model_dump()

                users_update_query = text(
                    '''
                    UPDATE users
                    SET
                        firstname = :firstname,
                        lastname = :lastname,
                        email = :email,
                        phone_number = :phone_number
                    WHERE user_id = :user_id
                    '''
                )
                user_data['user_id'] = user_id

                result = await session.execute(users_update_query, user_data)
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="User not found")

                drivers_update_query = text(
                    '''
                    UPDATE drivers
                    SET
                        birth_date = :birth_date,
                        driver_rides = :driver_rides,
                        driver_time_accidents = :driver_time_accidents,
                        driver_license_number = :driver_license_number
                    WHERE user_id = :user_id
                    '''
                )
                driver_data['user_id'] = user_id

                result = await session.execute(drivers_update_query, driver_data)
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Driver not found")

                return {"detail": "Driver updated successfully"}

            except Exception as error:
                raise HTTPException(status_code=500, detail=str(error))


@router.put("/passenger/update")
async def update_passenger(data_to_update: SPassengerUpdate, user: SPassengerGet = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            try:
                get_user_id_query = text(
                    '''
                    SELECT user_id
                    FROM passengers
                    WHERE passenger_id = :passenger_id
                    '''
                )
                result = await session.execute(get_user_id_query, {"passenger_id": user.passenger_id})
                user_id = result.scalar()

                user_data = data_to_update.user_data.model_dump()
                passenger_data = data_to_update.passenger_data.model_dump()

                users_update_query = text(
                    '''
                    UPDATE users
                    SET
                        firstname = :firstname,
                        lastname = :lastname,
                        email = :email,
                        phone_number = :phone_number
                    WHERE user_id = :user_id
                    '''
                )
                user_data['user_id'] = user_id

                result = await session.execute(users_update_query, user_data)
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="User not found")

                passengers_update_query = text(
                    '''
                    UPDATE passengers
                    SET
                        birth_date = :birth_date
                    WHERE user_id = :user_id
                    '''
                )

                passenger_data['user_id'] = user_id

                result = await session.execute(passengers_update_query, passenger_data)
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Passenger not found")

                return {"detail": "Passenger updated successfully"}

            except Exception as error:
                raise HTTPException(status_code=500, detail=str(error))


@router.put("/analyst/update")
async def update_analyst(data_to_update: SAnalystUpdate, user: SAnalystGet = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            try:
                get_user_id_query = text(
                    '''
                    SELECT user_id
                    FROM analysts
                    WHERE analyst_id = :analyst_id
                    '''
                )
                result = await session.execute(get_user_id_query, {"analyst_id": user.analyst_id})
                user_id = result.scalar()

                user_data = data_to_update.user_data.model_dump()
                analyst_data = data_to_update.analyst_data.model_dump()

                users_update_query = text(
                    '''
                    UPDATE users
                    SET
                        firstname = :firstname,
                        lastname = :lastname,
                        email = :email,
                        phone_number = :phone_number
                    WHERE user_id = :user_id
                    '''
                )
                user_data['user_id'] = user_id

                result = await session.execute(users_update_query, user_data)
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="User not found")

                analyst_update_query = text(
                    '''
                    UPDATE analysts
                    SET
                        grade = :grade
                    WHERE user_id = :user_id
                    '''
                )

                analyst_data['user_id'] = user_id

                result = await session.execute(analyst_update_query, analyst_data)
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Analyst not found")

                return {"detail": "Analyst updated successfully"}

            except Exception as error:
                raise HTTPException(status_code=500, detail=str(error))


@router.put("/car/update/{car_id}")
async def update_car(car_id: int, data_to_update: SCarUpdate):
    async with async_session() as session:
        async with session.begin():
            try:
                car_data = data_to_update.model_dump()

                cars_update_query = text(
                    '''
                    UPDATE cars
                    SET
                        car_number = :car_number,
                        status = :status
                    WHERE car_id = :car_id
                    '''
                )

                result = await session.execute(
                    cars_update_query,
                    {
                        'car_id': car_id,
                        'car_number': car_data['car_number'],
                        'status': car_data['status']
                    }
                )

                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Car not found")

                car_info_update_query = text(
                    '''
                    UPDATE car_info
                    SET
                        color = :color,
                        car_class = :car_class
                    WHERE car_id = :car_id
                    '''
                )

                result = await session.execute(
                    car_info_update_query,
                    {
                        'car_id': car_id,
                        'color': car_data['color'],
                        'car_class': car_data['car_class']
                    }
                )

                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Car not found")

                return {"detail": "Car updated successfully"}

            except Exception as error:
                raise HTTPException(status_code=500, detail=str(error))


@router.post("/analyst/query")
async def execute_sql(query: SQLQuery):
    async with async_session() as session:
        async with session.begin():
            try:
                sql_query = text(query.query)

                # Проверка на безопасное выполнение SQL-запросов (например, с использованием параметризации)
                result = await session.execute(sql_query)
                data = result.mappings().all()

                return {"data": data}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))


@router.post("/drivers/clear_table")
async def clear_drivers():
    async with async_session() as session:
        async with session.begin():
            try:
                query = text(
                    '''
                    TRUNCATE TABLE drivers RESTART IDENTITY CASCADE
                    '''
                )
                await session.execute(query)
                await session.commit()

                return {"detail": "Drivers cleared"}
            except Exception as error:
                raise HTTPException(status_code=400, detail=str(error))


@router.post("/passengers/clear_table")
async def clear_passengers():
    async with async_session() as session:
        async with session.begin():
            try:
                query = text(
                    '''
                    TRUNCATE TABLE passengers RESTART IDENTITY CASCADE
                    '''
                )
                await session.execute(query)
                await session.commit()

                return {"detail": "Passengers cleared"}
            except Exception as error:
                raise HTTPException(status_code=400, detail=str(error))


@router.post("/analysts/clear_table")
async def clear_analysts():
    async with async_session() as session:
        async with session.begin():
            try:
                query = text(
                    '''
                    TRUNCATE TABLE analysts RESTART IDENTITY CASCADE
                    '''
                )
                await session.execute(query)
                await session.commit()

                return {"detail": "Analysts cleared"}
            except Exception as error:
                raise HTTPException(status_code=400, detail=str(error))


@router.post("/cars/clear_table")
async def clear_cars():
    async with async_session() as session:
        async with session.begin():
            try:
                query = text(
                    '''
                    TRUNCATE TABLE cars RESTART IDENTITY CASCADE
                    '''
                )
                await session.execute(query)
                await session.commit()

                return {"detail": "Cars cleared"}
            except Exception as error:
                raise HTTPException(status_code=400, detail=str(error))


@router.delete("/driver/delete/{driver_id}")
async def delete_driver(driver_id: int):
    async with async_session() as session:
        async with session.begin():
            select_user_id_query = text(
                '''
                SELECT user_id
                FROM drivers
                WHERE driver_id = :driver_id
                '''
            )
            result = await session.execute(select_user_id_query, {'driver_id': driver_id})
            user_id = result.fetchone()[0]

            delete_driver_query = text(
                '''
                DELETE FROM users WHERE user_id = :user_id
                '''
            )
            await session.execute(delete_driver_query, {'user_id': user_id})

            return {"detail": "Driver deleted"}


@router.delete("/passenger/delete/{passenger_id}")
async def delete_passenger(passenger_id: int):
    async with async_session() as session:
        async with session.begin():
            select_user_id_query = text(
                '''
                SELECT user_id
                FROM passengers
                WHERE passenger_id = :passenger_id
                '''
            )
            result = await session.execute(select_user_id_query, {'passenger_id': passenger_id})
            user_id = result.fetchone()[0]

            delete_passenger_query = text(
                '''
                DELETE FROM users WHERE user_id = :user_id
                '''
            )
            await session.execute(delete_passenger_query, {'user_id': user_id})

            return {"detail": "Passenger deleted"}


@router.delete("/analyst/delete/{analyst_id}")
async def delete_analyst(analyst_id: int):
    async with async_session() as session:
        async with session.begin():
            select_user_id_query = text(
                '''
                SELECT user_id
                FROM analysts
                WHERE analyst_id = :analyst_id
                '''
            )
            result = await session.execute(select_user_id_query, {'analyst_id': analyst_id})
            user_id = result.fetchone()[0]

            delete_analyst_query = text(
                '''
                DELETE FROM users WHERE user_id = :user_id
                '''
            )
            await session.execute(delete_analyst_query, {'user_id': user_id})

            return {"detail": "Analyst deleted"}


@router.delete("/car/delete/{car_id}")
async def delete_car(car_id: int):
    async with async_session() as session:
        async with session.begin():
            delete_car_query = text(
                '''
                DELETE FROM cars WHERE car_id = :car_id
                '''
            )
            await session.execute(delete_car_query, {'car_id': car_id})

            return {"detail": "Car deleted"}
