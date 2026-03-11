import requests
import ssl
import socket
from datetime import datetime
import smtplib
import os

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

SITES = [
    "https://demo8.bmes.site/",
    "https://demo7.bmes.site/",
    "https://www.adhithya.bmes.site/"
]

def send_email(subject, message):
    email_message = f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.sendmail(EMAIL_USER, EMAIL_TO, email_message)
    server.quit()


def check_uptime(site):
    try:
        r = requests.get(f"https://{site}", timeout=10)
        return r.status_code == 200
    except:
        return False


def check_ssl(site):
    ctx = ssl.create_default_context()
    with ctx.wrap_socket(socket.socket(), server_hostname=site) as s:
        s.connect((site, 443))
        cert = s.getpeercert()
        expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        days_left = (expiry - datetime.utcnow()).days
        return days_left


for site in SITES:

    # uptime check
    if not check_uptime(site):
        send_email(
            f"Website Down: {site}",
            f"Alert: {site} is not reachable."
        )

    # ssl check
    ssl_days = check_ssl(site)

    if ssl_days < 15:
        send_email(
            f"SSL Expiry Warning: {site}",
            f"SSL certificate for {site} will expire in {ssl_days} days."
        )
