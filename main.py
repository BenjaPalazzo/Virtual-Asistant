import sys
import logging
import threading
import time
from interfaz import iniciar_ui, get_ui
from comandos import (
    abrir_spotify, tomar_nota, buscar_en_google,
    reproducir_cancion_spotify, pausar_spotify, reanudar_spotify,
    siguiente_spotify, controlar_volumen, abrir_aplicacion,
    guardar_nombre, saludar,
)
from gpt import charla_con_groq, consultar_groq
from domotica import prender_luz, apagar_luz
from funciones import decir_hora, decir_clima, poner_timer, abrir_sitio
from emociones import detectar_emocion, responder_segun_emocion
from voz import hablar as _hablar_original, escuchar, detectar_hotword, set_hablando

logging.basicConfig(
    filename='error.log', filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

# -------- Hablar con UI y bloqueo de micrófono -------
def hablar(texto):
    ui = get_ui()
    if ui:
        ui.agregar_mensaje("pepe", texto)
        ui.set_estado("hablando")
    set_hablando(True)
    _hablar_original(texto)
    set_hablando(False)
    if ui:
        ui.set_estado("esperando")

def escuchar_con_ui(hotword=False):
    ui = get_ui()
    if ui:
        ui.set_estado("esperando" if hotword else "escuchando")
    texto = escuchar()
    if ui and not hotword:
        ui.set_estado("esperando")
        if texto:
            ui.agregar_mensaje("user", texto)
    return texto

# -------- Procesar comando (voz o teclado) --------
def procesar_comando(texto):
    if not texto:
        return

    texto = texto.lower().strip()

    if guardar_nombre(texto):
        return

    if any(p in texto for p in ["salir", "chau", "basta"]):
        hablar("Modo conversación finalizado. Quedo a la espera.")
        return

    if any(p in texto for p in ["cerrar programa", "cerrar el programa", "cerrate"]):
        hablar("Cerrando el programa. Hasta luego.")
        sys.exit()

    match True:
        case _ if any(p in texto for p in ["prender luz", "encendé la luz", "enciende la luz"]):
            prender_luz()

        case _ if any(p in texto for p in ["apagar luz", "apagá la luz", "apaga la luz"]):
            apagar_luz()

        case _ if any(p in texto for p in ["qué hora", "que hora", "qué día", "que dia"]):
            decir_hora()

        case _ if any(p in texto for p in ["clima", "tiempo", "temperatura", "llueve"]):
            decir_clima()

        case _ if any(p in texto for p in ["timer", "temporizador", "alarma"]):
            poner_timer(texto)

        case _ if any(p in texto for p in ["cómo me ves", "qué emoción", "como me ves", "como me siento"]):
            emocion = detectar_emocion()
            respuesta = responder_segun_emocion(emocion)
            hablar(f"Detecto que estás {emocion}. {respuesta}")

        case _ if any(p in texto for p in ["reproducí", "poné una canción", "quiero escuchar", "reproducir"]):
            reproducir_cancion_spotify()

        case _ if "pausá" in texto or "pausar" in texto:
            pausar_spotify()

        case _ if "reanudar" in texto or "seguí" in texto:
            reanudar_spotify()

        case _ if "siguiente" in texto or "adelantar" in texto:
            siguiente_spotify()

        case _ if "spotify" in texto:
            abrir_spotify()

        case _ if "subí" in texto or "más volumen" in texto:
            controlar_volumen("subir")

        case _ if "bajá" in texto or "menos volumen" in texto:
            controlar_volumen("bajar")

        case _ if "silenciar" in texto or "mute" in texto:
            controlar_volumen("silenciar")

        case _ if "activar volumen" in texto or "quitar silencio" in texto:
            controlar_volumen("activar")

        case _ if "nota" in texto or "anotá" in texto:
            tomar_nota()

        case _ if "buscá" in texto or "buscar" in texto:
            buscar_en_google()

        case _ if any(p in texto for p in ["charlemos", "quiero hablar", "conversemos"]):
            charla_con_groq()

        case _ if any(s in texto for s in ["youtube", "google", "github", "twitter", "reddit", "netflix", "gmail"]):
            abrir_sitio(texto)

        case _:
            respuesta = consultar_groq(texto)
            hablar(respuesta)

# -------- Hotword --------
def esperar_hotword():
    ui = get_ui()
    if ui:
        ui.set_estado("esperando")
    while True:
        texto = escuchar_con_ui(hotword=True)
        if texto and detectar_hotword(texto):
            return

# -------- Modo activo por voz --------
def modo_activo():
    saludar()
    while True:
        texto = escuchar_con_ui()
        if not texto:
            continue
        procesar_comando(texto)

# -------- Hilo principal del asistente --------
def main():
    try:
        while True:
            esperar_hotword()
            modo_activo()
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        logging.error("Error inesperado", exc_info=True)
        sys.exit()


if __name__ == "__main__":
    def on_texto_teclado(texto):
        procesar_comando(texto)

    # Lanzar hilo del asistente
    hilo = threading.Thread(target=main, daemon=True)
    hilo.start()

    # Esperar que la UI arranque y registrar callback
    def registrar_callback():
        time.sleep(1.0)
        ui = get_ui()
        if ui:
            ui.set_on_texto(on_texto_teclado)

    threading.Thread(target=registrar_callback, daemon=True).start()

    # Interfaz en hilo principal (tkinter lo requiere)
    iniciar_ui()
    sys.exit()