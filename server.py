from flask import Flask, render_template, abort
from database import Database
import psycopg2
from movie import Movie
import views

conn = psycopg2.connect("dbname=postgres user=postgres password=postgres")
cur = conn.cursor()
cur.execute("SELECT * FROM player")
records = cur.fetchall()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config")
    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/leaderboard", view_func=views.leaderboard_page, methods=["GET", "POST"])
    app.add_url_rule("/matches", view_func=views.matches_page)
    app.add_url_rule("/profile", view_func=views.profile_page, methods=["GET", "POST"])
    app.add_url_rule(
        "/profile/<int:movie_key>/edit",
        view_func=views.movie_edit_page,
        methods=["GET", "POST"],
    )

    db = Database()
    app.config["db"] = db
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=8080)
