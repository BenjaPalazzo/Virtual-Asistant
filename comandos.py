import subprocess
import webbrowser
from voz import hablar, escuchar, detectar_y_guardar_info, leer_memoria
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from difflib import get_close_matches

# Cohere


# API Key de Cohere


# Spotify
CLIENT_ID = "00860fe8e5c648a79ddc86f6ae0c8f14"
CLIENT_SECRET = "eb9475793c584305be9307d2e467e936"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

# Diccionario de apps para Linux
APLICACIONES = {
    "discord":      "discord",
    "steam":        "steam",
    "spotify":      "spotify",
    "calculadora":  "gnome-calculator",
    "navegador":    "xdg-open https://www.google.com",
    "terminal":     "gnome-terminal",
    "archivos":     "nautilus",
}

def saludo_personalizado():
    memoria = leer_memoria()
    nombre = memoria.get("nombre", None)
    if nombre:
        hablar(f"Hola {nombre}, ¿en qué te puedo ayudar hoy?")
    else:
        hablar("Hola, ¿cómo te llamás?")

def saludar():
    memoria = leer_memoria()
    nombre = memoria.get("nombre")
    if nombre:
        hablar(f"Hola {nombre}, ¿en qué te puedo ayudar hoy?")
    else:
        hablar("Hola, ¿cómo te llamás?")

def guardar_nombre(texto):
    return detectar_y_guardar_info(texto)

def abrir_aplicacion(nombre):
    nombre = nombre.lower()
    coincidencias = get_close_matches(nombre, APLICACIONES.keys(), n=1, cutoff=0.6)
    if coincidencias:
        app = coincidencias[0]
        try:
            subprocess.Popen(APLICACIONES[app].split())
            hablar(f"Abriendo {app}.")
        except Exception as e:
            hablar(f"No pude abrir {app}.")
            print(f"Error: {e}")
    else:
        hablar(f"No encontré ninguna aplicación parecida a {nombre}.")

def abrir_spotify():
    try:
        subprocess.Popen(["spotify"])
        hablar("Abriendo Spotify.")
    except FileNotFoundError:
        # Intentar con snap
        try:
            subprocess.Popen(["snap", "run", "spotify"])
            hablar("Abriendo Spotify.")
        except Exception:
            hablar("No encontré Spotify instalado.")

def pausar_spotify():
    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=SCOPE,
                open_browser=False,
                cache_path=".cache",
            )
        )
        sp.pause_playback()
        hablar("Pausé la música.")
    except Exception as e:
        print("Error al pausar Spotify:", e)
        hablar("No pude pausar la música.")

def reanudar_spotify():
    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=SCOPE,
                open_browser=False,
                cache_path=".cache",
            )
        )
        sp.start_playback()
        hablar("Reanudé la reproducción.")
    except Exception as e:
        print("Error al reanudar Spotify:", e)
        hablar("No pude reanudar la música.")

def siguiente_spotify():
    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=SCOPE,
                open_browser=False,
                cache_path=".cache",
            )
        )
        sp.next_track()
        hablar("Pasé a la siguiente canción.")
    except Exception as e:
        print("Error al cambiar canción:", e)
        hablar("No pude cambiar la canción.")

def reproducir_cancion_spotify():
    hablar("¿Qué canción querés que reproduzca?")
    nombre_cancion = escuchar()
    if not nombre_cancion:
        hablar("No entendí el nombre de la canción.")
        return
    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=SCOPE,
                open_browser=False,
                cache_path=".cache",
            )
        )
        resultados = sp.search(q=nombre_cancion, type="track", limit=1)
        if resultados["tracks"]["items"]:
            cancion = resultados["tracks"]["items"][0]
            uri = cancion["uri"]
            nombre = cancion["name"]
            artista = cancion["artists"][0]["name"]
            dispositivos = sp.devices()
            if dispositivos["devices"]:
                device_id = dispositivos["devices"][0]["id"]
                sp.start_playback(device_id=device_id, uris=[uri])
                hablar(f"Reproduciendo {nombre} de {artista}.")
            else:
                hablar("No encontré un dispositivo de reproducción activo.")
        else:
            hablar("No encontré esa canción en Spotify.")
    except Exception as e:
        print(f"Error: {e}")
        hablar("Ocurrió un error al intentar reproducir la canción.")

def controlar_volumen(direccion):
    """Control de volumen usando amixer (nativo en Linux)."""
    try:
        if direccion == "subir":
            subprocess.run(["amixer", "-q", "sset", "Master", "10%+"])
            hablar("Subí el volumen.")
        elif direccion == "bajar":
            subprocess.run(["amixer", "-q", "sset", "Master", "10%-"])
            hablar("Bajé el volumen.")
        elif direccion == "silenciar":
            subprocess.run(["amixer", "-q", "sset", "Master", "mute"])
            hablar("Volumen silenciado.")
        elif direccion == "activar":
            subprocess.run(["amixer", "-q", "sset", "Master", "unmute"])
            hablar("Volumen activado.")
        else:
            hablar("No entendí el comando para el volumen.")
    except Exception as e:
        print(f"Error al controlar volumen: {e}")
        hablar("No pude controlar el volumen.")

def tomar_nota():
    hablar("¿Qué querés que anote?")
    nota = escuchar()
    if nota:
        with open("notas.txt", "a", encoding="utf-8") as f:
            f.write(nota + "\n")
        hablar("Nota guardada.")
    else:
        hablar("No entendí la nota.")

def buscar_en_google():
    hablar("¿Qué querés buscar?")
    consulta = escuchar()
    if consulta:
        url = f"https://www.google.com/search?q={consulta.replace(' ', '+')}"
        webbrowser.open(url)
        hablar(f"Buscando {consulta} en Google.")
    else:
        hablar("No entendí la búsqueda.")

def cargar_historial():
    if os.path.exists("charlas.txt"):
        with open("charlas.txt", "r", encoding="utf-8") as f:
            return f.read()
    return ""

def guardar_en_historial(usuario, respuesta):
    with open("charlas.txt", "a", encoding="utf-8") as f:
        f.write(f"Usuario: {usuario}\nAsistente: {respuesta}\n\n")


    hablar("Modo conversación inteligente activado.")
    contexto = "A partir de ahora, respondé siempre en español.\n\n"
    contexto += cargar_historial()
    while True:
        entrada = escuchar()
        if not entrada:
            hablar("No entendí, ¿podés repetir?")
            continue
        if entrada in ["chau", "salir", "cerrar"]:
            hablar("Terminando la conversación.")
            break
        prompt = contexto + f"Usuario: {entrada}\nAsistente:"
        respuesta = (
            co.generate(model="command", prompt=prompt, max_tokens=150, temperature=0.7)
            .generations[0]
            .text.strip()
        )
        hablar(respuesta)
        guardar_en_historial(entrada, respuesta)
        contexto += f"Usuario: {entrada}\nAsistente: {respuesta}\n"
