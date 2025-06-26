from tkinter import messagebox
from datetime import datetime
import os

USUARIOS_PATH = "usuarios.txt"
LOG_PATH = "log_accesos.txt"

def verificar(usuario, contrasena):
    if not os.path.exists(USUARIOS_PATH):
        messagebox.showerror("Error", "El archivo de usuarios no existe.")
        return False

    with open(USUARIOS_PATH, "r") as f:
        for linea in f:
            datos = linea.strip().split(",")
            if len(datos) == 2:
                user, pwd = datos
                if usuario == user and contrasena == pwd:
                    guardar_log(usuario)
                    return True
    return False

def guardar_usuario(nuevo_usuario, nueva_contrasena):
    if not nuevo_usuario or not nueva_contrasena:
        messagebox.showwarning("Campos vacíos", "Usuario o contraseña vacíos.")
        return

    # Esto verifica si existe el QR
    if verificar(nuevo_usuario, nueva_contrasena):
        messagebox.showinfo("Info", "El usuario ya existe.")
        return

    with open(USUARIOS_PATH, "a") as f:
        f.write(f"{nuevo_usuario},{nueva_contrasena}\n")

def guardar_log(usuario):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"[{fecha}] Acceso exitoso de usuario: {usuario}\n")
