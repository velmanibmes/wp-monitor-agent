import requests
import ssl
import socket
import smtplib
import os
from datetime import datetime, UTC

# -------- EMAIL CONFIG --------
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

# -------- WEBSITES TO MONITOR --------
SITES = [
    "demo8.bmes.site",
    "demo7.bmes.site",
    "adhithya.bmes.site"
]

# -------- EMAIL FUNCTION --------
def send_email(subject, message):

    email_message = f"Subject: {subject}\n\n{message}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, EMAIL_TO, email_message)
        server.quit()

        print("Email sent:", subject)

    except Exception as e:
        print("Email sending failed:", e)


# -------- UPTIME CHECK --------
def check_uptime(site):

    try:
        response = requests.get(f"https://{site}", timeout=10)

        if response.status_code == 200:
            return True
        else:
            return False

    except Exception as e:
        print("Uptime check failed:", site, e)
        return False


# -------- SSL CHECK --------
def check_ssl(site):

    try:
        ctx = ssl.create_default_context()

        with ctx.wrap_socket(socket.socket(), server_hostname=site) as s:
            s.connect((site, 443))

            cert = s.getpeercert()

            expiry = datetime.strptime(
                cert['notAfter'],
                '%b %d %H:%M:%S %Y %Z'
            )

            days_left = (expiry - datetime.now(UTC)).days

            return days_left

    except ssl.SSLCertVerificationError:

        print(f"{site} SSL certificate expired")

        return 0

    except Exception as e:

        print(f"SSL check failed for {site}: {e}")

        return -1


# -------- MAIN MONITOR --------
for site in SITES:

    print("Checking:", site)

    # -------- UPTIME --------
    uptime = check_uptime(site)

    if not uptime:

        send_email(
            f"🚨 Website Down: {site}",
            f"The website {site} is not reachable."
        )

    # -------- SSL --------
    ssl_days = check_ssl(site)

    if ssl_days == 0:

        send_email(
            f"⚠ SSL Expired: {site}",
            f"The SSL certificate for {site} has expired."
        )

    elif ssl_days > 0 and ssl_days < 15:

        send_email(
            f"⚠ SSL Expiry Warning: {site}",
            f"The SSL certificate for {site} will expire in {ssl_days} days."
        )

    print("SSL days remaining:", ssl_days)

print("Monitoring completed.")
