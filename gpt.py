import os
import json
from dotenv import load_dotenv
from groq import Groq
from voz import hablar, escuchar

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODELO = "llama-3.3-70b-versatile"
HISTORIAL_PATH = "historial.json"

SYSTEM_PROMPT = (
    "Sos Pepe, el asistente personal de Benja. "
    "Respondé siempre en español rioplatense, de forma clara y concisa. "
    "Sos amigable, directo y un poco informal. "
    "Tus respuestas deben ser cortas — máximo 3 oraciones — porque se van a leer en voz alta. "
    "Tenés memoria de conversaciones anteriores con Benja, usala para dar respuestas más personalizadas."
)

# -------- Historial persistente --------
def cargar_historial():
    if os.path.exists(HISTORIAL_PATH):
        try:
            with open(HISTORIAL_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def guardar_historial(historial):
    # Guardamos solo los últimos 100 mensajes para no crecer infinito
    historial_recortado = historial[-100:]
    with open(HISTORIAL_PATH, "w", encoding="utf-8") as f:
        json.dump(historial_recortado, f, ensure_ascii=False, indent=2)

def get_mensajes_con_system(historial):
    return [{"role": "system", "content": SYSTEM_PROMPT}] + historial

# -------- Consulta puntual --------
def consultar_groq(pregunta, guardar=True):
    historial = cargar_historial()
    historial.append({"role": "user", "content": pregunta})

    try:
        respuesta = client.chat.completions.create(
            model=MODELO,
            messages=get_mensajes_con_system(historial),
            temperature=0.7,
            max_tokens=200,
        )
        texto = respuesta.choices[0].message.content.strip()
        historial.append({"role": "assistant", "content": texto})

        if guardar:
            guardar_historial(historial)

        return texto
    except Exception as e:
        print(f"⚠️ Error Groq: {e}")
        return "Lo siento, tuve un problema al conectarme."

# -------- Modo conversación continua --------
def charla_con_groq():
    historial = cargar_historial()
    hablar("Modo conversación activado. Decime lo que quieras, decí 'salir' para terminar.")

    while True:
        entrada = escuchar()
        if not entrada:
            hablar("No entendí, ¿podés repetir?")
            continue

        if any(p in entrada for p in ["salir", "chau", "basta", "terminar"]):
            hablar("Cerrando conversación.")
            break

        historial.append({"role": "user", "content": entrada})

        try:
            respuesta = client.chat.completions.create(
                model=MODELO,
                messages=get_mensajes_con_system(historial),
                temperature=0.7,
                max_tokens=200,
            )
            texto = respuesta.choices[0].message.content.strip()
            historial.append({"role": "assistant", "content": texto})
            guardar_historial(historial)
            hablar(texto)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            hablar("Tuve un problema al responder.")