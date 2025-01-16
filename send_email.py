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
        img_search_path = (
            f"./images/search_{to}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        )
        player_img_path = (
            f"./images/player_{to}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        )

        img_search.save(img_search_path)
        player_details["image"].save(player_img_path)

        msgRoot = MIMEMultipart("related")
        msgRoot["Subject"] = "Football player look-alike inside…"
        msgRoot["From"] = st.secrets["email"]["email_from"]
        msgRoot["To"] = to

        # Create the body of the message.
        html = f"""\
        <div style="max-width: 900px; font-family: Arial, sans-serif;">
            <a href="https://www.enterprisedb.com/workload/postgres-for-ai">
                <img src="cid:image3" alt="EDB Postgres AI Logo" width="150" style="display: block; margin: 0 auto;">
            </a>
            <br><br>
            <h2 style="text-align: center;">Here’s your football player lookalike:</h2>

            <!-- Centered side-by-side images using a table -->
            <table style="margin: 0 auto; text-align: center; width: 100%; max-width: 600px;">
                <tr>
                    <td style="text-align: center; vertical-align: top; padding: 10px;">
                        <h4>Your Search Image:</h4>
                        <img src="cid:image1" alt="Search Image" style="height: 200px; width: auto; border-radius: 10px;">
                    </td>
                    <td style="text-align: center; vertical-align: top; padding: 10px;">
                        <h4>Matched Footballer:</h4>
                        <img src="cid:image2" alt="Football Player" style="height: 200px; width: auto; border-radius: 10px;">
                    </td>
                </tr>
            </table>

            <!-- Player details -->
            <div style="padding: 20px; background-color: #f0f0f5; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);">
                <h1 style="text-align: center; color: black;">{player_details["name"]}</h1>
                <h3 style="text-align: center; color: black; margin-bottom: 0px;">{str(round(player_details["similarity"] * 100, 2))}%</h3>
                <h4 style="text-align: center; color: black; margin-top: 0px; margin-bottom: 20px;"><b>Similarity Match</b></h4>
                <p style="text-align: center; color: black; margin-top: 30px;"><b>Date of Birth:</b> {player_details["date_of_birth"]}</p>
                <p style="text-align: center; color: black;"><b>Place of Birth:</b> {', '.join(filter(None, [player_details["city_of_birth"], player_details["country_of_birth"]]))}</p>
                <p style="text-align: center; color: black;"><b>Height:</b> {('{:,.2f}m'.format(player_details["height"] / 100) if player_details["height"] is not None else "No Info")}</p>
                <p style="text-align: center; color: black;"><b>Position:</b> {player_details['position']}</p>
                <p style="text-align: center; color: black;"><b>Current Club:</b> {player_details["club_name"]}</p>
                <p style="text-align: center; color: black;"><b>Joined:</b> {player_details["joined_on"] or "No Info"}</p>
                <p style="text-align: center; color: black;"><b>League:</b> {', '.join(player_details["competitions_names"]) or "No Info"}</p>
                <p style="text-align: center; color: black;"><b>Market Value: $</b>{('{:,.2f}'.format(player_details['market_value']) if player_details['market_value'] is not None else "No Info")}</p>
            </div>

            <!-- Footer text -->
            <div style="margin-top: 20px;">
                <p>This is just a glimpse of what our EDB Postgres AI platform can do—delivering powerful, AI-driven insights and applications at scale.</p>
                <p>Discover how EDB can transform your data into actionable intelligence while maintaining sovereignty and security. Learn more about EDB Postgres AI and explore the technology behind the game <a href="https://www.enterprisedb.com/workload/postgres-for-ai" style="color: #007BFF;">here</a>.</p>
            </div>

            <footer style="text-align: center; font-size: 10px; color: gray; margin-top: 20px;">
                <img src="cid:image3" alt="EDB Logo" width="150">
                <p>Discover the power of AI with EDB Postgres!</p>
                <p>Copyright © 2025 EDB, Inc.</p>
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
        msgLogo.add_header(
            "Content-Disposition", "inline", filename="source/edb_tagline_grey.png"
        )
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
