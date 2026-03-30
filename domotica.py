import serial
import time
from voz import hablar

# Puerto serial del Arduino en Linux
# Si no funciona, probá con /dev/ttyUSB0
PUERTO = "/dev/ttyUSB0"
BAUDRATE = 9600

def conectar_arduino():
    try:
        arduino = serial.Serial(PUERTO, BAUDRATE, timeout=2)
        time.sleep(2)  # Esperar que el Arduino inicialice
        print("✅ Arduino conectado en", PUERTO)
        return arduino
    except Exception as e:
        print(f"❌ No se pudo conectar al Arduino: {e}")
        return None

def enviar_comando(arduino, comando):
    if arduino and arduino.is_open:
        arduino.write((comando + '\n').encode())
        time.sleep(0.3)
        if arduino.in_waiting:
            respuesta = arduino.readline().decode().strip()
            print(f"Arduino respondió: {respuesta}")
    else:
        print("❌ Arduino no conectado")

# Instancia global del Arduino
_arduino = None

def get_arduino():
    global _arduino
    if _arduino is None or not _arduino.is_open:
        _arduino = conectar_arduino()
    return _arduino

def prender_luz():
    arduino = get_arduino()
    if arduino:
        enviar_comando(arduino, "LUZ_ON")
        hablar("Luz encendida.")
    else:
        hablar("No pude conectarme al Arduino.")

def apagar_luz():
    arduino = get_arduino()
    if arduino:
        enviar_comando(arduino, "LUZ_OFF")
        hablar("Luz apagada.")
    else:
        hablar("No pude conectarme al Arduino.")