import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

PROCESSED_DIR = "/data/processed"
MODELS_DIR = "/data/models"

def train():
    # Legge tutti i file CSV o .data in processed/
    dfs = []
    for filename in os.listdir(PROCESSED_DIR):
        if filename.endswith(".csv") or filename.endswith(".data"):
            filepath = os.path.join(PROCESSED_DIR, filename)
            print(f"Trovato file: {filepath}")
            df = pd.read_csv(filepath, header=None)  # <-- senza header
            dfs.append(df)
    
    if not dfs:
        print("Nessun file CSV trovato in processed/")
        return
    
    data = pd.concat(dfs, ignore_index=True)

    # Assumiamo che l'ultima colonna sia il target
    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Modello Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Valutazione
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")

    # Salvataggio modello
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, "model.joblib")
    joblib.dump(model, model_path)
    print(f"Modello salvato in: {model_path}")

if __name__ == "__main__":
    train()
