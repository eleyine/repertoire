from werkzeug.security import generate_password_hash, check_password_hash
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
# from flask_login import UserMixin
import jwt
from app import db
from hashlib import md5
from time import time
from flask import current_app

import re


# @login.user_loader
# def load_user(id):
#     return User.query.get(int(id))

class MyUserMixin(UserMixin):
    def get_id(self):
        """Converts a User ID and parts of a User password hash to a token."""

        # This function is used by Flask-Login to store a User ID securely as a browser cookie.
        # The last part of the password is included to invalidate tokens when password change.
        # user_id and password_ends_with are encrypted, timestamped and signed.
        # This function works in tandem with UserMixin.get_user_by_token()
        user_manager = current_app.user_manager

        user_id = self.id
        password_ends_with = '' if user_manager.USER_ENABLE_AUTH0 or self.password is None else self.password[-8:]
        user_token = user_manager.generate_token(
            user_id,               # User ID
            password_ends_with,    # Last 8 characters of user password
        )
        # print("UserMixin.get_id: ID:", self.id, "token:", user_token)
        return user_token

    @classmethod
    def get_user_by_token(cls, token, expiration_in_seconds=None):
        # This function works in tandem with UserMixin.get_id()
        # Token signatures and timestamps are verified.
        # user_id and password_ends_with are decrypted.

        # Verifies a token and decrypts a User ID and parts of a User password hash
        user_manager = current_app.user_manager
        data_items = user_manager.verify_token(token, expiration_in_seconds)

        # Verify password_ends_with
        token_is_valid = False
        if data_items:

            # Load user by User ID
            user_id = data_items[0]
            password_ends_with = data_items[1]
            user = user_manager.db_manager.get_user_by_id(user_id)
            user_password = '' if user_manager.USER_ENABLE_AUTH0 or user is None else user.password[-8:]

            # Make sure that last 8 characters of user password matches
            token_is_valid = user and user_password==password_ends_with

        return user if token_is_valid else None

class User(db.Model, MyUserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    tmp_password = db.Column(db.String(100), nullable=False, server_default='')
    reinitialise = db.Column('reset_by_user', db.Boolean(), nullable=False, server_default='0')

   # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary='user_roles', backref='users')

    def __eq__(self, other):
        if hasattr(other, 'username') and other.username == self.username:
            return True
        else:
            return False



    @property
    def role_list(self):
        return ', '.join([r.name for r in self.roles])

    @property
    def has_acccess_to_sensitive_data(self):
        if self.is_admin:
            return True

        from app.main.utils import get_config_json
        config = get_config_json()
        privileged_roles = config['roles_privilegies']
        patterns = []

        for privileged_role in privileged_roles:
            p = re.compile(privileged_role)
            patterns.append(re.compile(p))

        for role in self.roles:
            if role._is_privileged(patterns=patterns):
                return True
        return False

    def __str__(self):
        return '{}'.format(self.username)

    def __repr__(self): #print username
        return '<User: {}>'.format(self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    @property
    def is_in_json(self):
        from app.main.graph_models import DataTree
        from app.main.utils import get_json_data
        from app.admin.utils import find_user_node
        json_data = get_json_data(current_app)
        tree = DataTree(json_data)
        node = find_user_node(self.username, tree)
        return node is not None

    @property
    def is_admin(self):
        for role in self.roles:
            if role.name == 'Admin':
                return True
        return False

# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    @property
    def is_privileged(self):
        return self._is_privileged()

    def _is_privileged(self, patterns=[]):
        if not patterns:
            config = get_config_json()
            privileged_roles = config['roles_privilegies']
            patterns = []
            for privileged_role in privileged_roles:
                p = re.compile(privileged_role)
                patterns.append(re.compile(p))

        for p in patterns:
            if p.match(self.name):
                return True
        return False

    def __str__(self):
        return self.name

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

    def __str__(self):
        return 'User {} - Role {}'.format(self.user_id, self.role_id)

from app.admin.management import CustomUserManager
user_manager = CustomUserManager(None, db, User)
