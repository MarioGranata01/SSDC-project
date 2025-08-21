from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Prediction
import joblib, os, pandas as pd

routes = Blueprint("routes", __name__)

# Percorsi modelli ed encoders
MODEL_PATH = "/data/models/model.joblib"
ENCODER_PATH = "/data/encoders/car.data_encoders.joblib"

# Carica modello e encoders
model = joblib.load(MODEL_PATH)
encoders = joblib.load(ENCODER_PATH)
inv_target_map = {v: k for k, v in encoders["class"].items()}

# Dashboard (diversa per admin o user)
@routes.route("/dashboard")
@login_required
def dashboard():
    predictions = Prediction.query.order_by(Prediction.timestamp.desc()).all()
    if current_user.role == "admin":
        return render_template("admin_dashboard.html", predictions=predictions)
    else:
        user_preds = [p for p in predictions if p.user_id == current_user.id]
        return render_template("user_dashboard.html", predictions=user_preds)

# Effettua predizione
@routes.route("/predict", methods=["POST"])
@login_required
def predict():
    features = [request.form[col] for col in ["buying", "maint", "doors", "persons", "lug_boot", "safety"]]
    df = pd.DataFrame([features], columns=["buying","maint","doors","persons","lug_boot","safety"])

    # Codifica
    for col in df.columns:
        df[col] = pd.Categorical(df[col], categories=list(encoders[col].keys())).codes

    pred_code = model.predict(df)[0]
    prediction = inv_target_map[pred_code]

    # Salva predizione
    new_pred = Prediction(
        input_data=",".join(features),
        prediction=str(prediction),
        user_id=current_user.id
    )
    db.session.add(new_pred)
    db.session.commit()

    flash(f"Predizione: {prediction}", "success")
    return redirect(url_for("routes.dashboard"))

# Admin upload dataset
@routes.route("/admin/upload", methods=["POST"])
@login_required
def upload_dataset():
    if current_user.role != "admin":
        flash("Non autorizzato!", "danger")
        return redirect(url_for("routes.dashboard"))

    file = request.files["dataset"]
    if file:
        os.makedirs("/data/raw", exist_ok=True)
        filepath = os.path.join("/data/raw", "car.data")
        file.save(filepath)
        flash("Nuovo dataset caricato! Riavvia preprocessing e training.", "success")
    return redirect(url_for("routes.dashboard"))
