import requests
import streamlit as st
from utils import (  # Custom utility functions for face recognition and image processing
    facenet,
    find_similar_faces,
)
from io import BytesIO
from PIL import Image
import threading
from send_email import *  # Module for sending email notifications

# Thread-safe container for storing images
lock = threading.Lock()
img_container = {"img": None, "original_image": None}

# Footer image for the application
footer_img = Image.open("source/EDB_banner.jpg").convert("RGB")


# Function to disable a session state
def disable():
    st.session_state.disabled = True


# Initialize session state for disabling the submit button
if "disabled" not in st.session_state:
    st.session_state.disabled = False

# Set the page layout to wide mode
st.set_page_config(layout="wide")

# Sidebar setup for branding and user interface
st.sidebar.image("source/edb_tagline_grey.png")
st.sidebar.markdown(
    """
    <div style="font-size: medium; font-style: italic">
    This is a  <b>EDB Look-alike Application</b> leveraging  <font color="green"> EDB Postgres MPP </font> and <font color="blue"> pgvector extension </font> for AI-powered Search.<br>
    
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar elements for user input and display
st.sidebar.text("")
menu = ["Home", "Picture", "Webcam"]
choice = st.sidebar.selectbox("Input type", menu)

# Sidebar setup for filters and input
st.sidebar.title("Filters")

# Country filter - single-select
country_options = [
    "Any", "Albania", "Algeria", "Angola", "Bolivia", "Bosnia-Herzegovina", "Burkina Faso",
    "Burundi", "Cameroon", "Cape Verde", "Comoros", "Cote d'Ivoire", "CSSR", 
    "DR Congo", "Estonia", "French Guiana", "Guernsey", "Guinea", "Guinea-Bissau",
    "Isle of Man", "Jugoslawien (SFR)", "Liberia", "Macedonia", "Madagascar", 
    "Mali", "Malta", "Martinique", "Niger", "Northern Ireland", "Palestine", 
    "Paraguay", "Romania", "Rwanda", "Serbia and Montenegro", "Sierra Leone", 
    "Slovakia", "The Gambia", "Togo", "UdSSR", "Yugoslavia (Republic)", "Zaire"
]
selected_countries = st.sidebar.selectbox("Select Countries", country_options)

# Sidebar form for email input and submission
with st.sidebar.form("my_form", clear_on_submit=True):
    input_email = st.text_input("Email")
    submitted = st.form_submit_button("Send", disabled=st.session_state.disabled)


# Main application logic based on input type
# Home Page logic
if choice == "Home":
    st.title("Celebrity Look-Alike Finder: AI-Powered Footballer Matchmaking with PostgreSQL MPP and pgvector")
    st.markdown(
        """
        ## About this application
        This application leverages AI technology to identify Footballer look-alikes. 
        It uses facial recognition to match images uploaded by users with footballer faces.
        It integrates **EDB Postgres MPP** and the **pgvector** extension for AI-powered search functionality.
        
        ### Features:
        - Upload a photo for celebrity look-alike matching.
        - Take a live photo using your webcam.
        - Browse streaming video to see look-alike matches in real-time.
        """
    )
    st.image(footer_img, use_column_width=True)
elif choice == "Picture":
    # Rest of the code remains the same, just now you will need to filter or apply these selections

    st.title("Face Recognition App")

    c1, c2 = st.columns([2, 2])

    # File uploader for image input
    image_search_url = c1.text_input("Enter your Face url:", key="image")
    uploaded_images = c1.file_uploader(
        "Upload the image", type=["jpg", "png", "jpeg"]
    )
    search_button = c1.button("Search")

    # State variables
    if "img_search" not in st.session_state:
        st.session_state.img_search = None
    if "images_result" not in st.session_state:
        st.session_state.images_result = []

    if search_button:
        if uploaded_images is not None:
            st.session_state.img_search = Image.open(uploaded_images)
        else:
            response = requests.get(image_search_url)
            st.session_state.img_search = Image.open(BytesIO(response.content))

        if st.session_state.img_search:
            c2.image(st.session_state.img_search, width=200, caption="Face you would like to find")

            st.subheader("Results")
            data_load_state = st.empty()
            data_load_state.markdown("Searching results...")
            # Find and display similar celebrity faces
            st.session_state.images_result = find_similar_faces(
                facenet,
                st.session_state.img_search,
                selected_countries,
            )

            data_load_state.markdown(
                f"**{len(list(st.session_state.images_result))} Player Found**: ... Printing Information..."
            )
            for row in st.session_state.images_result:
                container = st.container()
                col1, col2 = container.columns([2,3])
                with col1:
                    st.image(row["image_url"], width=300)
                with col2:
                    st.markdown(
                    """<h4 style='text-align: center; color: black;'>{0}</h4>
                        <p style='text-align: center; color: black;'><b>Similarity:</b> {1} </p>
                        <p style='text-align: left; color: black;'><b>Date of Birth:</b> {2} </p>
                        <p style='text-align: left; color: black;'><b>Place of Birth:</b> {3}, {4}</p>
                        <p style='text-align: left; color: black;'><b>Position:</b> {5} </p>
                        <p style='text-align: left; color: black;'><b>Club:</b> {6} <b>joined on</b> {7} <b>signed from</b> {8} <b>until</b> {9}</p>
                        <p style='text-align: left; color: black;'><b>Status:</b> {10} </p>
                        <p style='text-align: left; color: black;'><b>Market Value: $</b>{11} </p>
                        <p style='text-align: left; color: black;'><b>Url:</b> {12} </p>
                    """.format(
                                row['name'],                                 
                                str(round(row["similarity"] * 100, 2)),
                                row["date_of_birth"], 
                                row["city_of_birth"], row["country_of_birth"],
                                row['position'],
                                row["club_name"], row["joined_on"], row["signed_from"] if row['signed_from'] else "No Info", row["contract"],
                                row['status'] if row['status'] else "No Info",
                                '{:,.2f}'.format(row['market_value']) if row['market_value'] else "No Info",
                                row['url'] if row['url'] else "No Info",
                            ),
                        unsafe_allow_html=True)
            data_load_state.markdown(f"**{len(list(st.session_state.images_result))} Player Found**")
        else:
            st.info("Please upload an image")

    
    if submitted:
        try:
            send_email_img(
                input_email,
                st.session_state.img_search,
                st.session_state.images_result[0]
            )
            st.info("Email successfully sent!")
        except:
            st.error("Failed to send Email", icon="🚨")


elif choice == "Webcam":
    st.title("Face Recognition App")
    st.write("Please allow access to your webcam and take a picture.")

    # Camera input for real-time face detection
    c1, c2 = st.columns(2)
    picture = c1.camera_input("Take a picture")

    # State variable
    if "img_search" not in st.session_state:
        st.session_state.img_search = None
    if "images_result" not in st.session_state:
        st.session_state.images_result = []

    if picture:
        # Process webcam image and find matches

        st.session_state.img_search = Image.open(picture)

        if st.session_state.img_search:

            st.subheader("Results")
            data_load_state = st.empty()
            data_load_state.markdown("Searching results...")
            # Find and display similar celebrity faces
            st.session_state.images_result = find_similar_faces(
                facenet,
                st.session_state.img_search,
                selected_countries,
            )

            data_load_state.markdown(
                f"**{len(list(st.session_state.images_result))} Player Found**: ... Printing Information..."
            )
            for row in st.session_state.images_result:
                container = st.container()
                col1, col2 = container.columns([2,3])
                with col1:
                    st.image(row["image_url"], width=300)
                with col2:
                    st.markdown(
                    """<h4 style='text-align: center; color: black;'>{0}</h4>
                        <p style='text-align: center; color: black;'><b>Similarity:</b> {1} </p>
                        <p style='text-align: left; color: black;'><b>Date of Birth:</b> {2} </p>
                        <p style='text-align: left; color: black;'><b>Place of Birth:</b> {3}, {4}</p>
                        <p style='text-align: left; color: black;'><b>Position:</b> {5} </p>
                        <p style='text-align: left; color: black;'><b>Club:</b> {6} <b>joined on</b> {7} <b>signed from</b> {8} <b>until</b> {9}</p>
                        <p style='text-align: left; color: black;'><b>Status:</b> {10} </p>
                        <p style='text-align: left; color: black;'><b>Market Value: $</b>{11} </p>
                        <p style='text-align: left; color: black;'><b>Url:</b> {12} </p>
                    """.format(
                                row['name'],                                 
                                str(round(row["similarity"] * 100, 2)),
                                row["date_of_birth"], 
                                row["city_of_birth"], row["country_of_birth"],
                                row['position'],
                                row["club_name"], row["joined_on"], row["signed_from"] if row['signed_from'] else "No Info", row["contract"],
                                row['status'] if row['status'] else "No Info",
                                '{:,.2f}'.format(row['market_value']) if row['market_value'] else "No Info",
                                row['url'] if row['url'] else "No Info",
                            ),
                        unsafe_allow_html=True)
            data_load_state.markdown(f"**{len(list(st.session_state.images_result))} Player Found**")
        else:
            st.info("Please upload an image")

    
    if submitted:
        try:
            send_email_img(
                input_email,
                st.session_state.img_search,
                st.session_state.images_result[0]
            )
            st.info("Email successfully sent!")
        except:
            st.error("Failed to send Email", icon="🚨")