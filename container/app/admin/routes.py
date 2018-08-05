from flask_user import current_user, login_required, roles_required
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import login_user
from flask_user.translation_utils import gettext as _

from app import csrf, db
from app.admin import bp
from app.admin.forms import CustomResetPasswordForm


@bp.route('/create-new-password/', methods=['GET', 'POST'])
def reset_password_view():
    user_manager = current_app.user_manager
    safe_next_url = user_manager._get_safe_next_url('next', '')
    if current_user.is_authenticated and current_user.reinitialise:
        form = CustomResetPasswordForm()
         # Process valid POST
        if request.method == 'POST' and form.validate():
            # Retrieve User
            password = form.new_password.data
            hash_password = user_manager.hash_password(password)
            current_user.password = hash_password
            current_user.reinitialise = False
            current_user.tmp_password = ''
            db.session.add(current_user)
            db.session.commit()

            flash(_("Votre mot de passe a été mis à jour."), "success")
            login_user(current_user, remember=True)
            return redirect(user_manager._endpoint_url(''))

        else:
            template_filename = 'admin/reset-password.html'
            return render_template(template_filename,
                  form=form)
    else:
        return redirect(user_manager._endpoint_url(''))

