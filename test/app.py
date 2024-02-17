import hashlib
import sqlite3
import streamlit as st
import cv2
import numpy as np
#import streamlit_option_menu
from streamlit_option_menu import option_menu
import pandas as pd
import cv2

st.set_page_config(
    page_title="OREL - Assembly Line Monitoring System",
    page_icon=":camera:",
    layout="wide"
)

# SQLite connection
conn = sqlite3.connect('orel.db')
cursor = conn.cursor()

# Create a table to store user credentials if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
''')
conn.commit()
# Create a table to store user feedback if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        feedback_text TEXT
    )
''')
conn.commit()

# Create a table to store predictions if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        prediction_text TEXT,
        prediction TEXT
    )
''')
conn.commit()


# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to verify passwords
def verify_password(entered_password, hashed_password):
    return hashlib.sha256(entered_password.encode()).hexdigest() == hashed_password

def process_video(video_contents):
    # Your logic for processing the uploaded video goes here
    # Example: Applying some basic processing using OpenCV
    video_np = np.asarray(bytearray(video_contents), dtype=np.uint8)
    video = cv2.imdecode(video_np, 1)
    # Add your video processing steps here
    return video

def count_events(frame):
    # Your logic for counting events in a frame goes here
    # This is a placeholder; replace it with your actual event counting logic
    return 10  # Example: Returning a static count for demonstration purposes


# Streamlit UI

st.sidebar.title(":orange[Orange] :red[Electrics] ")
# Display the logo
logo = "orange-logo.png"  # Replace with the actual path to your logo file
st.sidebar.image(logo, width=100)  # Adjust the width as needed
st.sidebar.title(":blue[Event Detection System] :green[Assembly Line Monitoring] 📹 ")

# Check if the user is logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Login and Registration Section in the Sidebar
login_option = st.sidebar.radio("Select Option", ["Register", "Login"])


if login_option == "Register":
    # Registration
    new_username = st.sidebar.text_input("New Username")
    new_password = st.sidebar.text_input("New Password", type='password')

    if st.sidebar.button("Register"):
        hashed_password = hash_password(new_password)

        insert_query = "INSERT INTO users (username, password) VALUES (?, ?)"
        values = (new_username, hashed_password)

        cursor.execute(insert_query, values)
        conn.commit()

        st.sidebar.success("Registration successful. You can now log in.")
# Selector for Navigation
elif login_option == "Login":
    # Login
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type='password')

    if st.sidebar.button("Login"):
        select_query = "SELECT password FROM users WHERE username = ?"
        cursor.execute(select_query, (username,))
        result = cursor.fetchone()

        if result:
            hashed_password_from_db = result[0]

            if verify_password(password, hashed_password_from_db):
                st.sidebar.success("Logged in as {}".format(username))
                st.session_state.logged_in = True
            else:
                st.sidebar.error("Invalid password. Please try again.")
        else:
            st.sidebar.error("Username not found. Please register.")

# Display options only if the user is logged in
if st.session_state.logged_in:
    with st.sidebar:
        selected = option_menu(
        menu_title = "Main Menu",
        options = ["Home","Warehouse","Dashboard"],
        icons = ["house","gear","activity"],
        menu_icon = "cast",
        default_index = 0,
        #orientation = "horizontal",
    )
        
    if selected == "Home":
        st.title('Assembly Line Monitoring System')

        st.write("Welcome to the Assembly Line Monitoring System. This system is designed to monitor and analyze the assembly line in real-time. You can access the warehouse monitoring and analysis, and the dashboard for real-time metrics.")

    if selected == "Warehouse":
        st.title('Real-time monitoring and analysis')

        st.markdown(
        """
        <style>
        .full-width {
            width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True
        )
            
     
        # Use Streamlit columns for layout
        col1, col2 = st.columns(2)

        # Camera Access
        with col1:
            st.header("Camera Access")
            camera_feed_checkbox = st.checkbox("Show Camera Feed", key="camera_feed_checkbox_col1")
            if camera_feed_checkbox:
                video_capture = cv2.VideoCapture(0)  # Initialize video capture
                ret, frame = video_capture.read()
                st.image(frame, channels="BGR", use_column_width=True)

        # Video Upload
        with col2:
            st.header("Video Upload")
            upload_file_checkbox = st.checkbox("Upload from machine", key="upload_file_checkbox_col2")
            if upload_file_checkbox:
             uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi"])
             if uploaded_file is not None:
                video_contents = uploaded_file.read()
                st.video(video_contents)

                # Your code for processing the uploaded video goes here
                processed_video = process_video(video_contents)
                st.header("Video Preview")
                st.video(processed_video)

        # Real-time Metrics
    if selected == "Dashboard":
        st.title('Real-time analysis')
        # Your code for displaying real-time metrics goes here
        ##event_count = count_events(frame) 
         # Replace 'frame' with the actual frame from the video
        ##st.metric("Event Count", event_count)
        # Add more metrics as needed

else:
    st.warning("Please log in to access the system.")




def main():
   
    # Add footer
    st.markdown(
        """
        <style>
            .footer {
                text-align: center;
                padding: 10px;
                color: #888;
            }
        </style>
        """,
        unsafe_allow_html=True,
)
    
st.markdown('<p class="footer">© 2024 Assembly Line Monitoring System</p>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

