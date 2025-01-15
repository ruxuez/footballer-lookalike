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
st.set_page_config(page_title="Footballer Finder by EDB", page_icon="⚽", layout="wide")
# Sidebar setup for branding and user interface
st.sidebar.image("source/edb_tagline_grey.png")

# Sidebar elements for user input and display
st.sidebar.text("")
menu = ["Home", "Picture", "Webcam"]
choice = st.sidebar.selectbox("Input type", menu)

# Sidebar setup for filters and input
st.sidebar.title("Filters")

# Country filter - single-select
country_options = [
    "Any",
    "Afghanistan",
    "Albania",
    "Algeria",
    "Angola",
    "Argentina",
    "Armenia",
    "Australia",
    "Austria",
    "Azerbaijan",
    "Bahrain",
    "Bangladesh",
    "Belarus",
    "Belgium",
    "Benin",
    "Bermuda",
    "Bhutan",
    "Bolivia",
    "Bosnia-Herzegovina",
    "Brazil",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Cambodia",
    "Cameroon",
    "Canada",
    "Cape Verde",
    "Chile",
    "China",
    "Chinese Taipei",
    "Colombia",
    "Comoros",
    "Costa Rica",
    "Cote d'Ivoire",
    "Croatia",
    "CSSR",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Dominican Republic",
    "DR Congo",
    "Ecuador",
    "Egypt",
    "England",
    "Estonia",
    "Ethiopia",
    "Finland",
    "France",
    "French Guiana",
    "Gabon",
    "Georgia",
    "Germany",
    "Ghana",
    "Greece",
    "Guernsey",
    "Guinea",
    "Guinea-Bissau",
    "Haiti",
    "Honduras",
    "Hongkong",
    "Hungary",
    "Iceland",
    "India",
    "Indonesia",
    "Iran",
    "Iraq",
    "Ireland",
    "Isle of Man",
    "Israel",
    "Italy",
    "Jamaica",
    "Japan",
    "Jordan",
    "Jugoslawien (SFR)",
    "Kazakhstan",
    "Kenya",
    "Korea, South",
    "Kuwait",
    "Kyrgyzstan",
    "Laos",
    "Latvia",
    "Lebanon",
    "Liberia",
    "Lithuania",
    "Luxembourg",
    "Macedonia",
    "Madagascar",
    "Malaysia",
    "Maldives",
    "Mali",
    "Malta",
    "Martinique",
    "Mauritania",
    "Mexico",
    "Moldova",
    "Mongolia",
    "Morocco",
    "Mozambique",
    "Myanmar",
    "Netherlands",
    "New Zealand",
    "Niger",
    "Nigeria",
    "Northern Ireland",
    "Norway",
    "Oman",
    "Palestine",
    "Panama",
    "Paraguay",
    "Philippines",
    "Poland",
    "Portugal",
    "Qatar",
    "Romania",
    "Russia",
    "Rwanda",
    "Saudi Arabia",
    "Scotland",
    "Senegal",
    "Serbia and Montenegro",
    "Sierra Leone",
    "Singapore",
    "Slovakia",
    "South Africa",
    "Spain",
    "Sudan",
    "Sweden",
    "Switzerland",
    "Syria",
    "Tajikistan",
    "Tanzania",
    "Thailand",
    "The Gambia",
    "Togo",
    "Trinidad and Tobago",
    "Tunisia",
    "Türkiye",
    "UdSSR",
    "Uganda",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom",
    "United States",
    "Uruguay",
    "Uzbekistan",
    "Vanuatu",
    "Venezuela",
    "Vietnam",
    "Wales",
    "Yugoslavia (Republic)",
    "Zaire",
    "Zambia",
    "Zimbabwe",
]

selected_countries = st.sidebar.selectbox("Select Countries", country_options)

# Sidebar form for email input and submission
with st.sidebar.form("my_form", clear_on_submit=True):
    input_email = st.text_input("Email")
    submitted = st.form_submit_button("Send", disabled=st.session_state.disabled)


# Main application logic based on input type
# Home Page logic
if choice == "Home":
    st.title(
        "Celebrity Look-Alike Finder: AI-Powered Footballer Matchmaking with PostgreSQL MPP and pgvector"
    )
    st.markdown(
        """
        ## About this application
        This application leverages AI technology to identify Footballer look-alikes. 
        It uses facial recognition to match images uploaded by users with footballer faces.
        It integrates **EDB Postgres MPP** and the **pgvector** extension for AI-powered search functionality.
        
        ### Features:
        - Upload a photo for celebrity look-alike matching.
        - Take a live photo using your webcam.
        """
    )
    st.image(footer_img, use_column_width=True)
