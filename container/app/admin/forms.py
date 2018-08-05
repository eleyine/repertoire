from flask_wtf import FlaskForm
from flask_user.translation_utils import gettext as _
from wtforms import StringField, FormField, FieldList, SubmitField, PasswordField, HiddenField
from wtforms import validators
from flask_user.forms import password_validator
from flask import current_app
class CustomResetPasswordForm(FlaskForm):
    """Reset password form."""
    # password = PasswordField(_('Mot de passe (temporaire)'), validators=[
        # validators.DataRequired(_('Password is required')),
        # ])
    new_password = PasswordField(_('New Password'), validators=[
        validators.DataRequired(_('New Password is required')),
        password_validator,
        ])
    retype_password = PasswordField(_('Retype New Password'), validators=[
        validators.EqualTo('new_password', message=_('New Password and Retype Password did not match'))])
    next = HiddenField()
    submit = SubmitField(_('Change password'))

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
