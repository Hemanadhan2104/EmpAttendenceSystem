import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import requests
import bcrypt

# Function to connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Hemanadhan@2104",
        database="employee_attendance"
    )

# Function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Function to verify passwords
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Function to register a new employee
def register_employee(name, department, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)  # Hash password before storing
    cursor.execute("INSERT INTO employees (name, department, email, password) VALUES (%s, %s, %s, %s)", 
                   (name, department, email, hashed_pw))
    conn.commit()
    conn.close()

# Function to verify login
def verify_login(email, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees WHERE email=%s", (email,))
    user = cursor.fetchone()
    conn.close()
    if user and verify_password(password, user["password"]):
        return user
    return None

# Function to get user location & IP
def get_location():
    try:
        response = requests.get("https://ipinfo.io")
        data = response.json()
        return data.get("city", "Unknown"), data.get("ip", "Unknown")
    except:
        return "Unknown", "Unknown"

# Function to mark attendance
def mark_attendance(user_id, status):
    location, ip_address = get_location()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (employee_id, status, location, ip_address) VALUES (%s, %s, %s, %s)", 
                   (user_id, status, location, ip_address))
    conn.commit()
    conn.close()

# Function to fetch attendance data
def fetch_attendance_data():
    conn = get_db_connection()
    df = pd.read_sql("SELECT employees.name, employees.department, attendance.date, attendance.time, attendance.status, attendance.location, attendance.ip_address FROM attendance JOIN employees ON attendance.employee_id = employees.id ORDER BY attendance.date DESC", conn)
    conn.close()
    return df

# Streamlit App
st.title("📊 Employee Attendance System")

# Sidebar Navigation
menu = st.sidebar.radio("Navigation", ["Login", "Register", "Dashboard"])

# Registration Form
if menu == "Register":
    st.sidebar.header("📝 Register New Employee")
    name = st.sidebar.text_input("Full Name")
    department = st.sidebar.text_input("Department")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    confirm_password = st.sidebar.text_input("Confirm Password", type="password")
    
    if st.sidebar.button("Register"):
        if password != confirm_password:
            st.sidebar.error("❌ Passwords do not match!")
        else:
            try:
                register_employee(name, department, email, password)
                st.sidebar.success("✅ Registration Successful! You can now log in.")
            except mysql.connector.errors.IntegrityError:
                st.sidebar.error("❌ Email already registered!")

# Login System
if menu == "Login":
    st.sidebar.header("🔐 Employee Login")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        user = verify_login(email, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.sidebar.success("✅ Login Successful! You can now click dashboard.")
            # st.rerun()
             
            
        else:
            st.sidebar.error("❌ Invalid credentials")

# After login
if menu == "Dashboard" and "logged_in" in st.session_state and st.session_state.logged_in:
    st.sidebar.header(f"👤 Welcome, {st.session_state.user['name']}")
    st.sidebar.write(f"Department: {st.session_state.user['department']}")

   

    # Attendance Marking Form
    st.write("### 📝 Mark Attendance")
    status = st.radio("Select Status", ["Present", "Absent", "Late"])
    if st.button("Submit Attendance"):
        mark_attendance(st.session_state.user['id'], status)
        st.success("✅ Attendance Recorded!")
        st.rerun()

    # Fetch Logged-in User's Attendance Data
    def fetch_user_attendance(user_id):
        conn = get_db_connection()
        query = "SELECT date, time, status, location, ip_address FROM attendance WHERE employee_id = %s ORDER BY date DESC"
        df = pd.read_sql(query, conn, params=[user_id])
        conn.close()
        return df


    # Display Only the Logged-in User's Attendance Records
    df = fetch_user_attendance(st.session_state.user['id'])
    st.write("### 📋 Your Attendance Records")
    st.dataframe(df)

    if not df.empty:
        # Attendance Insights
        st.write("### 📊 Your Attendance Insights")

        # Attendance Pie Chart
        fig1 = px.pie(df, names="status", title="Your Attendance Status Distribution", hole=0.4)
        st.plotly_chart(fig1)

      


    # Logout Button
    if st.sidebar.button("Logout"):
        del st.session_state.logged_in
        del st.session_state.user
        st.rerun()
