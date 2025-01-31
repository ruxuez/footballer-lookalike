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
menu = ["Webcam", "Picture"]
choice = st.sidebar.selectbox("Input type", menu)

# Sidebar setup for filters and input
st.sidebar.title("Filters")

# Country filter - single-select
country_options = [
    "Any", "Afghanistan", "Albania", "Algeria", "Angola", "Argentina", "Armenia", "Australia", 
    "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Benin", 
    "Bermuda", "Bhutan", "Bolivia", "Bonaire", "Bosnia-Herzegovina", "Brazil", "Brunei Darussalam", 
    "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde", 
    "Central African Republic", "Chad", "Chile", "China", "Chinese Taipei", "Colombia", "Comoros", 
    "Congo", "Congo DR", "Cookinseln", "Costa Rica", "Cote d'Ivoire", "Croatia", "Cuba", "Curacao", 
    "Cyprus", "Czech Republic", "Denmark", "Dominica", "Dominican Republic", "DR Congo", "Ecuador", 
    "Egypt", "El Salvador", "England", "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", 
    "Faroe Island", "Finland", "France", "French Guiana", "Gabon", "Georgia", "Germany", "Ghana", 
    "Greece", "Grenada", "Guadeloupe", "Guatemala", "Guernsey", "Guinea", "Guinea-Bissau", "Guyana", 
    "Haiti", "Honduras", "Hongkong", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", 
    "Isle of Man", "Israel", "Italy", "Jamaica", "Japan", "Jersey", "Jordan", "Kazakhstan", "Kenya", "Korea", 
    "Korea, South", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Liberia", "Liechtenstein", 
    "Lithuania", "Luxembourg", "Macedonia", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", 
    "Martinique", "Mauritania", "Mexico", "Moldova", "Montenegro", "Montserrat", "Morocco", "Mozambique", 
    "Myanmar", "Namibia", "Nepal", "Netherlands", "New Zealand", "Niger", "Nigeria", "Northern Ireland", 
    "North Macedonia", "Norway", "Oman", "Pakistan", "Palästina", "Palestine", "Panama", "Paraguay", "Peru", 
    "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Romania", "Russia", "Rwanda", "Saint-Martin", 
    "Samoa", "San Marino", "Saudi Arabia", "Scotland", "Scottland", "Senegal", "Serbia", "Sierra Leone", 
    "Singapore", "Slovakia", "Slovenia", "Somalia", "South", "South Africa", "Southern Sudan", "Spain", 
    "St. Kitts & Nevis", "St. Kitts &Nevis", "St. Lucia", "St. Vincent & Grenadinen", "Sudan", "Suriname", 
    "Sweden", "Switzerland", "Syria", "Tajikistan", "Tanzania", "Thailand", "The Gambia", "Togo", 
    "Trinidad and Tobago", "Tunisia", "Turkey", "Türkiye", "Uganda", "Ukraine", "United Arab Emirates", 
    "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "Wales", 
    "Yemen", "Zambia", "Zimbabwe"
]

# Competitions filter - single-select
competitions_options = [
    "Any",
    "AFC Challenge League",
    "AFC Champions League Elite",
    "AFC Champions League Two",
    "Bardzraguyn khumb",
    "Egyptian Premier League",
    "Oman Professional League",
    "Premier League",
    "Premier League 2",
    "Premier League Closing Round",
    "Premier League Opening Round",
    "Premyer Liqa",
    "Saudi Pro League",
    "Scottish Premiership",
    "Thai League",
    "UAE Pro League",
    "UEFA Champions League",
    "UEFA Champions League Qualifying",
    # Women competitions
    "1. deild kvenna",
    "1. Division",
    "1. Divisjon",
    "1. liga žen",
    "2. Bundesliga",
    "2. Frauen Bundesliga",
    "Adran Premier",
    "A-League Women",
    "A Lyga",
    "Besta deild kvenna",
    "Brasileirão Feminino",
    "Bundesliga",
    "Campeonato Nacional Feminino",
    "Chinese Women’s Football League",
    "Chinese Women’s Super League",
    "Damallsvenskan",
    "Deildin kvinnur",
    "Division 1 Mellersta",
    "Division 1 Norra",
    "Division 1 Södra",
    "Ekstraliga",
    "Elitettan",
    "Eredivisie Vrouwen",
    "Frauen Bundesliga",
    "Future League",
    "Hamburg Oberliga",
    "Hessenliga",
    "Kadın Futbol Süper Ligi",
    "Kansallinen Liiga",
    "Kvindeliga",
    "Liga MX Apertura",
    "Mittelrheinliga",
    "Molodezhnaya Liga Gruppa B",
    "Molodezhnaya Liga Gruppa C",
    "Molodezhnaya Liga Gruppa D",
    "Naiste Meistriliiga",
    "Naisten Ykkönen",
    "Nationalliga B",
    "Niederrheinliga",
    "Női NB I",
    "NWSL",
    "Oberliga Baden-Württemberg",
    "Oberliga Niedersachsen Ost",
    "Oberliga Niedersachsen West",
    "Oberliga Schleswig-Holstein",
    "Persha Liga A",
    "Persha Liga B",
    "Pirma Lyga",
    "Première Ligue",
    "Premijer Ženska Liga BiH",
    "Primera División Femenina",
    "Primera Federación",
    "Regionalliga Nord",
    "Regionalliga Nordost",
    "Regionalliga Süd",
    "Regionalliga Südwest",
    "Regionalliga West",
    "Seconde Ligue",
    "Segunda Federación Grupo Norte",
    "Segunda Federación Grupo Sur",
    "Serie A",
    "Serie B",
    "Super League",
    "Superliga",
    "SWPL 1",
    "SWPL 2",
    "Toppserien",
    "WE League",
    "Westfalenliga",
    "Wiener Frauen-Landesliga",
    "WK League",
    "Women’s Championship",
    "Women’s League",
    "Women’s Premier Division",
    "Women’s Premiership",
    "Women’s Super League",
]

