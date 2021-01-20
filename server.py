from flask import Flask, render_template, abort
from database import Database
from datetime import datetime
from movie import Player
from flask_login import LoginManager
import views
from player import get_user
import psycopg2
import urllib.parse as urlparse
import os

lm = LoginManager()


@lm.user_loader
def load_user(user_id):
    return get_user(user_id)


app = Flask(__name__)


def create_app():
    app.config['SECRET_KEY'] = 'very-secret-key'
    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule(
        "/login", view_func=views.login_page, methods=["GET", "POST"]
    )
    app.add_url_rule("/play", view_func=views.play_page)
    app.add_url_rule("/logout", view_func=views.logout_page)
    app.add_url_rule("/leaderboard", view_func=views.leaderboard_page, methods=["GET", "POST"])
    app.add_url_rule("/matches", view_func=views.matches_page)
    app.add_url_rule("/admin", view_func=views.admin_page, methods=["GET", "POST"])
    app.add_url_rule("/profile", view_func=views.profile_page)
    app.add_url_rule(
        "/signup",
        view_func=views.signup_page,
        methods=["GET", "POST"],
    )

    lm.init_app(app)
    lm.login_view = "login_page"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=8080)
