import os
import time
import threading
import webbrowser
import requests
from datetime import datetime
from dotenv import load_dotenv
from voz import hablar

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CIUDAD = "Mendoza"  # Cambiá si querés otra ciudad

# -------- HORA Y FECHA --------
def decir_hora():
    ahora = datetime.now()
    hora = ahora.strftime("%H:%M")
    fecha = ahora.strftime("%d de %B de %Y")
    hablar(f"Son las {hora} del {fecha}.")

# -------- CLIMA --------
def decir_clima():
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={CIUDAD}&appid={OPENWEATHER_API_KEY}&units=metric&lang=es"
        )
        r = requests.get(url, timeout=5)
        data = r.json()

        if r.status_code != 200:
            hablar("No pude obtener el clima en este momento.")
            return

        temp = round(data["main"]["temp"])
        sensacion = round(data["main"]["feels_like"])
        descripcion = data["weather"][0]["description"]
        humedad = data["main"]["humidity"]

        hablar(
            f"En {CIUDAD} hay {temp} grados, se siente como {sensacion}. "
            f"{descripcion.capitalize()}, con {humedad} por ciento de humedad."
        )
    except Exception as e:
        print(f"⚠️ Error clima: {e}")
        hablar("No pude conectarme al servicio del clima.")

# -------- TIMER --------
def _contar_timer(segundos):
    time.sleep(segundos)
    hablar(f"¡Tiempo! El temporizador de {segundos // 60} minutos terminó.")

def poner_timer(texto):
    """Extrae los minutos del texto y arranca el timer en un hilo."""
    import re
    match = re.search(r"(\d+)\s*(minuto|min|segundo|seg)", texto)
    if not match:
        hablar("No entendí cuánto tiempo querés. Decime por ejemplo: timer de 5 minutos.")
        return

    cantidad = int(match.group(1))
    unidad = match.group(2)

    if "seg" in unidad:
        segundos = cantidad
        hablar(f"Timer de {cantidad} segundos activado.")
    else:
        segundos = cantidad * 60
        hablar(f"Timer de {cantidad} minutos activado.")

    hilo = threading.Thread(target=_contar_timer, args=(segundos,), daemon=True)
    hilo.start()

# -------- ABRIR SITIOS WEB --------
SITIOS = {
    "youtube":    "https://www.youtube.com",
    "google":     "https://www.google.com",
    "github":     "https://www.github.com",
    "twitter":    "https://www.twitter.com",
    "reddit":     "https://www.reddit.com",
    "wikipedia":  "https://www.wikipedia.org",
    "spotify":    "https://open.spotify.com",
    "gmail":      "https://mail.google.com",
    "netflix":    "https://www.netflix.com",
    "chatgpt":    "https://chat.openai.com",
}

def abrir_sitio(texto):
    from difflib import get_close_matches
    palabras = texto.split()
    for palabra in palabras:
        coincidencias = get_close_matches(palabra, SITIOS.keys(), n=1, cutoff=0.6)
        if coincidencias:
            sitio = coincidencias[0]
            webbrowser.open(SITIOS[sitio])
            hablar(f"Abriendo {sitio}.")
            return
    hablar("No encontré ese sitio. Podés pedirme YouTube, Google, GitHub, Twitter y más.")