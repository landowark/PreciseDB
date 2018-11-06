
import smtplib
import json
from email.mime.text import MIMEText


def sendemail(kit_num, receiver, institute, patient_num):

    with open('credentials.json', 'r') as f:
        creds = json.load(f)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    body = "You are receiving this email because a sample with kit number {} was received in the Mai lab by {}. This is patient #{} of the trial.".format(
        kit_num, receiver, patient_num)
    mail = MIMEText(body)
    recipients = creds['emails']['Mai Lab'] + creds['emails'][institute]
    mail['Subject'] = "Automated message regarding Precise"
    mail['From'] = creds['gmail']
    mail['To'] = ", ".join(recipients)

    s.login(creds['gmail'], creds['app_pass'])

    s.sendmail(creds['gmail'], recipients, mail.as_string())
