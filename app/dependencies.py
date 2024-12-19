from sqlalchemy import text

from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
from datetime import datetime, timezone

from src.config import get_jwt_params
from app.schemas import *
from src.db.database import async_session


def get_token(request: Request):
    token = request.cookies.get('token')

    if not token:
        token = request.headers.get('Authorization')

        if token and token.startswith('Bearer '):
            token = token.split(" ")[1]


    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is missing')

    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        jwt_params = get_jwt_params()
        payload = jwt.decode(token, jwt_params['secret_key'], algorithms=[jwt_params['algorithm']])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is invalid')

    expire = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), timezone.utc)

    if not expire or expire_time < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is expired')

    user_id = payload.get('sub')

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User ID is missing')

    async with async_session() as session:
        async with session.begin():
            get_user_role_query = text(
                '''
                SELECT role
                FROM users
                WHERE user_id = :user_id
                '''
            )
            result = await session.execute(get_user_role_query, {'user_id': int(user_id)})
            user = result.fetchone()

            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

            if user[0] == 'driver':
                get_driver_user_query = text(
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
                    WHERE users.user_id = :user_id
                    '''
                )
                result = await session.execute(get_driver_user_query, {'user_id': int(user_id)})
                driver = result.fetchone()

                if not driver:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Driver not found')

                driver_dict = driver._mapping

                return SDriverGet(**driver_dict)
            elif user[0] == 'passenger':
                get_passenger_user_query = text(
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
                    WHERE users.user_id = :user_id
                    '''
                )
                result = await session.execute(get_passenger_user_query, {'user_id': int(user_id)})
                passenger = result.fetchone()

                if not passenger:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Passenger not found')

                passenger_dict = passenger._mapping

                return SPassengerGet(**passenger_dict)
            elif user[0] == 'analyst':
                get_analyst_user_query = text(
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
                    WHERE users.user_id = :user_id
                    '''
                )
                result = await session.execute(get_analyst_user_query, {'user_id': int(user_id)})
                analyst = result.fetchone()

                if not analyst:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Analyst not found')

                analyst_dict = analyst._mapping

                return SAnalystGet(**analyst_dict)
            elif user[0] == 'admin':
                get_admin_data_query = text(
                    '''
                    SELECT 
                        user_id,
                        firstname,
                        lastname,
                        email,
                        phone_number
                    FROM users
                    WHERE users.user_id = :user_id
                    '''
                )
                result = await session.execute(get_admin_data_query, {'user_id': int(user_id)})
                admin = result.fetchone()

                if not admin:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Admin not found')

                admin_dict = admin._mapping

                return SAdminGet(**admin_dict)
