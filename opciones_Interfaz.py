import tkinter as tk
from tkinter import Toplevel
from Aplicacion_Descarga_Videos import Aplicacion_Descarga_Videos
from AplicacionDescargas import AplicacionDescargas

# Funciones para abrir ventanas independientes
def ventana_descargar_video():
    ventana_video = Toplevel(root)
    ventana_video.title("Descargar Videos")
    ventana_video.geometry("600x400")

    app_video = Aplicacion_Descarga_Videos(ventana_video)
    app_video.pack(fill="both", expand=True)

def ventana_descargar_audio():
    ventana_audio = Toplevel(root)
    ventana_audio.title("Descargar Música o audios")
    ventana_audio.geometry("600x400")

    app_audio = AplicacionDescargas(ventana_audio)
    app_audio.pack(fill="both", expand=True)

# Ventana principal
root = tk.Tk()
root.title("Descargador de Videos Y Musica")
root.geometry("300x200")

# Etiqueta principal
tk.Label(root, text="Seleccione una opción", font=("Arial", 16)).pack(pady=20)

# Botones para las opciones
tk.Button(root, text="Descargar Videos", command=ventana_descargar_video, width=20, height=2).pack(pady=10)
tk.Button(root, text="Descargar Música", command=ventana_descargar_audio, width=20, height=2).pack(pady=10)

# Ejecutar aplicación
root.mainloop()
