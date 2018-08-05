import os
import shutil

import flask_user
from app import create_app
app = create_app()

with app.app_context():
    for lang in app.config['LANGUAGES']:
        # find flask_user translations directory
        dist_path = os.path.dirname(flask_user.__file__)
        dist_translations_path = os.path.join(dist_path, 'translations', lang)

        # find local translations directory
        src_translations_path = os.path.join(app.root_path, 'translations', lang)

        # copy local translations directory to package directory... only hack that works so far :(
        if os.path.exists(dist_translations_path):
            shutil.rmtree(dist_translations_path)

        print('{} --> {}'.format(src_translations_path, dist_translations_path))
        shutil.copytree(src_translations_path, dist_translations_path)
