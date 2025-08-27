from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  
    role = db.Column(db.String(10), nullable=False, default="user")  

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_data = db.Column(db.String(200), nullable=False)
    prediction = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

def create_admin(app):
    with app.app_context():
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                password=generate_password_hash("admin123"),
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()
