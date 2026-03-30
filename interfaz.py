import tkinter as tk
from tkinter import scrolledtext
import threading
import math
import time
import sys

# -------- Colores --------
BG_COLOR     = "#0d0d0d"
CIRCLE_COLOR = "#0a3d6b"
CIRCLE_PULSE = "#1a7abf"
TEXT_BG      = "#111827"
TEXT_BORDER  = "#1e3a5f"
USER_COLOR   = "#60a5fa"
PEPE_COLOR   = "#38bdf8"
TIME_COLOR   = "#4b5563"
INPUT_BG     = "#1a2332"
INPUT_FG     = "#e2e8f0"
BTN_COLOR    = "#1a7abf"

FONT_CHAT  = ("Consolas", 11)
FONT_TITLE = ("Consolas", 14, "bold")

class StarkIndustriesUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Starks Industries — Pepe")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("960x640")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", lambda: sys.exit())

        self.estado = "esperando"
        self.pulse_radio = 0
        self.pulse_dir = 1
        self.wave_offset = 0

        # Callback para cuando el usuario manda texto por teclado
        self.on_texto_callback = None

        self._build_ui()
        self._animar()

    def _build_ui(self):
        # ---- Panel izquierdo ----
        self.left = tk.Frame(self.root, bg=BG_COLOR, width=360)
        self.left.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 10), pady=20)
        self.left.pack_propagate(False)

        tk.Label(self.left, text="STARKS INDUSTRIES",
                 bg=BG_COLOR, fg="#38bdf8", font=FONT_TITLE).pack(pady=(10, 2))
        tk.Label(self.left, text="Sistema J.A.R.V.I.S  v1.0",
                 bg=BG_COLOR, fg=TIME_COLOR, font=("Consolas", 9)).pack(pady=(0, 15))

        self.canvas = tk.Canvas(self.left, width=300, height=300,
                                bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()

        self.estado_label = tk.Label(self.left, text="● EN ESPERA",
                                     bg=BG_COLOR, fg=TIME_COLOR,
                                     font=("Consolas", 10))
        self.estado_label.pack(pady=(14, 0))

        # ---- Panel derecho ----
        self.right = tk.Frame(self.root, bg=BG_COLOR)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True,
                        padx=(10, 20), pady=20)

        tk.Label(self.right, text="REGISTRO DE CONVERSACIÓN",
                 bg=BG_COLOR, fg="#38bdf8",
                 font=("Consolas", 10, "bold")).pack(anchor="w", pady=(10, 6))

        # Chat
        self.chat = scrolledtext.ScrolledText(
            self.right, bg=TEXT_BG, fg="#e2e8f0",
            font=FONT_CHAT, relief=tk.FLAT, bd=0,
            wrap=tk.WORD, state=tk.DISABLED, cursor="arrow",
        )
        self.chat.pack(fill=tk.BOTH, expand=True)
        self.chat.tag_config("user", foreground=USER_COLOR)
        self.chat.tag_config("pepe", foreground=PEPE_COLOR)
        self.chat.tag_config("time", foreground=TIME_COLOR)
        self.chat.tag_config("sep",  foreground="#1e3a5f")

        # ---- Input de teclado ----
        input_frame = tk.Frame(self.right, bg=BG_COLOR)
        input_frame.pack(fill=tk.X, pady=(8, 0))

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_frame,
            textvariable=self.input_var,
            bg=INPUT_BG, fg=INPUT_FG,
            insertbackground=INPUT_FG,
            font=("Consolas", 11),
            relief=tk.FLAT,
            bd=6,
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        self.input_entry.bind("<Return>", self._enviar_texto)
        self.input_entry.insert(0, "Escribí un comando o pregunta...")
        self.input_entry.bind("<FocusIn>", self._limpiar_placeholder)
        self.input_entry.bind("<FocusOut>", self._restaurar_placeholder)
        self.input_entry.config(fg="#4b5563")

        btn = tk.Button(
            input_frame, text="Enviar",
            bg=BTN_COLOR, fg="white",
            font=("Consolas", 10, "bold"),
            relief=tk.FLAT, padx=14, pady=6,
            cursor="hand2",
            command=self._enviar_texto,
        )
        btn.pack(side=tk.RIGHT, padx=(6, 0))

    def _limpiar_placeholder(self, event):
        if self.input_entry.get() == "Escribí un comando o pregunta...":
            self.input_entry.delete(0, tk.END)
            self.input_entry.config(fg=INPUT_FG)

    def _restaurar_placeholder(self, event):
        if not self.input_entry.get():
            self.input_entry.insert(0, "Escribí un comando o pregunta...")
            self.input_entry.config(fg="#4b5563")

    def _enviar_texto(self, event=None):
        texto = self.input_var.get().strip()
        if not texto or texto == "Escribí un comando o pregunta...":
            return
        self.input_entry.delete(0, tk.END)
        self.agregar_mensaje("user", texto)
        if self.on_texto_callback:
            threading.Thread(
                target=self.on_texto_callback,
                args=(texto,),
                daemon=True
            ).start()

    # -------- Animación --------
    def _animar(self):
        self.canvas.delete("all")
        cx, cy, r = 150, 150, 90

        if self.estado == "esperando":
            self._circulo_idle(cx, cy, r)
        elif self.estado == "escuchando":
            self._circulo_escucha(cx, cy, r)
        elif self.estado == "hablando":
            self._circulo_ondas(cx, cy, r)

        self.wave_offset += 0.12
        self.root.after(40, self._animar)

    def _circulo_idle(self, cx, cy, r):
        self.pulse_radio += 0.4 * self.pulse_dir
        if self.pulse_radio > 8 or self.pulse_radio < 0:
            self.pulse_dir *= -1
        pr = r + self.pulse_radio
        self.canvas.create_oval(cx-pr, cy-pr, cx+pr, cy+pr,
                                outline=CIRCLE_COLOR, width=1.5)
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                                fill=CIRCLE_COLOR, outline=CIRCLE_PULSE, width=2)
        self.canvas.create_text(cx, cy, text="PEPE",
                                fill="#38bdf8", font=("Consolas", 18, "bold"))

    def _circulo_escucha(self, cx, cy, r):
        self.pulse_radio += 1.2 * self.pulse_dir
        if self.pulse_radio > 15 or self.pulse_radio < 0:
            self.pulse_dir *= -1
        pr = r + self.pulse_radio
        self.canvas.create_oval(cx-pr, cy-pr, cx+pr, cy+pr,
                                outline="#1a7abf", width=1)
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                                fill="#0a3d6b", outline="#38bdf8", width=2.5)
        self.canvas.create_text(cx, cy-10, text="🎧",
                                fill="#38bdf8", font=("Consolas", 24))
        self.canvas.create_text(cx, cy+22, text="ESCUCHANDO",
                                fill="#38bdf8", font=("Consolas", 10))

    def _circulo_ondas(self, cx, cy, r):
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                                fill=CIRCLE_COLOR, outline=CIRCLE_PULSE, width=2)
        puntos = 80
        for i in range(3):
            freq = 2.5 + i * 0.8
            color = ["#1a7abf", "#38bdf8", "#7dd3fc"][i]
            coords = []
            for j in range(puntos + 1):
                x = cx - r + (2 * r * j / puntos)
                dx = x - cx
                if abs(dx) > r:
                    continue
                max_y = math.sqrt(max(0, r**2 - dx**2)) * 0.75
                y = cy + max_y * math.sin(
                    freq * math.pi * j / puntos + self.wave_offset + i * 1.2
                ) * 0.6
                coords.extend([x, y])
            if len(coords) >= 4:
                self.canvas.create_line(coords, fill=color,
                                        width=2 - i * 0.4, smooth=True)
        self.canvas.create_text(cx, cy+r+16, text="HABLANDO",
                                fill="#38bdf8", font=("Consolas", 10))

    # -------- API pública --------
    def set_estado(self, estado):
        self.estado = estado
        labels = {
            "esperando":  ("● EN ESPERA",  TIME_COLOR),
            "escuchando": ("● ESCUCHANDO", "#38bdf8"),
            "hablando":   ("● HABLANDO",   PEPE_COLOR),
        }
        texto, color = labels.get(estado, ("● EN ESPERA", TIME_COLOR))
        self.estado_label.config(text=texto, fg=color)

    def agregar_mensaje(self, quien, texto):
        self.chat.config(state=tk.NORMAL)
        hora = time.strftime("%H:%M:%S")
        prefijo = "Vos" if quien == "user" else "Pepe"
        self.chat.insert(tk.END, f"\n[{hora}] ", "time")
        self.chat.insert(tk.END, f"{prefijo}:\n", quien)
        self.chat.insert(tk.END, f"  {texto}\n", quien)
        self.chat.insert(tk.END, "  " + "─" * 40 + "\n", "sep")
        self.chat.config(state=tk.DISABLED)
        self.chat.see(tk.END)

    def set_on_texto(self, callback):
        """Registra el callback que se llama cuando el usuario manda texto por teclado."""
        self.on_texto_callback = callback


# -------- Instancia global --------
_ui = None
_root = None

def iniciar_ui():
    global _ui, _root
    _root = tk.Tk()
    _ui = StarkIndustriesUI(_root)
    _root.mainloop()

def get_ui():
    return _ui