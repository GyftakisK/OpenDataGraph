from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail, celery


@celery.task(queue='mailQueue')
def send_email(subject, sender, recipients, text_body, html_body,
               attachments=None):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    with current_app.app_context():
        mail.send(msg)
