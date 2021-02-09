# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message = Mail(
    from_email='admin@seonior.ru',
    to_emails='misteriska@Ya.ru',
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
try:
    KEY = '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'
    sg = SendGridAPIClient(KEY)
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)