from flask_wtf import FlaskForm
from flask_user.translation_utils import gettext as _
from wtforms import StringField, FormField, FieldList, SubmitField, PasswordField, HiddenField
from wtforms import validators
from flask_user.forms import password_validator
from flask import current_app

class CustomUserForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[validators.DataRequired()])
    email = StringField('Courriel', validators=[validators.DataRequired()])

class CustomUsersForm(FlaskForm):
    users = FieldList(FormField(CustomUserForm))

class CustomResetPasswordForm(FlaskForm):
    """Reset password form."""
    # password = PasswordField(_('Mot de passe (temporaire)'), validators=[
        # validators.DataRequired(_('Password is required')),
        # ])
    new_password = PasswordField('Nouveau mot de passe', validators=[
        validators.DataRequired('Nouveau mot de passe est requis'),
        password_validator,
        ])
    retype_password = PasswordField('Retapez nouveau mot de passe', validators=[
        validators.EqualTo('new_password', message='Nouveau mot de passe et mot de passe retapé sont différents')])
    next = HiddenField()
    submit = SubmitField('Soumettre nouveau mot de passe')

    def validate(self):
        # Use feature config to remove unused form fields
        user_manager =  current_app.user_manager
        if not user_manager.USER_REQUIRE_RETYPE_PASSWORD:
            delattr(self, 'retype_password')
        # # Add custom password validator if needed
        # has_been_added = False
        # for v in self.new_password.validators:
        #     if v==user_manager.password_validator:
        #         has_been_added = True
        # if not has_been_added:
        #     self.new_password.validators.append(user_manager.password_validator)
        # Validate field-validators
        if not super(CustomResetPasswordForm, self).validate(): return False
        # All is well
        return True
