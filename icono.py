import pystray
from PIL import Image
import sys
from voz import hablar  


def on_quit(icon):
    hablar("Cerrando el programa. Hasta luego.")
    icon.stop()
    sys.exit()


def crear_icono():
    image = Image.open(r"C:\Users\Usuario\Desktop\Nova\nova.ico")
    menu = pystray.Menu(pystray.MenuItem("Salir", on_quit))
    icon = pystray.Icon("nova", image, "Nova Asistente", menu)
    icon.run_detached()
    return icon
