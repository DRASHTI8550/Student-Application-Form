
import streamlit as st
import mysql.connector
import pandas as pd
from datetime import date

# Page configuration
# st.set_page_config(page_title="Student Management System")

st.title("🎓 Student Management System")


# 1. Connect Python with MySQL
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="student_db"
    )


# 2. Create Students Table
def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_name VARCHAR(100) NOT NULL,
            birthdate DATE NOT NULL,
            age INT NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


# Create table when application starts
try:
    create_table()
    st.success("MySQL Database Connected Successfully!")
except mysql.connector.Error as e:
    st.error(f"Database Connection Error: {e}")
    st.stop()


# 3. Student Details Form
st.header("Enter Student Details")

name = st.text_input("Student Name")

birthdate = st.date_input(
    "Birthdate",
    min_value=date(1900, 1, 1),
    max_value=date.today()
)

email = st.text_input("Email Address")


# 4. Calculate Student Age
today = date.today()

age = today.year - birthdate.year

if (today.month, today.day) < (birthdate.month, birthdate.day):
    age -= 1

st.write("Student Age:", age)


# 5. Add Student Details into MySQL
if st.button("Add Student"):

    if name.strip() == "":
        st.error("Please enter student name")

    elif email.strip() == "" or "@" not in email:
        st.error("Please enter a valid email address")

    else:
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO students
                (student_name, birthdate, age, email)
                VALUES (%s, %s, %s, %s)
            """

            values = (
                name.strip(),
                birthdate,
                age,
                email.strip()
            )

            cursor.execute(query, values)
            conn.commit()

            st.success("Student added successfully!")

        except mysql.connector.IntegrityError:
            st.error("This email address already exists!")

        except mysql.connector.Error as e:
            st.error(f"Error: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()


# 6. Display Student Details from MySQL
st.header("📋 View Student Details")

if st.button("View Students"):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM students ORDER BY id")

        students = cursor.fetchall()

        if students:
            df = pd.DataFrame(students)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No student details found in database.")

    except mysql.connector.Error as e:
        st.error(f"Error: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