# Gender filter - single-select
genders_options = ["Any", "Male", "Female"]

selected_countries = st.sidebar.selectbox("Select Countries", country_options)
selected_competitions = st.sidebar.selectbox("Select League", competitions_options)
selected_genders = st.sidebar.selectbox("Select Gender", genders_options)

# Sidebar form for email input and submission
with st.sidebar.form("my_form", clear_on_submit=True):
    input_email = st.text_input("Send your results! Enter your email address:")
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
                selected_competitions,
                selected_genders,
            )

            data_load_state.markdown(
                f"**{len(list(st.session_state.images_result))} Player Found**: ... Printing Information..."
            )
            for row in st.session_state.images_result:
                container = st.container()
                col1, col2, _, _ = container.columns([1, 2, 1.5, 1])
                with col1:
                    st.image(row["image_url"], use_column_width=True)
                with col2:
                    st.markdown(
                        f"""
                        <div style="padding: 5px; background-color: #f0f0f5; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);">
                            <h1 style="text-align: center; color: black; font-size: 30px; margin-top: 0px; margin-bottom: 0px;">{row["name"]}</h1>
                            <p style="text-align: center; color: black; font-size: 20px; margin-top: 0px; margin-bottom: 0px;"><b>{str(round(row["similarity"] * 100, 2))}% Similarity Match</b></p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 5px; margin-bottom: 0px;"><b>Date of Birth:</b> {row["date_of_birth"]} </p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 0px; margin-bottom: 0px;">
                                <b>Place of Birth:</b> {', '.join(filter(None, [row["city_of_birth"], row["country_of_birth"]]))}
                            </p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 0px; margin-bottom: 0px;">
                                <b>Height:</b> {('{:,.2f}m'.format(row["height"]/100) if row["height"] is not None else "No Info")} 
                            </p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 0px; margin-bottom: 0px;"><b>Position:</b> {row['position']} </p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 0px; margin-bottom: 0px;"><b>Current Club:</b> {row["club_name"]}</p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 0px; margin-bottom: 0px;"><b>Joined:</b> {row["joined_on"] or "No Info"}</p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 0px; margin-bottom: 0px;"><b>League:</b> {', '.join(row["competitions_names"]) or "No Info"}</p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 0px; margin-bottom: 0px;">
                                <b>Market Value: $</b>{('{:,.2f}'.format(row['market_value']) if row['market_value'] is not None else "No Info")} 
                            </p>
                        </div>
                        """, unsafe_allow_html=True,
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
                selected_competitions,
                selected_genders
            )

            data_load_state.markdown(
                f"**{len(list(st.session_state.images_result))} Player Found**: ... Printing Information..."
            )
            for row in st.session_state.images_result:
                container = st.container()
                col1, col2, _, _ = container.columns([1, 2, 1.5, 1])
                with col1:
                    st.image(row["image_url"], width=300, use_column_width=True)
                with col2:
                    st.markdown(
                        f"""
                        <div style="padding: 5px; background-color: #f0f0f5; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);">
                            <h1 style="text-align: center; color: black; font-size: 30px; margin-top: 0px; margin-bottom: 0px;">{row["name"]}</h1>
                            <p style="text-align: center; color: black; font-size: 20px; margin-top: 0px; margin-bottom: 0px;"><b>{str(round(row["similarity"] * 100, 2))}% Similarity Match</b></p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 5px; margin-bottom: 0px;"><b>Date of Birth:</b> {row["date_of_birth"]} </p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 0px; margin-bottom: 0px;">
                                <b>Place of Birth:</b> {', '.join(filter(None, [row["city_of_birth"], row["country_of_birth"]]))}
                            </p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 0px; margin-bottom: 0px;">
                                <b>Height:</b> {('{:,.2f}m'.format(row["height"]/100) if row["height"] is not None else "No Info")} 
                            </p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 0px; margin-bottom: 0px;"><b>Position:</b> {row['position']} </p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 0px; margin-bottom: 0px;"><b>Current Club:</b> {row["club_name"]}</p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 0px; margin-bottom: 0px;"><b>Joined:</b> {row["joined_on"] or "No Info"}</p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 0px; margin-bottom: 0px;"><b>League:</b> {', '.join(row["competitions_names"]) or "No Info"}</p>
                            <p style="text-align: center; color: black; font-size: 15px; margin-top: 0px; margin-bottom: 0px;">
                                <b>Market Value: $</b>{('{:,.2f}'.format(row['market_value']) if row['market_value'] is not None else "No Info")} 
                            </p>
                        </div>
                        """, unsafe_allow_html=True,
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
