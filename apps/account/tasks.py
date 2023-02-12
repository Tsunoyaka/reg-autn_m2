from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from config.celery import app
from django.conf import settings




@app.task
def send_activation_code(email, activation_code):
    activation_link = f'http://127.0.0.1:8000/account/activate/{activation_code}/'
    html_message = render_to_string(
        'account/code_mail.html', 
        {'activation_link': activation_link}
        )
    send_mail(
        'Activate your account!',
        '',
        settings.EMAIL_HOST_USER,
        [email],
        html_message=html_message,
        fail_silently=False
    )


@app.task
def send_mentor_activation_code(email, activation_code):
    activation_link = f'http://127.0.0.1:8000/account/mentor-activate/{activation_code}/'
    html_message = render_to_string(
        'account/code_mail.html', 
        {'activation_link': activation_link}
        )
    send_mail(
        'Activate your account!',
        '',
        settings.EMAIL_HOST_USER,
        [email],
        html_message=html_message,
        fail_silently=False
    )