import pickle
import numpy as np
import librosa
import sounddevice as sd
import soundfile as sf
import tempfile
import os

# -------- Cargar modelo --------
MODEL_PATH   = "modelo_emociones.pkl"
ENCODER_PATH = "encoder_emociones.pkl"
SCALER_PATH  = "scaler_emociones.pkl"

try:
    with open(MODEL_PATH, "rb") as f:
        modelo = pickle.load(f)
    with open(ENCODER_PATH, "rb") as f:
        encoder = pickle.load(f)
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    print("✅ Modelo de emociones cargado")
except Exception as e:
    print(f"⚠️  No se pudo cargar el modelo de emociones: {e}")
    modelo = None

# -------- Extraer features (igual que en entrenar.py) --------
def extraer_features(ruta_audio):
    try:
        audio, sr = librosa.load(ruta_audio, duration=3, offset=0.5)
        mfcc  = np.mean(librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40).T, axis=0)
        chroma = np.mean(librosa.feature.chroma_stft(y=audio, sr=sr).T, axis=0)
        mel   = np.mean(librosa.feature.melspectrogram(y=audio, sr=sr).T, axis=0)
        return np.concatenate([mfcc, chroma, mel])
    except:
        return None

# -------- Grabar audio del micrófono --------
def grabar_audio(segundos=3, sr=22050):
    print("🎙️ Grabando para detectar emoción...")
    audio = sd.rec(int(segundos * sr), samplerate=sr, channels=1, dtype="float32")
    sd.wait()
    tmp = tempfile.mktemp(suffix=".wav")
    sf.write(tmp, audio, sr)
    return tmp

# -------- Detectar emoción --------
def detectar_emocion(ruta_audio=None):
    if modelo is None:
        return "desconocido"

    # Si no se pasa audio, grabamos del micrófono
    grabado = False
    if ruta_audio is None:
        ruta_audio = grabar_audio()
        grabado = True

    features = extraer_features(ruta_audio)
    if features is None:
        return "desconocido"

    features_scaled = scaler.transform([features])
    pred = modelo.predict(features_scaled)[0]
    emocion = encoder.inverse_transform([pred])[0]

    if grabado:
        os.remove(ruta_audio)

    return emocion

# -------- Respuesta adaptada a la emoción --------
RESPUESTAS_EMOCION = {
    "enojado":  "Noto que estás un poco enojado. ¿Qué pasó?",
    "triste":   "Parece que no estás muy bien. ¿Querés contarme algo?",
    "feliz":    "Me alegra escucharte bien. ¿En qué te puedo ayudar?",
    "miedo":    "Tranquilo, acá estoy. ¿Qué necesitás?",
    "sorpresa": "¡Parece que algo te sorprendió! ¿Qué pasó?",
    "calma":    "Todo tranquilo. ¿En qué te ayudo?",
    "disgusto": "Parece que algo no te está gustando. Contame.",
    "neutral":  "¿En qué te puedo ayudar?",
}

def responder_segun_emocion(emocion):
    return RESPUESTAS_EMOCION.get(emocion, "¿En qué te puedo ayudar?")