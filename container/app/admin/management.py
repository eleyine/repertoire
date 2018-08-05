from flask_user import UserManager, signals, current_user
from flask_login import login_user
from flask_user.translation_utils import gettext as _
from flask import current_app, flash, redirect, render_template, request, url_for

from app.admin.forms import CustomResetPasswordForm


# Customize Flask-User
class CustomUserManager(UserManager):

    def _do_login_user(self, user, safe_next_url, remember_me=False):
        # User must have been authenticated
        if not user: return self.unauthenticated()

        # Check if user account has been disabled
        if not user.active:
            flash(_('Your account has not been enabled.'), 'error')
            return redirect(url_for('user.login'))

        # Check if user has a confirmed email address
        if self.USER_ENABLE_EMAIL \
                and self.USER_ENABLE_CONFIRM_EMAIL \
                and not current_app.user_manager.USER_ALLOW_LOGIN_WITHOUT_CONFIRMED_EMAIL \
                and not self.db_manager.user_has_confirmed_email(user):
            url = url_for('user.resend_email_confirmation')
            flash(_('Your email address has not yet been confirmed. Check your email Inbox and Spam folders for the confirmation email or <a href="%(url)s">Re-send confirmation email</a>.', url=url), 'error')
            return redirect(url_for('user.login'))

        # Use Flask-Login to sign in user
        # print('login_user: remember_me=', remember_me)
        login_user(user, remember=remember_me)

        # Send user_logged_in signal
        signals.user_logged_in.send(current_app._get_current_object(), user=user)

        # Check if password has been reset correctly (THIS IS MY ADDITION)
        if user.reinitialise:
            print('User has reset password!')
            return redirect(url_for('my_admin.reset_password_view'))

        # Flash a system message
        flash(_('You have signed in successfully.'), 'success')
        # Redirect to 'next' URL
        return redirect(safe_next_url)

    # Override or extend the default forgot password view
    def forgot_password_view(self):
        """Prompt for email and send reset password email."""

        # Initialize form
        form = self.ForgotPasswordFormClass(request.form)
        UserClass = self.db_manager.UserClass

        # Process valid POST
        if request.method == 'POST' and form.validate():
            from app.admin.utils import set_tmp_password_for_user
            from app.admin.email import send_password_reset_email
            # Get User and UserEmail by email
            email = form.email.data
            user = UserClass.query.filter(UserClass.email == email).one_or_none()

            if user and email:
                # Create new tmp password for this user
                tmp_password = set_tmp_password_for_user(user)

                # Send reset_password email
                send_password_reset_email(user, tmp_password)
                # self.email_manager.send_reset_password_email(user, user_email)
                # Send forgot_password signal
                signals.user_forgot_password.send(current_app._get_current_object(), user=user)

                # Flash a system message
                flash(_(
                    "Un mot de passe temporaire a été envoyé au courriel '%(email)s'.",
                    email=email), 'success')
            else:
                flash(_(
                    "Le courriel '%(email)s' n'est assigné à aucun compte. Veuillez contacter l'administrateur pour créer un compte.",
                    email=email), 'success')

            # Redirect to the login page
            return redirect(self._endpoint_url(self.USER_AFTER_FORGOT_PASSWORD_ENDPOINT))

        # Render form
        self.prepare_domain_translations()
        return render_template(self.USER_FORGOT_PASSWORD_TEMPLATE, form=form)
