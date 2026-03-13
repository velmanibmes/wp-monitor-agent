import requests
import ssl
import socket
import smtplib
import os
from datetime import datetime, UTC

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

SITES = [
    "demo8.bmes.site",
    "demo7.bmes.site",
    "adhithya.bmes.site"
]

def send_email(subject, message):
    email_message = f"Subject: {subject}\n\n{message}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, EMAIL_TO, email_message)
        server.quit()
        print("Email sent")
    except Exception as e:
        print("Email failed:", e)


def check_uptime(site):
    try:
        r = requests.get(f"https://{site}", timeout=10)
        return r.status_code == 200
    except:
        return False


def check_ssl(site):
    try:
        import ssl
        from datetime import datetime, UTC
        import socket

        cert = ssl.get_server_certificate((site, 443))
        x509 = ssl._ssl._test_decode_cert(cert)

        expiry = datetime.strptime(
            x509['notAfter'],
            '%b %d %H:%M:%S %Y %Z'
        )

        days_left = (expiry - datetime.now(UTC)).days
        return days_left

    except ssl.SSLCertVerificationError:
        return 0

    except Exception as e:
        print("SSL check error:", site, e)
        return -1

report = []
report.append("WordPress Site Monitoring Report\n")
report.append(f"Generated: {datetime.now()}\n")
report.append("---------------------------------\n")

for site in SITES:

    uptime = check_uptime(site)
    ssl_days = check_ssl(site)

    status_line = f"{site}\n"

    if uptime:
        status_line += "Uptime: OK\n"
    else:
        status_line += "Uptime: DOWN\n"

    if ssl_days == 0:
        status_line += "SSL: EXPIRED\n"

    elif ssl_days > 0:
        status_line += f"SSL days left: {ssl_days}\n"

        if ssl_days < 15:
            status_line += "⚠ SSL expiring soon\n"

    else:
        status_line += "SSL check failed\n"

    status_line += "\n"

    report.append(status_line)

final_report = "".join(report)

send_email(
    "Daily Website Monitoring Report",
    final_report
)

print(final_report)
