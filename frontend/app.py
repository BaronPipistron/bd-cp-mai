import streamlit as st
import requests
import pandas as pd
from datetime import datetime

import os

API_URL = "http://localhost:8000"


def login():
    st.title("Authorization")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not email or not password:
            st.error("Email and Password cannot be empty")
            return

        response = requests.post(f"{API_URL}/login", json={"email": email, "password": password})

        if response.status_code == 200:
            token = response.cookies.get("user_access_token")
            role = response.cookies.get("role")
            st.session_state.token = token
            st.session_state.role = role
            st.success("Authorization Successful")
            st.stop()
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")


def registration():
    st.title("Registration")

    role = st.selectbox("Select Role", ["Driver", "Passenger", "Analyst"])

    firstname = st.text_input("Firstname")
    lastname = st.text_input("Lastname")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    phone_number = st.text_input("Phone Number")

    if role == "Driver":
        birth_date = st.date_input("Date of Birth")
        sex = st.selectbox("Sex", ["M", "F"])
        driver_rides = st.number_input("Number of Rides", min_value=0)
        driver_time_accidents = st.number_input("Number of Accidents", min_value=0)
        driver_license_number = st.text_input("Driver License Number")
    elif role == "Passenger":
        birth_date = st.date_input("Date of Birth")
        sex = st.selectbox("Sex", ["M", "F"])
    elif role == "Analyst":
        grade = st.text_input("Grade")

    if st.button("Register"):
        user_data = {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "password_hash": password,
            "phone_number": phone_number,
            "role": role.lower()
        }

        if role == "Driver":
            role_data = {
                "birth_date": str(birth_date),
                "sex": sex,
                "driver_rides": driver_rides,
                "driver_time_accidents": driver_time_accidents,
                "driver_license_number": driver_license_number
            }
            endpoint = "/driver/registration"
            payload = {"user_data": user_data, "driver_data": role_data}
        elif role == "Passenger":
            role_data = {
                "birth_date": str(birth_date),
                "sex": sex
            }
            endpoint = "/passenger/registration"
            payload = {"user_data": user_data, "passenger_data": role_data}
        elif role == "Analyst":
            role_data = {"grade": grade}
            endpoint = "/analyst/registration"
            payload = {"user_data": user_data, "analyst_data": role_data}

        response = requests.post(f"{API_URL}{endpoint}", json=payload)

        if response.status_code == 200:
            st.success(f"{role} registered successfully!")
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")


