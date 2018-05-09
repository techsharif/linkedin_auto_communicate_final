from django.core.mail import send_mail

from jetbuzz import settings


def mail_send(subject, message):
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        ['sharif.cse.hstu@gmail.com'],
        fail_silently=False,
    )
