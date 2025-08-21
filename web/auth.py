from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models import db, User

auth = Blueprint("auth", __name__)

# Registrazione
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username già esistente!", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role="user"
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registrazione completata! Ora puoi fare login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# Login
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash("Credenziali errate!", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)
        return redirect(url_for("routes.dashboard"))

    return render_template("login.html")


# Logout
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