def profile():
    st.title("Profile")

    token = st.session_state.get("token")
    role = st.session_state.get("role")

    if not token:
        st.error("You must be logged in to access the profile")

        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/profile", headers=headers)

    if response.status_code == 200:
        user_data = response.json()

        st.title(f"Welcome {user_data['firstname']} {user_data['lastname']}")
        st.subheader("Profile Information")

        st.markdown("---")

        st.write(f"Email: {user_data['email']}")
        st.write(f"Phone Number: {user_data['phone_number']}")

        if role == "admin":
            pass
        elif role == "driver":
            st.write(f"Date of Birth: {user_data['birth_date']}")
            st.write(f"Sex: {user_data['sex']}")
            st.write(f"Driver License: {user_data['driver_license_number']}")
            st.write(f"Rides: {user_data['driver_rides']}")
            st.write(f"Accidents: {user_data['driver_time_accidents']}")
        elif role == "passenger":
            st.write(f"Date of Birth: {user_data['birth_date']}")
            st.write(f"Sex: {user_data['sex']}")
        elif role == "analyst":
            st.write(f"Grade: {user_data['grade']}")

        if role == "driver" or role == "passenger":
            st.subheader("My Rides")

            if st.button("View My Rides"):
                if role == "passenger":
                    rides_response = requests.get(f"{API_URL}/passenger/get_rides", headers=headers)
                    if rides_response.status_code == 200:
                        rides = rides_response.json()

                        for ride in rides:
                            st.write("---")
                            st.write(f"Driver ID: {ride['driver_id']}")
                            st.write(f"Passenger ID: {ride['passenger_id']}")
                            st.write(f"Car ID: {ride['car_id']}")
                            st.write(f"Rate: {ride['rate']}")
                            st.write(f"Date: {ride['ride_date']}")
                            st.write(f"Duration (seconds): {ride['ride_duration_seconds']}")
                            st.write(f"Cost (rubles): {ride['ride_cost_rubles']}")
                            st.write(f"Distance (km): {ride['distance']}")
                    else:
                        st.error("Unable to fetch rides")
                elif role == "driver":
                    rides_response = requests.get(f"{API_URL}/driver/get_rides", headers=headers)
                    if rides_response.status_code == 200:
                        rides = rides_response.json()

                        for ride in rides:
                            st.write("---")
                            st.write(f"Driver ID: {ride['driver_id']}")
                            st.write(f"Passenger ID: {ride['passenger_id']}")
                            st.write(f"Car ID: {ride['car_id']}")
                            st.write(f"Rate: {ride['rate']}")
                            st.write(f"Date: {ride['ride_date']}")
                            st.write(f"Duration (seconds): {ride['ride_duration_seconds']}")
                            st.write(f"Cost (rubles): {ride['ride_cost_rubles']}")
                            st.write(f"Distance (km): {ride['distance']}")
                    else:
                        st.error("Unable to fetch rides")

        st.markdown("---")

        st.subheader("Update My Data")

        updated_firstname = st.text_input("Firstname")
        updated_lastname = st.text_input("Lastname")
        updated_email = st.text_input("Email")
        updated_phone = st.text_input("Phone Number")

        if role == "driver":
            updated_birth_date = st.date_input("Date of Birth")
            updated_birth_date = datetime.strptime(str(updated_birth_date), "%Y-%m-%d").isoformat()

            updated_driver_rides = st.number_input("Number of Rides", min_value=0)
            updated_driver_time_accidents = st.number_input("Number of Accidents", min_value=0)
            updated_driver_license_number = st.text_input("Driver License Number")
        elif role == "passenger":
            updated_birth_date = st.date_input("Date of Birth")
            updated_birth_date = datetime.strptime(str(updated_birth_date), "%Y-%m-%d").isoformat()
        elif role == "analyst":
            updated_grade = st.text_input("Grade", ["Intern", "Junior", "Middle", "Senior"])

        if st.button("Save"):
            if role == "driver":
                data_to_update = {
                    "user_data": {
                        "firstname": updated_firstname,
                        "lastname": updated_lastname,
                        "email": updated_email,
                        "phone_number": updated_phone,
                    },
                    "driver_data": {
                        "birth_date": updated_birth_date.split("T")[0],
                        "driver_rides": updated_driver_rides,
                        "driver_time_accidents": updated_driver_time_accidents,
                        "driver_license_number": updated_driver_license_number,
                    }
                }

                endpoint = "/driver/update"
                payload = data_to_update
            elif role == "passenger":
                data_to_update = {
                    "user_data": {
                        "firstname": updated_firstname,
                        "lastname": updated_lastname,
                        "email": updated_email,
                        "phone_number": updated_phone,
                    },
                    "passenger_data": {
                        "birth_date": updated_birth_date.split("T")[0]
                    }
                }

                endpoint = "/passenger/update"
                payload = data_to_update
            elif role == "analyst":
                data_to_update = {
                    "user_data": {
                        "firstname": updated_firstname,
                        "lastname": updated_lastname,
                        "email": updated_email,
                        "phone_number": updated_phone,
                    },
                    "analyst_data": {
                        "grade": updated_grade
                    }
                }

                endpoint = "/analyst/update"
                payload = data_to_update

            response = requests.put(f"{API_URL}{endpoint}", json=payload, headers=headers)

            if response.status_code == 200:
                st.success("Profile updated successfully!")
                st.rerun()
            else:
                st.error("Unable to update profile")

                if isinstance(response.json()["detail"], str):
                    st.error(response.json()["detail"])

                else:
                    for i in range(len(response.json()["detail"])):
                        st.error(response.json()["detail"][i]["msg"] + "\n\nПоле: " +
                                 response.json()["detail"][i]["loc"][1])

        st.markdown("---")

        st.subheader("Logout")
        if st.button("Logout"):
            response = requests.post(f"{API_URL}/logout", cookies={"user_access_token": token})
            if response.status_code == 200:
                st.success("Successfully logged out!")
                del st.session_state.token
                del st.session_state.role

                st.rerun()
            else:
                st.error("Error logging out")


