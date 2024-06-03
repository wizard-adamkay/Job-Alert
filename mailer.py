import os
import smtplib
import ssl
from email.mime.text import MIMEText
import keyring

botEmail = os.getenv("BOTEMAIL")
myEmail = os.getenv("MYEMAIL")
smtp_server = "smtp.gmail.com"
smtp_port = 465
botPass = keyring.get_password("email_service", botEmail)

class Mailer:
	def sendEmail(self, jobs):
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
		print(f"Email sent to {myEmail} with new job postings.")
