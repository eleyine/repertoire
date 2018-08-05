import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_babelex import Babel, Domain
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from config import Config
from flask_wtf.csrf import CSRFProtect
from flask import g, session

import sqlite3 as sql
import json
import datetime
from sqlalchemy import and_

# babel = Babel()
domain = Domain(domain='app')
babel = Babel()

db = SQLAlchemy()
migrate = Migrate()

mail = Mail()
bootstrap = Bootstrap()
csrf = CSRFProtect()

@babel.localeselector
def get_locale():
    translations = [str(translation) for translation in babel.list_translations()]
    # dirname = os.path.join(app.root_path, 'translations')
    # print(dirname)
    print(translations)
    from flask import _request_ctx_stack
    ctx = _request_ctx_stack.top
    # ctx = app.app_context()
    # print('default domain path', domain.get_translations_path(ctx))
    # babel._default_domain = domain
    print('default domain from babel object??', babel._default_domain.get_translations_path(ctx))
    print('os path:', os.path.join(ctx.app.root_path, 'translations'))
    return 'fr'

# @babel.localeselector
# def get_locale():
#     if request.args.get('lang'):
#         session['lang'] = request.args.get('lang')
#     return session.get('lang', 'fr')

# @babel.localeselector
# def get_locale():
#     print('getting locale...')
#     return 'fr'
    # translations = [str(translation) for translation in babel.list_translations()]
    # return request.accept_languages.best_match(translations)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # refresh()
    # dirname = os.path.join(app.root_path, 'translations')
    # domain = Domain(domain='flask_user', dirname=dirname)
    # babel = Babel(app, default_domain=domain)
    # babel._default_domain = domain
    babel.init_app(app)
    babel._default_domain = domain


        # return request.accept_languages.best_match(translations))
        # return app.config['BABEL_DEFAULT_LOCALE']

    # babel.init_app(app)

    csrf.init_app(app)

    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    db.init_app(app)
    with app.app_context():
        db.create_all()
    migrate.init_app(app, db)
    # login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/custom-admin')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # update app config
    from app.main.utils import get_config_json
    with app.app_context():
        config = get_config_json(update_app_config=False)
        for k, v in config.items():
            app.config[k] = v

    if app.config['MAIL_SERVER'] and app.config["admins"]:
        app.logger.info("Setting up mail server...")
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'],
                    app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()

        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['admins'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log',
                                       maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('App startup')

    # Create protocols database if it does not exist
    from app.main.utils import get_json_data
    with sql.connect(app.config.get('PROTOCOLS_DB_FN')) as con:
        cur = con.cursor()
        sql_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';".format(table_name='Protocols')
        cur.execute(sql_query)
        rows = cur.fetchall()

        # if table does not exist or is empty, (create it and) populate it with init_data.json
        if len(rows) == 0 or get_json_data(app) is None:
            cur.execute('CREATE TABLE IF NOT EXISTS Protocols (version_id INTEGER PRIMARY KEY, user, timestamp, JSON_text TEXT)')

            json_data_fn = os.path.join(app.config.get('ROOT_DIR'), 'data', 'init_data.json')
            print(json_data_fn)
            if not os.path.exists(json_data_fn):
                print('Unable to populate db with initial json...')

            else:

                with open(json_data_fn, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)

                json_str = json.dumps(json_data)
                now = str(datetime.datetime.now())
                user = 'Original Data'

                cur.execute("INSERT INTO Protocols (user, timestamp, JSON_text) VALUES (?,?,?)",
                    (user, now, json_str,))
                con.commit()

    from app.models import User
    from app.models import user_manager

    user_manager.init_app(app, db, User)

    from flask_user import current_user
    @app.context_processor
    def context_processor():
        return dict(user_manager=user_manager, current_user=current_user)

    # setup admin
    from app.admin.setup_flask_admin import setup_admin
    with app.app_context():
        setup_admin(app, db)

    # make sure admins have admin roles
    with app.app_context():
        admin_role = Role.query.filter(Role.name == 'Admin').one_or_none()
        if not admin_role:
            admin_role = Role(name='Admin')
        for username in app.config['ADMIN_USERNAMES']:
            user = User.query.filter(User.username == username).one_or_none()
            if user:
                # user_is_admin = user.is_admin
                # UserRoles.query.filter(and_(UserRoles.user_id == user.id, UserRoles.role_id == admin_role.id))
                if not user.is_admin:
                    user.roles.append(admin_role)
                    db.session.add(user)
                    db.session.commit()
    return app

from app import models
from app.models import User, Role, UserRoles
# user_manager = UserManager(app, db, User)
