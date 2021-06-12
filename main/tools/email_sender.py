from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.core.mail import send_mail

class MailEngine:
    def __init__(self, post_data):
        self.admin_email = 'admin@seonior.ru'
        self.SENDGRID_API_KEY = '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'
        self.post_data = post_data
        self.recipients = list()

        self.get_recipients()

    def get_recipients(self):
        self.recipients = self.post_data['email'].lower()

    def send_reset_password_mail_via_django(self, password):
        mail_title = 'Письмо с паролем'
        mail_body = f'Ваш временный пароль: {password}. Пожалуйста, смените его сразу после авторизации. Ссылка для авторизации: https://seonior.ru/authorization'

        send_mail(mail_title, mail_body, self.admin_email, self.recipients)

    def send_order_ready_mail_via_sendgrid(self, order_number):
        url = f'https://seonior.ru/orders/{order_number}'
        mail = Mail(from_email=self.admin_email,
                    to_emails=self.recipients,
                    subject=f'Ваш заказ номер {order_number} успешно собран',
                    html_content=f'Отчет доступен по ссылке: {url}')

        sg = SendGridAPIClient(self.SENDGRID_API_KEY)
        sg.send(mail)