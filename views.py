from flask import Flask, render_template, current_app, abort, request, url_for, redirect, flash
from datetime import datetime
from database import Database
from wtforms import StringField, PasswordField
from flask_wtf import FlaskForm
from flask_wtf.file import DataRequired
from passlib.hash import pbkdf2_sha256 as hasher
from flask_login import login_user, logout_user
from player import get_user
from movie import Player


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


def home_page():
    return render_template("home.html")


def play_page():
    return render_template("play.html")


def leaderboard_page():
    return render_template("leaderboard.html")


def admin_page():
    if request.method == "GET":
        return render_template(
            "admin.html")
    else:
        valid = validate_form(request.form)
        if not valid:
            return render_template(
                "admin.html"
            )
        username = request.form.data["username"]
        if username is not None:
            db = Database()
            db.delete_player(username)
        match_id = request.form.data["match_id"]
        if match_id is not None:
            db = Database()
            db.delete_match(match_id)


def profile_page():
    return render_template("profile.html")


def matches_page():
    return render_template("matches.html")


def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.data["username"]
        user = get_user(username)
        if user is not None:
            password = form.data["password"]
            if hasher.verify(password, user.password):
                login_user(user)
                flash("You have logged in.")
                next_page = request.args.get("next", url_for("profile_page"))
                return redirect(next_page)
        flash("Invalid credentials.")
    return render_template("login.html", form=form)


def logout_page():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for("home_page"))


def signup_page():
    if request.method == "GET":
        return render_template(
            "signup.html")
    else:
        valid = validate_form(request.form)
        if not valid:
            return render_template(
                "signup.html"
            )
        username = request.form.data["username"]
        password = request.form.data["password"]
        db = Database()
        value = db.new_player(username, password)
        if value == 0:
            return redirect(url_for("signup_page"))
        else:
            flash("Sign up successful. You can log in now.")
            return redirect(url_for("login_page"))


def validate_form(form):
    form.data = {}
    form.errors = {}

    form_username = form.get("username", "").strip()
    if len(form_username) == 0:
        form.errors["username"] = "Username can not be blank."
    else:
        form.data["username"] = form_username

    form_password = form.get("password", "").strip()
    if len(form_password) == 0:
        form.errors["password"] = "Password can not be blank."
    else:
        form.data["password"] = form_password

    return len(form.errors) == 0
