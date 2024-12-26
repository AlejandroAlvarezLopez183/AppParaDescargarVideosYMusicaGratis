import tkinter as tk
from tkinter import Toplevel, ttk, filedialog
import yt_dlp
import os
import re
import threading
from Aplicacion_Descarga_Videos import Aplicacion_Descarga_Videos

# Clase para descargar música de YouTube
class Aplicacion_Descargas(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.url_var = tk.StringVar()
        self.carpeta_var = tk.StringVar()
        self.progreso_var = tk.DoubleVar()
        self.estado_descarga = tk.StringVar(value="Esperando...")
        self.crear_widgets()

    def crear_widgets(self):
        tk.Label(self, text="URL del video:").pack(pady=5)
        tk.Entry(self, textvariable=self.url_var, width=50).pack()

        tk.Label(self, text="Carpeta de descarga:").pack(pady=5)
        tk.Entry(self, textvariable=self.carpeta_var, width=50).pack()
        tk.Button(self, text="Seleccionar carpeta", command=self.seleccionar_carpeta).pack(pady=5)

        tk.Button(self, text="Descargar Audio", command=self.descargar_audio).pack(pady=10)

        self.barra_progreso = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate",
                                              variable=self.progreso_var)
        self.barra_progreso.pack(pady=10)

        tk.Label(self, textvariable=self.estado_descarga).pack(pady=5)

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.carpeta_var.set(carpeta)

    def progreso_callback(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes', 0) / (1024 * 1024)  # Total en MB
            descargado = d.get('downloaded_bytes', 0) / (1024 * 1024)  # Descargado en MB
            porcentaje = d.get('_percent_str', '0%').strip()

            # Limpiar cualquier código de color ANSI de la cadena del porcentaje
            porcentaje = re.sub(r'\x1b\[[0-9;]*m', '', porcentaje).strip()

            try:
                # Actualizar barra de progreso
                self.progreso_var.set(float(porcentaje.strip('%')))
            except ValueError:
                # Si no se puede convertir el porcentaje, no hacer nada
                pass

            # Actualizar etiquetas
            self.estado_descarga.set(f"Descargando: {descargado:.2f} MB de {total:.2f} MB ({porcentaje})")

        elif d['status'] == 'finished':
            self.estado_descarga.set("Descarga completada.")
            self.progreso_var.set(100)

    def descargar_audio(self):
        url = self.url_var.get()
        carpeta = self.carpeta_var.get()

        if not url or not carpeta:
            self.estado_descarga.set("Por favor, ingrese una URL y seleccione una carpeta.")
            return

        self.estado_descarga.set("Iniciando descarga...")
        self.progreso_var.set(0)

        # Configuración de descarga
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(carpeta, '%(title)s.%(ext)s'),  # Ruta y nombre de archivo
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.5',
            },
            'progress_hooks': [self.progreso_callback],
        }

        # Crear un hilo para la descarga
        def proceso_descarga():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                self.estado_descarga.set(f"Error: {e}")

        # Iniciar la descarga en un hilo separado
        threading.Thread(target=proceso_descarga, daemon=True).start()


# Funciones para abrir ventanas independientes
def ventana_descargar_video():
    ventana_video = Toplevel(root)
    ventana_video.title("Descargar Videos")
    ventana_video.geometry("600x400")

    app_video = Aplicacion_Descarga_Videos(ventana_video)
    app_video.pack(fill="both", expand=True)


def ventana_descargar_audio():
    ventana_audio = Toplevel(root)
    ventana_audio.title("Descargar Música")
    ventana_audio.geometry("600x400")

    app_audio = Aplicacion_Descargas(ventana_audio)
    app_audio.pack(fill="both", expand=True)


# Ventana principal
root = tk.Tk()
root.title("Descargador de videos y musica")
root.geometry("300x200")

# Etiqueta principal
tk.Label(root, text="Seleccione una opción", font=("Arial", 16)).pack(pady=20)

# Botones para las opciones
tk.Button(root, text="Descargar Videos", command=ventana_descargar_video, width=20, height=2).pack(pady=10)
tk.Button(root, text="Descargar Música", command=ventana_descargar_audio, width=20, height=2).pack(pady=10)

# Ejecutar aplicación
root.mainloop()
