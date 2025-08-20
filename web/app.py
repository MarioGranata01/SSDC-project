import joblib
import pandas as pd
from flask import Flask, request, render_template

app = Flask(__name__)

# Carica modello e encoder numerico
model = joblib.load("/data/models/model.joblib")
encoders = joblib.load("/data/encoders/car.data_encoders.joblib")

# Inverti la mappatura della colonna target
inv_target_map = {v: k for k, v in encoders['class'].items()}

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    if request.method == "POST":
        # Leggi input form come lista di valori
        input_values = [request.form.get(f) for f in ['buying','maint','doors','persons','lug_boot','safety']]
        
        # Trasforma input in codici numerici coerenti con gli encoder
        df = pd.DataFrame([input_values], columns=['buying','maint','doors','persons','lug_boot','safety'])
        for col in df.columns:
            df[col] = pd.Categorical(df[col], categories=list(encoders[col].keys())).codes

        # Predizione
        pred_code = model.predict(df)[0]

        # Decodifica predizione in label originale
        prediction = inv_target_map[pred_code]

    return render_template("index.html", prediction=prediction)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
