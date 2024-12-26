import re
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import yt_dlp
import os
import threading
import requests
from io import BytesIO


class Aplicacion_Descarga_Videos(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.url_var = tk.StringVar()
        self.carpeta_var = tk.StringVar()
        self.video_titulo = tk.StringVar(value="Título del video")
        self.calidad_var = tk.StringVar()
        self.progreso_var = tk.DoubleVar()
        self.estado_descarga = tk.StringVar(value="Esperando...")
        self.calidad_opciones = {}
        self.nombre_archivo = tk.StringVar(value="nombre_del_video")  # Variable para el nombre del archivo
        self.crear_widgets()

    def crear_widgets(self):
        tk.Label(self, text="URL del video:").pack(pady=5)
        tk.Entry(self, textvariable=self.url_var, width=50).pack(pady=5)
        tk.Button(self, text="Obtener información", command=self.obtener_informacion_video).pack(pady=5)

        self.miniatura_label = tk.Label(self)
        self.miniatura_label.pack(pady=5)

        tk.Label(self, textvariable=self.video_titulo, wraplength=400, justify="center").pack(pady=5)

        tk.Label(self, text="Seleccione la calidad:").pack(pady=5)
        self.calidad_menu = ttk.OptionMenu(self, self.calidad_var, None)
        self.calidad_menu.pack(pady=5)

        tk.Label(self, text="Carpeta de descarga:").pack(pady=5)
        tk.Entry(self, textvariable=self.carpeta_var, width=50).pack(pady=5)
        tk.Button(self, text="Seleccionar carpeta", command=self.seleccionar_carpeta).pack(pady=5)

        tk.Label(self, text="Nombre del archivo:").pack(pady=5)
        tk.Entry(self, textvariable=self.nombre_archivo, width=50).pack(pady=5)  # Campo para el nombre del archivo

        tk.Button(self, text="Descargar Video", command=self.descargar_video).pack(pady=10)

        self.barra_progreso = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate", variable=self.progreso_var)
        self.barra_progreso.pack(pady=10)

        tk.Label(self, textvariable=self.estado_descarga).pack(pady=5)

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.carpeta_var.set(carpeta)

    def obtener_informacion_video(self):
        url = self.url_var.get()
        if not url:
            self.estado_descarga.set("Por favor, ingrese una URL.")
            return

        self.estado_descarga.set("Obteniendo información del video...")

        def proceso_obtener_info():
            try:
                with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    self.video_titulo.set(info.get("title", "Desconocido"))

                    miniatura_url = info.get("thumbnail")
                    if miniatura_url:
                        try:
                            response = requests.get(miniatura_url, timeout=5)
                            img_data = BytesIO(response.content)
                            img = Image.open(img_data).resize((200, 150))
                            miniatura_img = ImageTk.PhotoImage(img)
                            self.miniatura_label.configure(image=miniatura_img)
                            self.miniatura_label.image = miniatura_img
                        except requests.exceptions.RequestException:
                            self.estado_descarga.set("No se pudo cargar la imagen por problemas de red.")
                    else:
                        self.estado_descarga.set("No se encontró miniatura.")

                    formatos = info.get("formats", [])
                    self.calidad_menu['menu'].delete(0, 'end')
                    for f in formatos:
                        if f.get("vcodec") != "none":  # Solo formatos con video
                            self.calidad_menu['menu'].add_command(label=f"{f['format']} ({f['ext']})",
                                                                   command=tk._setit(self.calidad_var, f['format_id']))
                            self.calidad_opciones[f['format_id']] = f

                    if not self.calidad_opciones:
                        self.estado_descarga.set("No hay formatos disponibles para este video.")
                    else:
                        self.calidad_var.set(next(iter(self.calidad_opciones)))  # Seleccionar automáticamente una calidad disponible
                        self.estado_descarga.set("Información obtenida. Seleccione la calidad y carpeta.")
            except yt_dlp.utils.DownloadError:
                self.estado_descarga.set("El video no existe o no está disponible.")
            except Exception as e:
                self.estado_descarga.set(f"Error al obtener información: {e}")

        threading.Thread(target=proceso_obtener_info, daemon=True).start()

    def progreso_callback(self, d):
        if d['status'] == 'downloading':
            porcentaje = re.sub(r'\x1b\[[0-9;]*m', '', d.get('_percent_str', '0%')).strip('%')
            try:
                self.progreso_var.set(float(porcentaje))
            except ValueError:
                pass
            self.estado_descarga.set(f"Descargando: {porcentaje}%")
        elif d['status'] == 'finished':
            self.estado_descarga.set("Descarga completada.")
            self.progreso_var.set(100)

    def descargar_video(self):
        url = self.url_var.get()
        carpeta = self.carpeta_var.get()
        calidad = self.calidad_var.get()
        nombre_archivo = self.nombre_archivo.get()

        if not url or not carpeta or not calidad or not nombre_archivo:
            self.estado_descarga.set("Por favor, complete todos los campos.")
            return

        self.estado_descarga.set("Iniciando descarga...")
        self.progreso_var.set(0)

        def proceso_descarga():
            try:
                seleccion = self.calidad_opciones.get(calidad)
                if not seleccion:
                    self.estado_descarga.set("La calidad seleccionada no está disponible.")
                    return

                # Usamos el nombre proporcionado por el usuario para el archivo
                ydl_opts = {
                    'format': seleccion['format_id'],
                    'outtmpl': os.path.join(carpeta, f"{nombre_archivo}.%(ext)s"),  # Usamos el nombre dado por el usuario
                    'progress_hooks': [self.progreso_callback],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except yt_dlp.utils.DownloadError:
                self.estado_descarga.set("Error en la red: No se pudo descargar el video.")
            except Exception as e:
                self.estado_descarga.set(f"Error: {e}")

        threading.Thread(target=proceso_descarga, daemon=True).start()

