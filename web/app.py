import os, joblib
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, current_user
from models import db, create_admin
from auth import auth
from routes import routes

app = Flask(__name__)
app.secret_key = "supersecret"

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "database", "database.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    db.create_all()
    create_admin(app)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

from models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth, url_prefix="/")
app.register_blueprint(routes, url_prefix="/")

@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect("/dashboard")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
