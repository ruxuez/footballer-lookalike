#! /usr/bin/python

import smtplib
import ssl
from datetime import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import streamlit as st

# Setup port number and servr name

smtp_port = st.secrets["email"]["smtp_port"]
smtp_server = st.secrets["email"]["smtp_server"]

pswd = st.secrets["email"]["password"]


def send_email_img(to, img_search, player_details):
    try:
        # Save the images locally for attachment
        img_search_path = f"./images/search_{to}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        player_img_path = f"./images/player_{to}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"

        img_search.save(img_search_path)
        player_details["image"].save(player_img_path)

        msgRoot = MIMEMultipart("related")
        msgRoot["Subject"] = "EDB Players Lookalike Discovery with EDB Postgres AI 🌟"
        msgRoot["From"] = st.secrets["email"]["email_from"]
        msgRoot["To"] = to

        # Create the body of the message.
        html = f"""\
        <div style="max-width: 900px; font-family: Arial, sans-serif;">
            <a href="https://www.enterprisedb.com/workload/postgres-for-ai">
                <img src="cid:image3" alt="EDB Postgres AI Logo" width="150" style="display: block; margin: 0 auto;">
            </a>
            <br><br>
            <h2 style="text-align: center;">Discover Your Football Player Lookalike!</h2>
            <p style="text-align: center; font-size: 16px;">We found a match for your photo! Here's your football player lookalike:</p>
            
            <div style="text-align: center; margin: 20px 0;">
                <h3 style="color: #007BFF;">{player_details["name"]}</h3>
                <img src="cid:image2" alt="Football Player" width="200" style="border-radius: 10px;">
            </div>
            
            <div style="margin: 20px;">
                <h4>Player Details:</h4>
                <ul style="list-style: none; padding: 0;">
                    <li><b>Date of Birth:</b> {player_details["date_of_birth"]}</li>
                    <li><b>Place of Birth:</b> {player_details["city_of_birth"]}, {player_details["country_of_birth"]}</li>
                    <li><b>Height:</b> {'{:,.2f}'.format(player_details["height"]/100)}m</li>
                    <li><b>Position:</b> {player_details["position"]}</li>
                    <li><b>Foot:</b> {player_details["foot"]}</li>
                    <li><b>Current club:</b> {player_details["club_name"]}</li>
                    <li><b>Joined On:</b> {player_details["joined_on"]}</li>
                    <li><b>Contract Expires:</b> {player_details["contract"]}</li>
                    <li><b>Market Value:</b> ${'{:,.2f}'.format(player_details['market_value']) or "No Info"}</li>
                    <li><b>More Info:</b> <a href="{player_details['url']}">{player_details['url'] or "No Info"}</a></li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <h4>Your Search Image:</h4>
                <img src="cid:image1" alt="Search Image" width="200" style="border-radius: 10px;">
            </div>
            
            <footer style="text-align: center; font-size: 10px; color: gray; margin-top: 20px;">
                <img src="cid:image3" alt="EDB Logo" width="150">
                <p>Discover the power of AI with EDB Postgres!</p>
                <p>Copyright © 2024 EDB, Inc.</p>
            </footer>
        </div>
        """

        msgHtml = MIMEText(html, "html")
        msgRoot.attach(msgHtml)

        # Attach images to email
        with open(img_search_path, "rb") as f:
            msgImg1 = MIMEImage(f.read())
        msgImg1.add_header("Content-ID", "<image1>")
        msgImg1.add_header("Content-Disposition", "inline", filename=img_search_path)
        msgRoot.attach(msgImg1)

        with open(player_img_path, "rb") as f:
            msgImg2 = MIMEImage(f.read())
        msgImg2.add_header("Content-ID", "<image2>")
        msgImg2.add_header("Content-Disposition", "inline", filename=player_img_path)
        msgRoot.attach(msgImg2)

        # Attach EDB logo
        with open("source/edb_tagline_grey.png", "rb") as f:
            msgLogo = MIMEImage(f.read())
        msgLogo.add_header("Content-ID", "<image3>")
        msgLogo.add_header("Content-Disposition", "inline", filename="source/edb_tagline_grey.png")
        msgRoot.attach(msgLogo)

        # Send email
        simple_email_context = ssl.create_default_context()
        smtp_server = st.secrets["email"]["smtp_server"]
        smtp_port = st.secrets["email"]["smtp_port"]
        email_from = st.secrets["email"]["email_from"]
        email_password = st.secrets["email"]["password"]

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=simple_email_context)
            server.login(email_from, email_password)
            server.sendmail(email_from, to, msgRoot.as_string())

        print(f"Email successfully sent to - {to}")

    except Exception as e:
        print(f"Failed to send email: {e}")