import requests
import ssl
import socket
from datetime import datetime
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SITES = [
    "example1.com",
    "example2.com",
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def check_uptime(site):
    try:
        r = requests.get(f"https://{site}", timeout=5)
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
    if not check_uptime(site):
        send_telegram(f"🚨 {site} is DOWN!")

    ssl_days = check_ssl(site)
    if ssl_days < 15:
        send_telegram(f"⚠ {site} SSL expires in {ssl_days} days!")