elif choice == "Picture":
    # Rest of the code remains the same, just now you will need to filter or apply these selections

    st.title("EDB Look-alike Application")
    st.write(
        """
    <div style="font-size: 25px;">
    <b>Leveraging EDB Postgres MPP and pgvector extension for AI-powered Search.</b>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.text("")

    c1, c2 = st.columns([2, 2])

    # File uploader for image input
    image_search_url = c1.text_input("Enter your Face url:", key="image")
    uploaded_images = c1.file_uploader("Upload the image", type=["jpg", "png", "jpeg"])
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
            c2.image(
                st.session_state.img_search,
                width=200,
                caption="Face you would like to find",
            )

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
                col1, col2 = container.columns([2, 3])
                with col1:
                    st.image(row["image_url"], width=400)
                with col2:
                    st.markdown(
                        f"""<h4 style='text-align: center; color: black;'>{row["name"]}</h4>
                        <p style='text-align: center; color: black;'><b>Similarity:</b> {str(round(row["similarity"] * 100, 2))} </p>
                        <p style='text-align: left; color: black;'><b>Date of Birth:</b> {row["date_of_birth"]} </p>
                        <p style='text-align: left; color: black;'><b>Place of Birth:</b> {row["city_of_birth"]}, {row["country_of_birth"]}</p>
                        <p style='text-align: left; color: black;'><b>Height:</b> {'{:,.2f}m'.format(row["height"]/100) or "No Info"} </p>
                        <p style='text-align: left; color: black;'><b>Position:</b> {row['position']} </p>
                        <p style='text-align: left; color: black;'><b>Foot:</b> {row['foot']} </p>
                        <p style='text-align: left; color: black;'><b>Current Club:</b> {row["club_name"]}</p>
                        <p style='text-align: left; color: black;'><b>Joined:</b> {row["joined_on"] or "No Info"}</p>
                        <p style='text-align: left; color: black;'><b>Contract expires:</b> {row["contract"] or "No Info"}</p>
                        <p style='text-align: left; color: black;'><b>Market Value: $</b>{'{:,.2f}'.format(row['market_value']) or "No Info"} </p>
                        <p style='text-align: left; color: black;'><b>More Info: </b>{f'<a href="{row["url"]}" target="_blank" style="color: blue; text-decoration: none;">{row["url"]}</a>' if row["url"] else "No Info"}
                    """,
                        unsafe_allow_html=True,
                    )
            data_load_state.markdown(
                f"**{len(list(st.session_state.images_result))} Player Found**"
            )
        else:
            st.info("Please upload an image")

    if submitted:
        try:
            send_email_img(
                input_email,
                st.session_state.img_search,
                st.session_state.images_result[0],
            )
            st.info("Email successfully sent!")
        except:
            st.error("Failed to send Email", icon="🚨")


elif choice == "Webcam":
    st.title("EDB Look-alike Application")
    st.write(
        """
    <div style="font-size: 25px;">
    <b>Leveraging EDB Postgres MPP and pgvector extension for AI-powered Search.</b>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.text("")
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
                col1, col2 = container.columns([2, 3])
                with col1:
                    st.image(row["image_url"], width=300)
                with col2:
                    st.markdown(
                        f"""<h4 style='text-align: center; color: black;'>{row["name"]}</h4>
                        <p style='text-align: center; color: black;'><b>Similarity:</b> {str(round(row["similarity"] * 100, 2))} </p>
                        <p style='text-align: left; color: black;'><b>Date of Birth:</b> {row["date_of_birth"]} </p>
                        <p style='text-align: left; color: black;'><b>Place of Birth:</b> {row["city_of_birth"]}, {row["country_of_birth"]}</p>
                        <p style='text-align: left; color: black;'><b>Height:</b> {'{:,.2f}m'.format(row["height"]/100) or "No Info"} </p>
                        <p style='text-align: left; color: black;'><b>Position:</b> {row['position']} </p>
                        <p style='text-align: left; color: black;'><b>Foot:</b> {row['foot']} </p>
                        <p style='text-align: left; color: black;'><b>Current Club:</b> {row["club_name"]}</p>
                        <p style='text-align: left; color: black;'><b>Joined:</b> {row["joined_on"] or "No Info"}</p>
                        <p style='text-align: left; color: black;'><b>Contract expires:</b> {row["contract"] or "No Info"}</p>
                        <p style='text-align: left; color: black;'><b>Market Value: $</b>{'{:,.2f}'.format(row['market_value']) or "No Info"} </p>
                        <p style='text-align: left; color: black;'><b>More Info: </b>{f'<a href="{row["url"]}" target="_blank" style="color: blue; text-decoration: none;">{row["url"]}</a>' if row["url"] else "No Info"}
 </p>
                    """,
                        unsafe_allow_html=True,
                    )
            data_load_state.markdown(
                f"**{len(list(st.session_state.images_result))} Player Found**"
            )
        else:
            st.info("Please upload an image")

    if submitted:
        try:
            send_email_img(
                input_email,
                st.session_state.img_search,
                st.session_state.images_result[0],
            )
            st.info("Email successfully sent!")
        except:
            st.error("Failed to send Email", icon="🚨")