def all_drivers():
    st.title("All Drivers")

    role = st.session_state.get("role")

    if role not in ["driver", "analyst", "admin"]:
        st.error("Access denied")

        return

    response = requests.get(f"{API_URL}/drivers/get_all")

    if response.status_code == 200:
        drivers = response.json()

        if drivers:
            for driver in drivers:
                st.write(f"Firstname: {driver['firstname']}")
                st.write(f"Lastname: {driver['lastname']}")
                st.write(f"Email: {driver['email']}")
                st.write(f"Phone Number: {driver['phone_number']}")
                st.write(f"Birth Date: {driver['birth_date']}")
                st.write(f"Sex: {driver['sex']}")
                st.write(f"Driver Rides: {driver['driver_rides']}")
                st.write(f"Accidents: {driver['driver_time_accidents']}")
                st.write(f"Driver License: {driver['driver_license_number']}")
                st.write("---")
        else:
            st.write("No drivers available.")
    else:
        st.error("Error fetching drivers")


def all_passengers():
    st.title("All Passengers")

    role = st.session_state.get("role")

    if role not in ["analyst", "admin"]:
        st.error("Access denied")

        return

    response = requests.get(f"{API_URL}/passengers/get_all")

    if response.status_code == 200:
        passengers = response.json()

        if passengers:
            for passenger in passengers:
                st.write(f"Firstname: {passenger['firstname']}")
                st.write(f"Lastname: {passenger['lastname']}")
                st.write(f"Email: {passenger['email']}")
                st.write(f"Phone Number: {passenger['phone_number']}")
                st.write(f"Birth Date: {passenger['birth_date']}")
                st.write(f"Sex: {passenger['sex']}")
                st.write("---")
        else:
            st.write("No passengers available.")
    else:
        st.error("Error fetching passengers")


def all_analysts():
    st.title("All Analysts")

    role = st.session_state.get("role")

    if role not in ["analyst", "admin"]:
        st.error("Access denied")

        return

    response = requests.get(f"{API_URL}/analysts/get_all")

    if response.status_code == 200:
        analysts = response.json()

        if analysts:
            for analyst in analysts:
                st.write(f"Firstname: {analyst['firstname']}")
                st.write(f"Lastname: {analyst['lastname']}")
                st.write(f"Email: {analyst['email']}")
                st.write(f"Phone Number: {analyst['phone_number']}")
                st.write(f"Grade: {analyst['grade']}")
                st.write("---")
        else:
            st.write("No analysts available.")
    else:
        st.error("Error fetching analysts")


def all_cars():
    st.title("All Cars")

    role = st.session_state.get("role")

    if role not in ["driver", "analyst", "admin"]:
        st.error("Access denied")

        return

    response = requests.get(f"{API_URL}/cars/get_all")

    if response.status_code == 200:
        cars = response.json()

        if cars:
            for car in cars:
                st.write(f"Car Number: {car['car_number']}")
                st.write(f"Status: {car['status']}")
                st.write(f"Color: {car['color']}")
                st.write(f"Model: {car['model']}")
                st.write(f"Class: {car['car_class']}")
                st.write(f"Year: {car['year']}")
                st.write("---")
        else:
            st.write("No cars available.")
    else:
        st.error("Error fetching cars")


