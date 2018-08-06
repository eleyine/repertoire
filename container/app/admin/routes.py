from flask_user import current_user, login_required, roles_required
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import login_user
from flask_user.translation_utils import gettext as _

from app import csrf, db
# from app import domain
from app.admin import bp
from app.admin.forms import CustomResetPasswordForm

@bp.route('/test/', methods=['GET', 'POST'])
def test_view():
    return redirect(url_for('my_admin.reset_password_view'))


@bp.route('/create-new-password/', methods=['GET', 'POST'])
def reset_password_view():
    # domain.as_default()
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

@bp.route('/admin/custom/edit-users/', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
@csrf.exempt
def show_user_list():
    form = CustomUsersForm()
    if request.method == 'GET':
        users = User.query.all()
        subform_list = []
        for user in users:
            print(user.username)
            # user_data = {
            #     'username': user.username,
            #     'email': user.email
            # }
            # user_list_data.append(user_list_data)


            sub_form = CustomUserForm()
            sub_form.username.data = user.username
            sub_form.email.data = user.email
            form.users.append_entry(sub_form)

        # form.users.data = subform_list
        return render_template('admin/edit-users.html', form=form)

    else:
        pass
        # for user in users:
        #     form = CustomUserForm()
        #     if form.validate_on_submit():
        #         form_users = form.users
        #         for form_user in form_users:
        #             username = form_user.data.
        #             users = User.query.filter_by(email=form.email.data).first()
        #
        #         if user:
        #             send_password_reset_email(user)
        #         flash('Vérifiez votre email pour les instructions pour réinitialiser votre mot de passe')
        #         return redirect(url_for('auth.login'))
        #     json_data = get_json_data(current_app)
        #     tree_obj = DataTree(json_data)
        #     return render_template('index.html', title='Accueil', protocols=tree_obj.root.children)
