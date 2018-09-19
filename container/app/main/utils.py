# coding=utf-8

import re
import unidecode
import sqlite3 as sql
import json
import random
import string

from flask import current_app

def get_config_json(fn=None, update_app_config=True):
    if fn is None:
        fn = current_app.config['CONFIG_JSON_FILENAME']
    config = {}
    try:
        with open(fn, 'r', encoding='utf-8') as f:
            json_config = json.load(f)
        config = json_config
    except:
        raise(Exception('Missing or corrupted config json file in {}'.format(fn)))

    required_keys = (
        ('profondeur', int),
        ('username_field', str),
    )

    for k, _type in required_keys:
        if k not in config.keys():
            raise(Exception('Config file must include key "{}"'.format(k)))
        if not isinstance(config[k], _type):
            raise(Exception('Value "{}" for key "{}" in config file is not of type {}'.format(
                config[k], k, _type)))

    if update_app_config:
        for k, v in config.items():
            current_app.config[k] = v
    return config

def camelify(s):
    """
    Simplifies strings into CamelCase strings
    """
    # remove accents
    s = unidecode.unidecode(s)
    s = ''.join(x for x in s.title() if not x.isspace())
    s = s.replace(':', '')
    s = s.replace('.', '')
    return s

def slugify(s):
    """
    Simplifies ugly strings into something URL-friendly.
    >>> print slugify("[Some] _ Article's Title--")
    some-articles-title
    source: https://blog.dolphm.com/slugify-a-string-in-python/
    """

    # "[Some] _ Article's Title--"
    # "[some] _ article's title--"
    s = s.lower()

    # "[some] _ article's_title--"
    # "[some]___article's_title__"
    for c in [' ', '-', '.', '/']:
        s = s.replace(c, '_')

    # "[some]___article's_title__"
    # "some___articles_title__"
    s = re.sub('\W', '', s)

    # "some___articles_title__"
    # "some   articles title  "
    s = s.replace('_', ' ')

    # "some   articles title  "
    # "some articles title "
    s = re.sub('\s+', ' ', s)

    # "some articles title "
    # "some articles title"
    s = s.strip()

    # "some articles title"
    # "some-articles-title"
    s = s.replace(' ', '-')

    # remove accents
    s = unidecode.unidecode(s)

    return s

def get_json_data(app):
    with sql.connect(app.config.get('PROTOCOLS_DB_FN')) as con:
        cur = con.cursor()
        cur.execute("SELECT JSON_text FROM Protocols ORDER BY version_id DESC LIMIT 1")
        rows = cur.fetchall()

    if len(rows) == 0 or len(rows[0]) == 0:
        return None

    return json.loads(rows[0][0])


import collections

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def get_random_password(n=8):
    pwd = ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))
    return pwd

def get_username_for_node(node):
    config = get_config_json()
    username_field = config['username_field']
    for child in node.children:
        if child.label == username_field:
            return child.leaf_content
    return None

def update_static_content(app):
    from app.main.graph_models import DataTree
    from flask import render_template
    static_html_fn = app.config['STATIC_CONTENT_FILENAME']
    json_data = get_json_data(app)
    tree_obj = DataTree(json_data)
    static_html = render_template('index/static_content_template.html', title='Accueil', protocols=tree_obj.root.children)
    with open(static_html_fn, 'w') as f:
        f.write(static_html)
