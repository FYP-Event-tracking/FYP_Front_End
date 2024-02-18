import hashlib
import sqlite3
import streamlit as st
import cv2
import numpy as np
from streamlit_option_menu import option_menu
import supervision as sv
from ultralytics import YOLO
import os
import glob

def model_run(SOURCE_VIDEO_PATH, TARGET_VIDEO_PATH):
    model = YOLO(os.path.relpath("best.pt"))
    model.fuse()

    # initiate polygon zone
    polygon = np.array([
        [50,1000],
        [1050, 1000],
        [1050, 300],
        [50, 300]
    ])

    list_of_dict = []
    in_count = 0
    out_count = 0
    in_check = False
    out_check = False

    import matplotlib.pyplot as plt
    from PIL import Image

    # create VideoInfo instance
    video_info = sv.VideoInfo.from_video_path(SOURCE_VIDEO_PATH)

    # create frame generator
    generator = sv.video.get_video_frames_generator(SOURCE_VIDEO_PATH)

    # create LineCounter instance
    # line_counter = sv.LineZone(start=LINE_START, end=LINE_END)

    # create ZoneCounter instance
    zone = sv.PolygonZone(polygon=polygon, frame_resolution_wh=video_info.resolution_wh)

    # create ZoneCounter instance
    zone_2 = sv.PolygonZone(polygon=polygon, frame_resolution_wh=video_info.resolution_wh)

    # create instance of BoxAnnotator, LineCounterAnnotator and ZoneCounterAnnotator
    # line_annotator = sv.LineZoneAnnotator(
    #    thickness=4, 
    #    text_thickness=4, 
    #    text_scale=2
    #)

    box_annotator = sv.BoxAnnotator(
        thickness=4,
        text_thickness=4,
        text_scale=2
    )

    zone_annotator = sv.PolygonZoneAnnotator(
        zone=zone, 
        color=sv.Color.white(), 
        thickness=6, 
        text_thickness=6, 
        text_scale=2
    )

    zone_annotator_2 = sv.PolygonZoneAnnotator(
        zone=zone_2, 
        color=sv.Color.blue(), 
        thickness=6, 
        text_thickness=6, 
        text_scale=2
    )

    # open target video file
    with sv.VideoSink(TARGET_VIDEO_PATH, video_info) as sink:  
        for result in model.track(source=SOURCE_VIDEO_PATH, tracker = 'bytetrack.yaml', show=False, stream=True, agnostic_nms=True, persist=True ):

            frame = result.orig_img
            detections = sv.Detections.from_yolov8(result)

            if result.boxes.id is not None:
                detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)
            
            labels = [
                f"{tracker_id} {model.model.names[class_id]} {confidence:0.2f}"
                for _, confidence, class_id, tracker_id
                in detections
            ]

            frame = box_annotator.annotate(
                scene=frame, 
                detections=detections,
                labels=labels
            )
            
            detections = detections[detections.class_id == 2]
            zone.trigger(detections=detections)
            
            if (any(detections.class_id == 2) and  any(zone.trigger(detections=detections)) and in_check == False):
                in_count = in_count + 1
                print(in_count)
                in_check = True
                out_check = False
                #dict_entry = {"class_id": detections.class_id, "track_id": detections.tracker_id}
                #list_of_dict.append(dict_entry)
            
            detections = sv.Detections.from_yolov8(result)
            detections = detections[detections.class_id == 3]
            zone_2.trigger(detections=detections)
            
            if (any(detections.class_id == 3) and  any(zone_2.trigger(detections=detections)) and out_check == False):
                out_count = out_count + 1
                print(out_count)
                out_check = True
                in_check = False
                #dict_entry = {"class_id": detections.class_id, "track_id": detections.tracker_id}
                #list_of_dict.append(dict_entry)
            
            #line_counter.trigger(detections=detections)
            #line_annotator.annotate(frame=frame, line_counter=line_counter)
            frame = zone_annotator.annotate(scene=frame)
            frame = zone_annotator_2.annotate(scene=frame)
            
            #plt.imshow(frame)
            #plt.show()
            #print(detections.class_id)
            #print(detections.tracker_id)
            sink.write_frame(frame)
    
    print(in_count, out_count)
    return in_count, out_count  

def save_uploadedfile(uploadedfile):
    with open(os.path.join("tempDir",uploadedfile.name),"wb") as f:
        f.write(uploadedfile.getbuffer())
    return st.success("Saved File:{} to tempDir".format(uploadedfile.name))

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
                # st.title("Webcam Live Feed")
                # run = st.checkbox('Run')
                FRAME_WINDOW = st.image([])
                camera = cv2.VideoCapture(0)

                while camera_feed_checkbox:
                    _, frame = camera.read()
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    FRAME_WINDOW.image(frame)
                else:
                    st.write('Stopped')
                # video_capture = cv2.VideoCapture(0)  # Initialize video capture
                # ret, frame = video_capture.read()
                # st.image(frame, channels="BGR", use_column_width=True)      
        # Video Upload
        with col2:
            st.header("Video Upload")
            upload_file_checkbox = st.checkbox("Upload from machine", key="upload_file_checkbox_col2")
            if upload_file_checkbox:
             files = glob.glob('tempDir/*')
             for f in files:
                    os.remove(f)
             uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi"])
             if uploaded_file is not None:
                save_uploadedfile(uploaded_file)
                with st.spinner('Processing...'):
                    in_c , out_c =model_run(f'tempDir/{uploaded_file.name}',f'tempDir/output{uploaded_file.name}')
                st.success('Processing complete!')
                output_file = f'tempDir/output{uploaded_file.name}'
                print(output_file)
                st.header("Video Preview")
                st.video(output_file, format="video/mp4", start_time=0)
                st.subheader(f"Total Count : {min(in_c-2, out_c-2)}")

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