def all_rides():
    st.title("All Rides")

    role = st.session_state.get("role")

    if role not in ["analyst", "admin"]:
        st.error("Access denied")

        return

    response = requests.get(f"{API_URL}/rides/get_all")

    if response.status_code == 200:
        rides = response.json()

        if rides:
            for ride in rides:
                st.write(f"Driver ID: {ride['driver_id']}")
                st.write(f"Passenger ID: {ride['passenger_id']}")
                st.write(f"Car ID: {ride['car_id']}")
                st.write(f"Rate: {ride['rate']}")
                st.write(f"Ride Date: {ride['ride_date']}")
                st.write(f"Ride Time (min): {ride['ride_duration_seconds'] / 60}")
                st.write(f"Ride Cost (rubs): {ride['ride_cost_rubles']}")
                st.write(f"Distance (km): {ride['distance']}")
                st.write("---")
        else:
            st.write("No cars available.")
    else:
        st.error("Error fetching cars")


def sql_query():
    st.title("SQL Query")

    role = st.session_state.get("role")

    if role not in ["analyst", "admin"]:
        st.error("Access denied")

        return

    query = st.text_area("Enter SQL query:")

    if st.button("Execute SQL Query"):
        if query:
            response = requests.post(f"{API_URL}/analyst/query", json={"query": query})

            if response.status_code == 200:
                data = response.json().get("data", [])

                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df)
                else:
                    st.info("No results found for the query")
            else:
                st.error("Error running SQL query")
        else:
            st.warning("Enter SQL query")


