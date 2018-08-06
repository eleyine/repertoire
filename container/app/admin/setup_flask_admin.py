import re

from flask import url_for, redirect

from flask_admin import Admin
# from flask_wtf import Form
from wtforms_alchemy import ModelForm
from flask_wtf import Form
from flask_admin.form import SecureForm
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.menu import MenuLink, MenuView
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.filters import BaseBooleanFilter

from app.models import User, Role, UserRoles
from app.main.utils import get_config_json
# from flask.ext.contrib.sqla import ModelView
class MyForm(Form):
    def __init__(self, formdata=None, obj=None, prefix=u'', **kwargs):
        self._obj = obj
        super(MyForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)


def setup_admin(app, db):
    from flask_user import current_user

    class SecureModelView(ModelView):
        # Make Flask-Admin use WTForms-Alchemy
        form_base_class = MyForm
        def is_accessible(self):
            return current_user.is_authenticated and current_user.is_admin

    class UserModelView(SecureModelView):
        list_template = 'admin/user_list.html'
        column_list = ('active', 'reinitialise', 'username', 'email', 'tmp_password', 'is_admin', 'roles')
        column_labels = dict(active='Actif', reinitialise='Réinitialisé', email='Courriel', tmp_password='MdP temporaire', is_admin='Admin', roles='Rôles')
        page_size = 150

        # column_filters = (IsAdminFilter,)
        column_searchable_list = ('username', 'email')

        can_create = False

        edit_modal = True
        form_widget_args = {
            'reinitialise': {
                'readonly':True
            },
            'username': {
                'readonly':True,
                # 'required': False,
            },
            'email': {
                'readonly':True,
                # 'required': False,
            },
            'password': {
                'readonly':True
            },
            'tmp_password': {
                'readonly':True
            },
        }

        # def reinitialise_formatter(view, context, model, name):
        #     # `view` is current administrative view
        #     # `context` is instance of jinja2.runtime.Context
        #     # `model` is model instance
        #     # `name` is property name
        #     if getattr(model, name):
        #         return 'Mot de passe temporaire'
        #     else:
        #         return "Nouveau mot de passe crée"
        # column_formatters = dict(
        #     reinitialise=reinitialise_formatter
        #     )

        column_descriptions = dict(
            reinitialise="Ce champ indique si le mot de passe actuel est temporaire / réinitialisé (nouvel utilisateur ou mot de passe oublié). Si c'est le cas, l'utilisateur devra créer un nouveau mot de passe lors de sa prochaine connexion."
        )



        def test_bool(self):
            return True

    class RoleModelView(SecureModelView):
        column_list = ('name', 'users')
        form_columns = ('name',)
        form_widget_args = {
            'users': {
                'readonly':True
            },
        }


    class HomeView(AdminIndexView):
        @expose('/')
        def index(self):
            all_roles = [role.name for role in Role.query.all() if role.name != 'Admin']

            config = get_config_json()
            privileged_roles_regex_list = config['roles_privilegies']
            patterns = []
            for privileged_role_regex in privileged_roles_regex_list:
                p = re.compile(privileged_role_regex)
                patterns.append(re.compile(p))

            privileged_roles = []
            non_privileged_roles = []
            for role_name in all_roles:
                is_privileged = False
                for p in patterns:
                    if p.match(role_name):
                        is_privileged = True
                        break
                if is_privileged:
                    privileged_roles.append(role_name)
                else:
                    non_privileged_roles.append(role_name)

            champs_sensibles = ', '.join(config['champs_sensibles'])
            return self.render('admin/index.html', privileged_roles=privileged_roles, non_privileged_roles=non_privileged_roles, champs_sensibles=champs_sensibles)


    class JsonView(BaseView):
        @expose('/')
        def index(self):
            return redirect(url_for('main.view_last_json'))

    admin = Admin(app, template_mode='bootstrap3', index_view=HomeView(),  url='/admin')

    # User-related Models
    admin.add_view(UserModelView(User, db.session, name='Utilisateurs', endpoint='admin.model_view_user'))
    admin.add_view(RoleModelView(Role, db.session, name='Rôles',  endpoint='admin.model_view_role'))

    # JSON
    admin.add_view(JsonView(name='JSON', endpoint='admin.view_json'))

    # Back to home page
    admin.add_link(MenuLink(name='Retour au site', category='', url='/'))
