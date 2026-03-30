import speech_recognition as sr
import json
import os
import sys
import asyncio
import edge_tts
import subprocess

# -------- Utilidad para impresión segura --------
def print_seguro(texto):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        print(texto)
    except Exception:
        print(texto.encode('ascii', errors='ignore').decode())

# -------- Configuración --------
MEMORIA_PATH = "memoria.json"
HOTWORD = "pepe"

# Voz de edge-tts
VOZ = "es-MX-DaliaNeural"
# Otras opciones:
# "es-AR-ElenaNeural"   → Mujer argentina
# "es-ES-ElviraNeural"  → Mujer española
# "es-CO-SalomeNeural"  → Mujer colombiana

# -------- Bloqueo de micrófono --------
_hablando = False

def set_hablando(valor: bool):
    global _hablando
    _hablando = valor

# -------- Texto a voz (edge-tts) --------
async def _hablar_async(texto):
    comunicar = edge_tts.Communicate(texto, VOZ)
    await comunicar.save("/tmp/pepe_voz.mp3")

def hablar(texto):
    try:
        print_seguro(f"🗣️ {texto}")
    except Exception:
        print(texto)
    asyncio.run(_hablar_async(texto))
    subprocess.run(
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "/tmp/pepe_voz.mp3"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

# -------- Voz a texto --------
def escuchar():
    # No escuchar mientras Pepe está hablando
    if _hablando:
        return ""

    r = sr.Recognizer()
    r.pause_threshold = 1.5
    r.phrase_threshold = 0.3
    r.non_speaking_duration = 0.8

    with sr.Microphone() as source:
        print_seguro("🎧 Escuchando...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source, timeout=10, phrase_time_limit=15)
    try:
        texto = r.recognize_google(audio, language="es-ES").lower()
        print_seguro(f"🗣️ Usted dijo: {texto}")
        return texto
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "No puedo conectarme al servicio de reconocimiento de voz."
    except sr.WaitTimeoutError:
        return ""

# -------- Memoria --------
def leer_memoria():
    if not os.path.exists(MEMORIA_PATH):
        return {}
    with open(MEMORIA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_memoria(data):
    with open(MEMORIA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def actualizar_memoria(clave, valor):
    memoria = leer_memoria()
    memoria[clave] = valor
    guardar_memoria(memoria)

# -------- Detección de datos --------
def extraer_nombre(texto):
    import re
    match = re.search(r"(me llamo|llamame|soy) (\w+)", texto)
    if match:
        nombre = match.group(2).capitalize()
        actualizar_memoria("nombre", nombre)
        return nombre
    return None

def extraer_color_favorito(texto):
    import re
    match = re.search(r"color favorito es (\w+)", texto)
    if match:
        color = match.group(1).lower()
        actualizar_memoria("color_favorito", color)
        return color
    return None

def extraer_gusto_musical(texto):
    import re
    match = re.search(r"me gusta (el )?(\w+)", texto)
    if match:
        gusto = match.group(2).lower()
        memoria = leer_memoria()
        gustos = memoria.get("gustos_musicales", [])
        if gusto not in gustos:
            gustos.append(gusto)
            actualizar_memoria("gustos_musicales", gustos)
        return gusto
    return None

def detectar_y_guardar_info(texto):
    return (
        extraer_nombre(texto)
        or extraer_color_favorito(texto)
        or extraer_gusto_musical(texto)
    )

def detectar_hotword(texto):
    return HOTWORD in texto