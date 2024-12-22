import tkinter as tk
from tkinter import ttk, filedialog
import yt_dlp
import os
import re
import threading

def seleccionar_carpeta():
    carpeta = filedialog.askdirectory()
    if carpeta:
        carpeta_var.set(carpeta)

def progreso_callback(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes', 0) / (1024 * 1024)  # Total en MB
        descargado = d.get('downloaded_bytes', 0) / (1024 * 1024)  # Descargado en MB
        porcentaje = d.get('_percent_str', '0%').strip()
        
        # Limpiar cualquier código de color ANSI de la cadena del porcentaje
        porcentaje = re.sub(r'\x1b\[[0-9;]*m', '', porcentaje).strip()

        try:
            # Actualizar barra de progreso
            progreso_var.set(float(porcentaje.strip('%')))
        except ValueError:
            # Si no se puede convertir el porcentaje, no hacer nada
            pass
        
        # Actualizar etiquetas
        estado_descarga.set(f"Descargando: {descargado:.2f} MB de {total:.2f} MB ({porcentaje})")
    
    elif d['status'] == 'finished':
        estado_descarga.set("Descarga completada.")
        progreso_var.set(100)

def descargar_audio():
    url = url_var.get()
    carpeta = carpeta_var.get()

    if not url or not carpeta:
        estado_descarga.set("Por favor, ingrese una URL y seleccione una carpeta.")
        return
    
    estado_descarga.set("Iniciando descarga...")
    progreso_var.set(0)

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
        'cookiefile': 'cookies.txt',  # Archivo de cookies
        'socket_timeout': 60,        # Tiempo de espera ampliado
        'retries': 5,                # Más intentos antes de fallar
        'nocheckcertificate': True,  # Desactivar verificación de certificados SSL
        'progress_hooks': [progreso_callback],
    }

    # Crear un hilo para la descarga
    def proceso_descarga():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            estado_descarga.set(f"Error: {e}")
    
    # Iniciar la descarga en un hilo separado
    threading.Thread(target=proceso_descarga, daemon=True).start()

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Descargador de Audio de YouTube")
ventana.geometry("500x300")

# Variables
url_var = tk.StringVar()
carpeta_var = tk.StringVar()
progreso_var = tk.DoubleVar()
estado_descarga = tk.StringVar(value="Esperando...")

# Widgets
tk.Label(ventana, text="URL del video:").pack(pady=5)
tk.Entry(ventana, textvariable=url_var, width=50).pack()

tk.Label(ventana, text="Carpeta de descarga:").pack(pady=5)
tk.Entry(ventana, textvariable=carpeta_var, width=50).pack()
tk.Button(ventana, text="Seleccionar carpeta", command=seleccionar_carpeta).pack(pady=5)

tk.Button(ventana, text="Descargar Audio", command=descargar_audio).pack(pady=10)

barra_progreso = ttk.Progressbar(ventana, orient="horizontal", length=400, mode="determinate", variable=progreso_var)
barra_progreso.pack(pady=10)

tk.Label(ventana, textvariable=estado_descarga).pack(pady=5)

# Iniciar aplicación
ventana.mainloop()
