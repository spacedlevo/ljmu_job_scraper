import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader

import email_settings


db = sqlite3.connect('ljmu_jobs.db')
c = db.cursor()


def send_email(html):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(email_settings.username, email_settings.pwd)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "LJMU Vacancies"
    msg['From'] = email_settings.username
    msg['To'] = email_settings.to
    mail_message = MIMEText(html, 'html')
    msg.attach(mail_message)
    server.sendmail(email_settings.username, email_settings.to, msg.as_string())
    print("Mail Sent")
    server.quit()
    server.close()


def get_jobs():
    with db:
        c.execute(
            ''' SELECT title, "contract type", hours, salary, "closing date", ref
            FROM jobs WHERE "email sent"=0 AND "job type"="Admin" ''')
        return c.fetchall()


def create_template(jobs):
    template_vars = {'jobs': jobs}
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("email.html")
    return template.render(template_vars)


def update_emailed(jobs):
    with db:
        for job in jobs:
            c.execute(''' UPDATE jobs SET "email sent"=1 WHERE ref=? ''', (job[5],))


if __name__ == '__main__':
    jobs = get_jobs()
    if len(jobs) > 0:
        html = create_template(jobs)
        send_email(html)
        update_emailed(jobs)
    else:
        print("Nothing to send")
