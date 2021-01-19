from flask import current_app
from flask import flash
from flask_login import UserMixin
import psycopg2
import os
import urllib.parse as urlparse


class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.active = True
        self.is_admin = False

    def get_id(self):
        return self.username

    @property
    def is_active(self):
        return self.active


def get_user(user_id):
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    dbname = url.path[1:]
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port

    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()
    query = "SELECT password FROM player WHERE username = '" + user_id + "';"
    cur.execute(query)
    record = cur.fetchall()
    password = ''
    for row in record:
        password = row[0]
    user = User(user_id, password) if password else None
    if user is not None:
        query = "SELECT username FROM admin WHERE username = '" + user_id + "';"
        cur.execute(query)
        record = cur.fetchall()
        username = ''
        for row in record:
            username = row[0]
        if username == user_id:
            user.is_admin = True
    return user
