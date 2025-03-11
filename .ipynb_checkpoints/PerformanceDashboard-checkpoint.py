import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px
import requests
import bcrypt
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

 # sender_password = "huxi hyvf puig hlcq"   # Use an App Password for security

# Hide Streamlit's default menu and GitHub link
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)
# # Function to connect to MySQL
# def get_db_connection():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="Hemanadhan@2104",
#         database="employee_attendance"
#     )
# Function to connect to MySQL on Railway
# mysql://root:TWWfLfYyjMtJJsRpiErJXFWQsTxJRiKH@centerbeam.proxy.rlwy.net:44359/railway
# Function to connect to Railway MySQL
def get_db_connection():
    try:
        conn = pymysql.connect(
            host="centerbeam.proxy.rlwy.net",
            user="root",
            password="TWWfLfYyjMtJJsRpiErJXFWQsTxJRiKH",
            database="railway",
            port=44359,
            cursorclass=pymysql.cursors.DictCursor  # ✅ Correct way to get dictionary-like results
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None
# Function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Function to verify passwords
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
# Function to register a new employee
def register_employee(name, department, email, password):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:  # ✅ No 'dictionary=True' needed
                hashed_pw = hash_password(password)  # Hash password before storing
                query = "INSERT INTO employees (name, department, email, password) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (name, department, email, hashed_pw))
                conn.commit()
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            conn.close()

# Function to verify login
def verify_login(email, password):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM employees WHERE email=%s", (email,))
                user = cursor.fetchone()
                
                # Debugging logs
                if not user:
                    st.error("No user found with this email")
                    return None
                
                stored_hashed_password = user["password"]
                
                # Debugging logs
                st.write(f"Stored Hashed Password: {stored_hashed_password}")

                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                    return user
                else:
                    st.error("Invalid password")
                    return None
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            conn.close()
    return None
# Function to get user location & IP
def get_location():
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)  # Added timeout
        if response.status_code == 200:
            data = response.json()
            return data.get("city", "Unknown"), data.get("ip", "Unknown")
        else:
            return "Unknown", "Unknown"
    except requests.RequestException:
        return "Unknown", "Unknown"

# Example usage
city, ip = get_location()
print(f"City: {city}, IP: {ip}")

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



# Function to send an email notification
def send_email(to_email, employee_name, status, date, time, location, ip_address):
    sender_email = "hemanadhan2104@gmail.com"   # Replace with your email
    sender_password = "huxi hyvf puig hlcq"   # Use an App Password for security

    subject = "📢 Attendance Marked Successfully!"
    body = f"""
    Hello {employee_name},

    Your attendance has been recorded successfully.

    📅 Date: {date}
    ⏰ Time: {time}
    📍 Location: {location}
    🌍 IP Address: {ip_address}
    🏷️ Status: {status}

    Regards,  
    Attendance Management System  
    """

    # Email Setup
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Sending Email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("✅ Email Sent Successfully!")
    except Exception as e:
        print(f"❌ Error Sending Email: {e}")






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
    # if st.button("Submit Attendance"):
    #     mark_attendance(st.session_state.user['id'], status)
    #     st.success("✅ Attendance Recorded!")
    #     location, ip_address = get_location()
    #     st.rerun()  # Assume this function fetches location & IP
    # Modify Attendance Submission
    if st.button("Submit Attendance"):
        user_id = st.session_state.user['id']
        user_email = st.session_state.user['email']
        user_name = st.session_state.user['name']
        
        mark_attendance(user_id, status)  # Save to Database
        
        # Fetch User Location & IP
        location, ip_address = get_location()  # Assume this function fetches location & IP
        
        # Send Email Notification
        send_email(user_email, user_name, status,  str(datetime.today().date()),  # Correct way to get today's date
        str(datetime.now().time()),    # Correct way to get current time, 
                   location, ip_address)
        
        st.success("✅ Attendance Recorded & Email Sent!")
    


    # Fetch Logged-in User's Attendance Data
    # def fetch_user_attendance(user_id):
    #     conn = get_db_connection()
    #     query = "SELECT date, time, status, location, ip_address FROM attendance WHERE employee_id = %s ORDER BY date DESC"
    #     df = pd.read_sql(query, conn, params=[user_id])
    #     conn.close()
    #     return df
    def fetch_user_attendance(user_id):
        conn = get_db_connection()
        query = "SELECT date, time, status, location, ip_address FROM attendance WHERE employee_id = %s ORDER BY date DESC"
    
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id,))
            records = cursor.fetchall()  # Get data
            columns = [desc[0] for desc in cursor.description]  # Extract column names
        
        conn.close()
        
        # Convert SQL results into DataFrame
        df = pd.DataFrame(records, columns=columns)
        # df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S").dt.strftime("%I:%M %p")

        return df
    
    # Fetch and display attendance records
    df = fetch_user_attendance(st.session_state.get("user", {}).get("id"))
    
    # st.write("✅ Data Loaded:", df.shape)  # Debug DataFrame shape
    # st.dataframe(df)  # Display in Streamlit
    

    
    # Display Only the Logged-in User's Attendance Records
  
    # df = fetch_user_attendance(st.session_state.get('user', {}).get('id'))
    df = fetch_user_attendance(st.session_state.user['id'])
    st.write("### 📋 Your Attendance Records")
    st.write(f"🆔 Logged-in User ID: {st.session_state.get('user', {}).get('id')}")
    # if not df.empty:
    #     df = df.astype(str)  # ✅ Convert all data to string format
    #     st.write("✅ Data Successfully Loaded")
    # else:
    #     st.write("⚠️ No Data Found!")
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
