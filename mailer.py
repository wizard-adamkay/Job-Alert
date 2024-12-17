import os
import smtplib
import ssl
from email.mime.text import MIMEText
from typing import List

import keyring

from job import Job

botEmail = os.getenv("BOTEMAIL")
myEmail = os.getenv("MYEMAIL")
smtp_server = "smtp.gmail.com"
smtp_port = 465
botPass = keyring.get_password("email_service", botEmail)


class Mailer:

	def sendEmail(self, jobs: List[Job]):
		subject = "New Job Postings Detected"
		body = "Jobs found:\n"
		for job in jobs:
			body += f"Title: {job.title}\nLink: {job.link}\nCompany: {job.company}\n\n"
		msg = MIMEText(body)
		msg["Subject"] = subject
		msg["From"] = botEmail
		msg["To"] = myEmail

		context = ssl.create_default_context()
		with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
			server.login(botEmail, botPass)
			server.sendmail(botEmail, myEmail, msg.as_string())
