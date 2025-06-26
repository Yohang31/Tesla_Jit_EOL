import tkinter as tk
from Diseño_Tesla import LoginFrame, MenuFrame

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Detección de Rollos")
        self.root.geometry("600x500")
        self.root.configure(bg="black")

        self.frames = {}
        for F in (LoginFrame, MenuFrame):
            frame = F(self.root, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.mostrar_frame(LoginFrame)

    def mostrar_frame(self, contenedor):
        frame = self.frames[contenedor]
        frame.tkraise()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
