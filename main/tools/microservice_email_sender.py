# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_order_ready_mail(recipient, order_number):
    KEY = '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'
    author = 'admin@seonior.ru'
    url = f'https://seonior.ru/orders/{order_number}'
    mail = Mail(from_email=author,
                to_emails=recipient,
                subject=f'Ваш заказ номер {order_number} успешно собран',
                html_content=f'Отчет доступен по ссылке: {url}')

    sg = SendGridAPIClient(KEY)
    sg.send(mail)