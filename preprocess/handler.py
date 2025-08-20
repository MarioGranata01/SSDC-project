import pandas as pd
import os
import joblib

RAW_DIR = "/data/raw"
PROCESSED_DIR = "/data/processed"
ENCODERS_DIR = "/data/encoders"

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(ENCODERS_DIR, exist_ok=True)

for filename in os.listdir(RAW_DIR):
    filepath = os.path.join(RAW_DIR, filename)
    if os.path.isfile(filepath):
        # Leggi senza header, poi assegna nomi
        df = pd.read_csv(filepath, header=None)
        df.columns = ['buying','maint','doors','persons','lug_boot','safety','class']

        # Pulizia valori strani tipo "vhigh.1" -> "vhigh"
        df = df.applymap(lambda x: str(x).split('.')[0] if isinstance(x, str) else x)
        df = df.dropna()

        # Codifica tutte le colonne categoriche in numeri
        encoders = {}
        for col in df.columns:
            df[col] = df[col].astype('category')
            encoders[col] = dict(zip(df[col].cat.categories, range(len(df[col].cat.categories))))
            df[col] = df[col].cat.codes

        # salva CSV processato senza header e senza indice
        df.to_csv(os.path.join(PROCESSED_DIR, filename), index=False, header=False)

        # salva encoders
        joblib.dump(encoders, os.path.join(ENCODERS_DIR, f"{filename}_encoders.joblib"))

        print(f"Processed {filename}")
