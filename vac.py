import requests
import json
import datetime
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def vac_data(district, date_):
    rs = []
    url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district}&date={date_}"
    data = requests.get(url).json()
    for center in data['centers']:
        if center["fee_type"] == "Paid":
            for session in center["sessions"]:
                if session["available_capacity"] > 0 and session["min_age_limit"] == 18:
                    session['name'] = center['name']
                    session['address'] = center['address']
                    session['district_name'] = center['district_name']
                    rs.append(session)
    return rs

def send_email(send, recv ,pass_, body):
    sender_email = send
    receiver_email = recv
    password = pass_
    message = MIMEMultipart("alternative")
    message["Subject"] = "Vaccine Slot Booking Alert!!!"
    message["From"] = sender_email
    message["To"] = receiver_email
    part2 = MIMEText(body, "html")
    message.attach(part2)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
        sender_email, receiver_email, message.as_string()
    )
    return "mail Sent"
def main():
    with open("config.json", "r") as cp:
        config = json.load(cp)

    dist1, dist2 = config["dist_code"]
    rs1 = vac_data(dist1,datetime.date.today().strftime("%d-%m-%Y"))
    rs2 = vac_data(dist2,datetime.date.today().strftime("%d-%m-%Y"))
    rs = rs1 + rs2
    if len(rs) > 0:
        table = ""
        for session in rs:
            table += "<tr>"
            table += f"<td>{session['date']}</td>"
            table += f"<td>{session['name']}</td>"
            table += f"<td>{session['address']}</td>"
            table += f"<td>{session['district_name']}</td>"
            table += f"<td>{session['available_capacity']}</td>"
            table += "</tr>"
        with open("tb.html",'r') as fp:
            html = fp.read()
        # print(html)
        html = html.replace("##@@",table)
        send_email(config["send"], config["recv"],config["email_pass"], html)



if __name__ == "__main__":
    main()