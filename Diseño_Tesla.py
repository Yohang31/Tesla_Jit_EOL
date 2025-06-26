import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import Login_Tesla
import os
from Camara_prueba_Tesla import CamaraIntegrada  

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        self.controller = controller

        # Logo
        try:
             ruta_logo = os.path.join(os.path.dirname(__file__), "logo.png")
             logo_img = Image.open(ruta_logo)
             logo_img = logo_img.resize((250, 150), Image.Resampling.LANCZOS)
             self.logo = ImageTk.PhotoImage(logo_img)
             tk.Label(self, image=self.logo, bg="black").pack(pady=10)
        except Exception as e:
            print("No se pudo cargar el logo:", e)

        tk.Label(self, text="Login", font=("Arial", 20), fg="white", bg="black").pack(pady=10)

        form_frame = tk.Frame(self, bg="black")
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Usuario:", font=("Arial", 12), fg="white", bg="black").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.usuario_entry = tk.Entry(form_frame, fg="white", bg="#000000", insertbackground="white")
        self.usuario_entry.grid(row=0, column=1, pady=5)

        tk.Label(form_frame, text="Clave:", font=("Arial", 12), fg="white", bg="black").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.contra_entry = tk.Entry(form_frame, show="*", fg="white", bg="#222222", insertbackground="white")
        self.contra_entry.grid(row=1, column=1, pady=5)

        # Botones verticales al lado izquierdo
        buttons_frame = tk.Frame(self, bg="black")
        buttons_frame.pack(side="left", fill="y", padx=30, pady=20)

        btn_login = tk.Button(buttons_frame, text="Ingresar", command=self.login,
                              bg="#03ed07", fg="black", activebackground="#0036f9", width=15)
        btn_login.pack(pady=5)

        btn_registrar = tk.Button(buttons_frame, text="Registrar", command=self.registrar,
                                  bg="#2ecc71", fg="black", activebackground="#27ae60", width=15)
        btn_registrar.pack(pady=5)

        btn_salir = tk.Button(buttons_frame, text="Salir", command=self.salir,
                              bg="#e74c3c", fg="white", activebackground="#c0392b", width=15)
        btn_salir.pack(pady=5)

    def login(self):
        usuario = self.usuario_entry.get()
        contrasena = self.contra_entry.get()

        if Login_Tesla.verificar(usuario, contrasena):
            self.controller.mostrar_frame(MenuFrame)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    def registrar(self):
        usuario = self.usuario_entry.get()
        contrasena = self.contra_entry.get()
        if usuario and contrasena:
            Login_Tesla.guardar_usuario(usuario, contrasena)
            messagebox.showinfo("Registro", f"Usuario '{usuario}' registrado.")
        else:
            messagebox.showwarning("Advertencia", "Debe llenar ambos campos.")

    def salir(self):
        self.controller.root.quit()

class MenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        self.controller = controller

        tk.Label(self, text="Menú Principal", font=("Arial", 20), fg="white", bg="black").pack(pady=10)

        self.camara = CamaraIntegrada(self)

        # Botones verticales a la izquierda
        botones_frame = tk.Frame(self, bg="black")
        botones_frame.pack(side="left", fill="y", padx=20, pady=20)

        tk.Button(botones_frame, text="Activar Cámara", command=self.camara.iniciar,
                  bg="#2ecc71", fg="black", activebackground="#27ae60", width=15).pack(pady=5)

        tk.Button(botones_frame, text="Detener Cámara", command=self.camara.detener,
                  bg="#2ecc71", fg="black", activebackground="#27ae60", width=15).pack(pady=5)
        tk.Button(botones_frame, text="Cerrar Sesión", command=self.cerrar_sesion,
                  bg="#2ecc71", fg="black", activebackground="#27ae60", width=15).pack(pady=5)

        tk.Button(botones_frame, text="Salir", command=self.salir,
                  bg="#e74c3c", fg="white", activebackground="#c0392b", width=15).pack(pady=5)

    def cerrar_sesion(self):
        self.camara.detener()
        self.controller.mostrar_frame(LoginFrame)

    def salir(self):
        self.camara.detener()
        self.controller.root.quit()
