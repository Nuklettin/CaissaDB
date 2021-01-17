from flask import Flask, render_template, current_app, abort, request, url_for, redirect
from datetime import datetime
from movie import Movie


def home_page():
    today = datetime.today()
    day_name = today.strftime("%A")
    return render_template("home.html", day=day_name)


def leaderboard_page():
    db = current_app.config["db"]
    if request.method == "GET":
        return render_template("movies.html")
    else:
        form_movie_keys = request.form.getlist("movie_keys")
        for form_movie_key in form_movie_keys:
            db.delete_movie(int(form_movie_key))
        return redirect(url_for("profile_page"))


def matches_page():
    db = current_app.config["db"]
    return render_template("movie.html")


def profile_page():
    db = current_app.config["db"]
    return render_template("movies.html")


def movie_edit_page(movie_key):
    if request.method == "GET":
        db = current_app.config["db"]
        movie = db.get_movie(movie_key)
        if movie is None:
            abort(404)
        values = {"title": movie.title, "year": movie.year}
        return render_template(
            "movie_edit.html",
            min_year=1887,
            max_year=datetime.now().year,
            values=values,
        )
    else:
        valid = validate_movie_form(request.form)
        if not valid:
            return render_template(
                "movie_edit.html",
                min_year=1887,
                max_year=datetime.now().year,
                values=request.form,
            )
        title = request.form.data["title"]
        year = request.form.data["year"]
        movie = Movie(title, year=year)
        db = current_app.config["db"]
        db.update_movie(movie_key, movie)
        return redirect(url_for("profile_page", movie_key=movie_key))


def validate_movie_form(form):
    form.data = {}
    form.errors = {}

    form_title = form.get("title", "").strip()
    if len(form_title) == 0:
        form.errors["title"] = "Title can not be blank."
    else:
        form.data["title"] = form_title

    form_year = form.get("year")
    if not form_year:
        form.data["year"] = None
    elif not form_year.isdigit():
        form.errors["year"] = "Year must consist of digits only."
    else:
        year = int(form_year)
        if (year < 1887) or (year > datetime.now().year):
            form.errors["year"] = "Year not in valid range."
        else:
            form.data["year"] = year

    return len(form.errors) == 0
