from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail

from app import create_app
app = create_app()

# if __name__ == "__main__":
#     app.jinja_env.auto_reload = True
#     app.config['TEMPLATES_AUTO_RELOAD'] = True
#     app.run(debug=True, host='0.0.0.0', port=5000)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def main():
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # app.run(debug=True, host='0.0.0.0', port=5000)

    with app.app_context():
        send_email('ceci est un test', 'chum', ['eleyine@gmail.com'], 'test', 'test')

def main_with_context():
    with app.app_context():
        from app.admin.email import send_password_reset_email
        from app.models import User
        user = User.query.filter(User.username == 'eleyine').one_or_none()
        if user:
            send_password_reset_email(user, 'tmptmp')
        else:
            print('no user found...')

if __name__ == '__main__':
    main_with_context()
