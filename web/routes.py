from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user
from models import db, Prediction
import joblib, os, pandas as pd
from werkzeug.utils import secure_filename

routes = Blueprint("routes", __name__)

# Percorsi modelli ed encoders
MODEL_PATH = "/data/models/model.joblib"
ENCODER_PATH = "/data/encoders/car.data_encoders.joblib"
TRIGGER_FILE = "/data/raw/trigger.txt"

# Carica modello e encoders
model = joblib.load(MODEL_PATH)
encoders = joblib.load(ENCODER_PATH)
inv_target_map = {v: k for k, v in encoders["class"].items()}

# Dashboard (solo utenti loggati)
@routes.route("/dashboard")
def dashboard():
    if hasattr(current_user, "is_authenticated") and current_user.is_authenticated:
        predictions = Prediction.query.order_by(Prediction.timestamp.desc()).all()
        if current_user.role == "admin":
            return render_template("admin_dashboard.html", predictions=predictions)
        else:
            user_preds = [p for p in predictions if p.user_id == current_user.id]
            return render_template("user_dashboard.html", predictions=user_preds)
    else:
        return render_template("home.html")  # Mostra home se non loggato

# Predizione (accessibile anche senza login)
@routes.route("/predict", methods=["POST"])
def predict():
    try:
        features = [request.form[col] for col in ["buying","maint","doors","persons","lug_boot","safety"]]
    except KeyError:
        return jsonify({"error": "Mancano dati nel form"}), 400

    df = pd.DataFrame([features], columns=["buying","maint","doors","persons","lug_boot","safety"])

    # Codifica
    for col in df.columns:
        df[col] = pd.Categorical(df[col], categories=list(encoders[col].keys())).codes

    pred_code = model.predict(df)[0]
    prediction = inv_target_map[pred_code]

    # Salva predizione solo se l'utente è loggato
    if hasattr(current_user, "is_authenticated") and current_user.is_authenticated:
        new_pred = Prediction(
            input_data=",".join(features),
            prediction=str(prediction),
            user_id=current_user.id
        )
        db.session.add(new_pred)
        db.session.commit()

    return jsonify({
        "result": prediction,
        "description": f"Predizione generata per i valori forniti: {','.join(features)}"
    })

# Gestione admin per upload dataset
UPLOAD_FOLDER = "/data/uploads"
ALLOWED_EXTENSIONS = {"data"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@routes.route("/upload_dataset", methods=["POST"])
def upload_dataset():
    if 'dataset' not in request.files:
        flash("Nessun file selezionato", "error")
        return redirect(url_for("routes.dashboard"))
    
    file = request.files['dataset']
    
    if file.filename == "":
        flash("Nessun file selezionato", "error")
        return redirect(url_for("routes.dashboard"))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        flash(f"Dataset '{filename}' caricato correttamente!", "success")
        # Qui puoi aggiungere logica per aggiornare modello o trigger per ricaricare dati
        return redirect(url_for("routes.dashboard"))
    else:
        flash("Formato file non supportato. Usa solo file .data", "error")
        return redirect(url_for("routes.dashboard"))
