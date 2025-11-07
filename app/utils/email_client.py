import smtplib
import os
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER or "noreply@example.com")

def send_email(to_address: str, subject: str, body: str):
	msg = EmailMessage()
	msg["From"] = FROM_EMAIL
	msg["To"] = to_address
	msg["Subject"] = subject
	msg.set_content(body)

	if not SMTP_HOST:
		# fallback: print to console
		print("SMTP não configurado. Email abaixo:")
		print(msg)
		return

	with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as s:
		s.starttls()
		if SMTP_USER and SMTP_PASS:
			s.login(SMTP_USER, SMTP_PASS)
		s.send_message(msg)