def admin_panel():
    st.title("Admin Panel")

    token = st.session_state.get("token")
    role = st.session_state.get("role")

    headers = {"Authorization": f"Bearer {token}"}

    if role not in ["admin"]:
        st.error("Access denied")

        return

    action = st.selectbox(
        "Select Action",
        [
            "Add Admin", # dont work
            "Do DB BackUp", # dont work
            "Restore DB from BackUp", # dont work
            "Delete Driver by ID",
            "Delete Passenger by ID",
            "Delete Analyst by ID",
            "Add Car",
            "Delete Car by ID",
            "Add Ride",
            "Clear Table drivers",
            "Clear Table passengers",
            "Clear Table analysts",
            "Clear Table cars"
        ]
    )

    if action == "Add Admin":
        firstname = st.text_input("Firstname")
        lastname = st.text_input("Lastname")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        phone_number = st.text_input("Phone Number")

        payload = {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "password_hash": password,
            "phone_number": phone_number,
            "role": "admin"
        }

        if st.button("Add Admin"):
            response = requests.post(f"{API_URL}/admin/add_admin", json=payload, headers=headers)

            if response.status_code == 200:
                st.success(f"Admin {firstname} {lastname} registered successfully!")
            else:
                st.error("Error adding admin")

                for i in range(len(response.json()["detail"])):
                    st.error(response.json()["detail"][i]["msg"] + "\n\nПоле: " +
                             response.json()["detail"][i]["loc"][1])

    elif action == "Do DB BackUp":
        backup_file = st.text_input("BackUp File Name")
        payload = {"backup_file": backup_file}

        if st.button("Create Backup"):
            response = requests.post(f"{API_URL}/backup/create", json=payload)

            if response.status_code == 200:
                st.success(response.json().get("message"))
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

    elif action == "Restore DB from BackUp":
        backup_file = st.text_input("Backup file name")
        payload = {"backup_file": backup_file}

        if st.button("Restore Backup"):
            response = requests.post(f"{API_URL}/backup/restore", json=payload)

            if response.status_code == 200:
                st.success(response.json().get("message"))
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

    elif action == "Delete Driver by ID":
        driver_id = st.text_input("Driver ID")

        if st.button("Delete Driver by ID"):
            response = requests.delete(f"{API_URL}/driver/delete/{driver_id}")

            if response.status_code == 200:
                st.success(f"Driver {driver_id} deleted successfully!")
            else:
                st.error("Error deleting driver")

    elif action == "Delete Passenger by ID":
        passenger_id = st.text_input("Passenger ID")

        if st.button("Delete Passenger by ID"):
            response = requests.delete(f"{API_URL}/passenger/delete/{passenger_id}")

            if response.status_code == 200:
                st.success(f"Passenger {passenger_id} deleted successfully!")
            else:
                st.error("Error deleting passenger")

    elif action == "Delete Analyst by ID":
        analyst_id = st.text_input("Analyst ID")

        if st.button("Delete Analyst by ID"):
            response = requests.delete(f"{API_URL}/analyst/delete/{analyst_id}")

            if response.status_code == 200:
                st.success(f"Analyst {analyst_id} deleted successfully!")
            else:
                st.error("Error deleting analyst")

    elif action == "Add Car":
        car_number = st.text_input("Car Number")
        status = st.selectbox("Car Status", ["Active", "Inactive"])
        color = st.text_input("Car Color")
        model = st.text_input("Car Model")
        car_class = st.text_input("Car Class")
        year = st.text_input("Car Year")

        payload = {
            "car_number": car_number,
            "status": status,
            "color": color,
            "model": model,
            "car_class": car_class,
            "year": year
        }

        if st.button("Add Car"):
            response = requests.post(f"{API_URL}/cars/add", json=payload)

            if response.status_code == 200:
                st.success(f"Car added successfully!")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

    elif action == "Add Ride":
        driver_id = st.text_input("Driver ID")
        passenger_id = st.text_input("Passenger ID")
        car_id = st.text_input("Car ID")
        rate = st.text_input("Rate")
        ride_date = st.text_input("Ride Date")
        ride_duration_seconds = st.text_input("Ride Duration (Sec)")
        ride_cost_rubles = st.text_input("Ride Cost (Rub)")
        distance = st.text_input("Distance")

        try:
            ride_date = datetime.strptime(ride_date, "%d.%m.%Y").isoformat()
        except ValueError:
            st.error("Ride Date should be in the format DD.MM.YYYY")
            ride_date = None

        payload = {
            "driver_id": driver_id,
            "passenger_id": passenger_id,
            "car_id": car_id,
            "rate": rate,
            "ride_date": ride_date,
            "ride_duration_seconds": ride_duration_seconds,
            "ride_cost_rubles": ride_cost_rubles,
            "distance": distance
        }

        if st.button("Add Ride"):
            response = requests.post(f"{API_URL}/rides/add", json=payload)

            if response.status_code == 200:
                st.success(f"Ride added successfully!")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

    elif action == "Delete Car by ID":
        car_id = st.text_input("Car ID")

        if st.button("Delete Car by ID"):
            response = requests.delete(f"{API_URL}/car/delete/{car_id}")

            if response.status_code == 200:
                st.success(f"Car {car_id} deleted successfully!")
            else:
                st.error("Error deleting car")

    elif action == "Clear Table drivers":
        if st.button("Clear Drivers Table"):
            response = requests.post(f"{API_URL}/drivers/clear_table")

            if response.status_code == 200:
                st.success(f"Drivers table cleared successfully!")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

    elif action == "Clear Table passengers":
        if st.button("Clear Passengers Table"):
            response = requests.post(f"{API_URL}/passengers/clear_table")

            if response.status_code == 200:
                st.success(f"Passengers table cleared successfully!")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

    elif action == "Clear Table analysts":
        if st.button("Clear Analysts Table"):
            response = requests.post(f"{API_URL}/analysts/clear_table")

            if response.status_code == 200:
                st.success(f"Analysts table cleared successfully!")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

    elif action == "Clear Table cars":
        if st.button("Clear Cars Table"):
            response = requests.post(f"{API_URL}/cars/clear_table")

            if response.status_code == 200:
                st.success(f"Cars table cleared successfully!")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")


st.markdown(
    """
    <style>
    .stRadio > label {
        font-size: 24px; 
    }
    .stRadio > div {
        gap: 12px; 
    }
    </style>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Authorization",
        "Registration",
        "Profile",
        "Drivers",
        "Passengers",
        "Analysts",
        "Cars",
        "All Rides",
        "SQL Query",
        "Admin Panel"
    ]
)

if page == "Authorization":
    login()
elif page == "Registration":
    registration()
elif page == "Profile":
    profile()
elif page == "Drivers":
    all_drivers()
elif page == "Passengers":
    all_passengers()
elif page == "Analysts":
    all_analysts()
elif page == "Cars":
    all_cars()
elif page == "SQL Query":
    sql_query()
elif page == "Admin Panel":
    admin_panel()
