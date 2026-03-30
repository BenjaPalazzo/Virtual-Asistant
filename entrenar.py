import os
import numpy as np
import librosa
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report

# -------- Configuración --------
DATASET_PATH = "dataset"
MODEL_PATH   = "modelo_emociones.pkl"
ENCODER_PATH = "encoder_emociones.pkl"
SCALER_PATH  = "scaler_emociones.pkl"

# Emociones RAVDESS
EMOCIONES = {
    "01": "neutral",
    "02": "calma",
    "03": "feliz",
    "04": "triste",
    "05": "enojado",
    "06": "miedo",
    "07": "disgusto",
    "08": "sorpresa",
}

# -------- Extraer features --------
def extraer_features(ruta_audio):
    try:
        audio, sr = librosa.load(ruta_audio, duration=3, offset=0.5)

        # MFCC
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
        mfcc_mean = np.mean(mfcc.T, axis=0)

        # Chroma
        chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
        chroma_mean = np.mean(chroma.T, axis=0)

        # Mel spectrogram
        mel = librosa.feature.melspectrogram(y=audio, sr=sr)
        mel_mean = np.mean(mel.T, axis=0)

        return np.concatenate([mfcc_mean, chroma_mean, mel_mean])
    except Exception as e:
        print(f"⚠️  Error procesando {ruta_audio}: {e}")
        return None

# -------- Cargar dataset --------
def cargar_dataset():
    X, y = [], []
    total = 0

    actores = sorted(os.listdir(DATASET_PATH))
    for actor in actores:
        actor_path = os.path.join(DATASET_PATH, actor)
        if not os.path.isdir(actor_path):
            continue

        for archivo in os.listdir(actor_path):
            if not archivo.endswith(".wav"):
                continue

            partes = archivo.split("-")
            if len(partes) < 3:
                continue

            emocion = EMOCIONES.get(partes[2])
            if not emocion:
                continue

            features = extraer_features(os.path.join(actor_path, archivo))
            if features is not None:
                X.append(features)
                y.append(emocion)
                total += 1

        print(f"✅ {actor} procesado ({total} audios)")

    return np.array(X), np.array(y)

# -------- Entrenar --------
def entrenar():
    print("\n🧠 Procesando dataset...")
    print("Esto puede tardar unos minutos.\n")

    X, y = cargar_dataset()
    print(f"\n📊 {len(X)} audios cargados — {len(np.unique(y))} emociones")
    print(f"Emociones: {np.unique(y)}\n")

    # Encodear etiquetas
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    # Normalizar features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded,
        test_size=0.2,
        random_state=42,
        stratify=y_encoded
    )

    print(f"🔀 Train: {len(X_train)} | Test: {len(X_test)}\n")

    # -------- Red neuronal liviana --------
    modelo = MLPClassifier(
        hidden_layer_sizes=(256, 128, 64),
        activation="relu",
        solver="adam",
        max_iter=200,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=15,
        random_state=42,
        verbose=True,
    )

    print("🚀 Entrenando red neuronal...\n")
    modelo.fit(X_train, y_train)

    # -------- Evaluación --------
    acc = modelo.score(X_test, y_test)
    y_pred = modelo.predict(X_test)

    print(f"\n✅ Precisión final: {acc * 100:.1f}%\n")
    print(classification_report(y_test, y_pred, target_names=encoder.classes_))

    # -------- Guardar modelo --------
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(modelo, f)
    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(encoder, f)
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    print(f"💾 Modelo guardado en: {MODEL_PATH}")
    print(f"💾 Encoder guardado en: {ENCODER_PATH}")
    print(f"💾 Scaler guardado en: {SCALER_PATH}")
    print("\n🎉 Listo para integrar a Pepe.")

if __name__ == "__main__":
    entrenar()