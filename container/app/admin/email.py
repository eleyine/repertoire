from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail

from app.main.utils import get_config_json

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(current_app, msg)
    # Thread(target=send_async_email,
           # args=(current_app._get_current_object(), msg)).start()

def send_password_reset_email(user, tmp_password):
    print('sending password reset email with password', tmp_password)
    site_title = current_app.config['title']
    send_email('[{}] Réinitialisation de mot de passe'.format(site_title),
               sender=current_app.config['USER_EMAIL_SENDER_EMAIL'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, tmp_password=tmp_password,
                                         site_title=site_title),
               html_body=render_template('email/reset_password.html',
                                         user=user, tmp_password=tmp_password,
                                         site_title=site_title))
