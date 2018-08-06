import os
import shutil

import flask_user
from app import create_app
app = create_app()

def test_user_roles():
    with app.app_context():
        from app.models import Role, UserRoles
        admin_role = Role.query.filter(Role.name == 'Admin').one_or_none()
        if admin_role:
            print([str(i) for i in admin_role.users])
            # help(admin_role)
            user_roles = UserRoles.query.filter(UserRoles.role_id == admin_role.id)
            print([str(i) for i in user_roles.all()])

def reset_users():
    with app.app_context():
        # delete all users except admin
        from app.models import User
        from app import db
        users = User.query.all()
        for user in users:
            if not user.is_admin:
                print('Delete', user)
                db.session.delete(user)
                db.session.commit()


if __name__ == '__main__':
    pass
    # reset_users()
