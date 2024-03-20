from . import mail
from flask_mail import Message
from settings import settings 


def send_mail(user, email, token):
    msg = Message('Hello from book store app',sender=settings.email_sender,recipients=[email])
    msg.body = f"Hey {user}, sending you this email from my Book store app, Click this link to verify" \
                f" http://127.0.0.1:5000/verify?token={token}"
    mail.send(msg)
    return "Message sent!"