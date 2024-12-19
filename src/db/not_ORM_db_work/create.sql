CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    firstname VARCHAR NOT NULL,
    lastname VARCHAR NOT NULL,
    email VARCHAR NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL UNIQUE,
    phone_number VARCHAR NOT NULL UNIQUE,
    role VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS drivers (
    driver_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    birth_date DATE NOT NULL,
    sex VARCHAR NOT NULL,
    driver_rides INTEGER NOT NULL DEFAULT 0,
    driver_time_accidents INTEGER NOT NULL DEFAULT 0,
    driver_license_number VARCHAR NOT NULL UNIQUE,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS passengers (
    passenger_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    birth_date DATE NOT NULL,
    sex VARCHAR NOT NULL,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS analysts (
    analyst_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    grade VARCHAR NOT NULL,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cars (
    car_id SERIAL PRIMARY KEY,
    car_number VARCHAR NOT NULL UNIQUE,
    status VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS car_info (
    car_id INTEGER PRIMARY KEY,
    color VARCHAR NOT NULL,
    model VARCHAR NOT NULL,
    car_class VARCHAR NOT NULL,
    year INTEGER NOT NULL,

    FOREIGN KEY (car_id) REFERENCES cars(car_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rides (
    ride_id INTEGER PRIMARY KEY,
    driver_id INTEGER NOT NULL,
    passenger_id INTEGER NOT NULL,
    car_id INTEGER NOT NULL,
    rate FLOAT NOT NULL DEFAULT 5.0,

    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
    FOREIGN KEY (car_id) REFERENCES cars(car_id)
);

CREATE TABLE IF NOT EXISTS ride_info (
    ride_id INTEGER PRIMARY KEY,
    ride_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ride_duration_seconds INTEGER NOT NULL,
    ride_cost_rubles INTEGER NOT NULL,
    distance INTEGER NOT NULL,

    FOREIGN KEY (ride_id) REFERENCES rides(ride_id) ON DELETE CASCADE
);