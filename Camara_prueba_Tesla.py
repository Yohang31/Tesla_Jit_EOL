import tkinter as tk
import tkinter.messagebox as messagebox
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO
import os
import sys
import datetime
import json
import time
import threading


class CamaraIntegrada:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.cap = None
        self.label_video = None
        self.running = False
        self.model = YOLO(self.resource_path("best.pt"))

        self.qr_leidos = set()
        self.ultimo_qr = None
        self.ultimo_tiempo_qr = 0
        self.tiempo_espera = 6
        self.lectura_activa = False

        self.tiempo_inactividad = 20
        self.ultimo_tiempo_activo = time.time()

        os.makedirs(self.resource_path("capturas"), exist_ok=True)
        os.makedirs(self.resource_path("logs"), exist_ok=True)
        os.makedirs(self.resource_path("informacion_de_capturas"), exist_ok=True)

        self.detector_qr = cv2.QRCodeDetector()

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.join(base_path, relative_path)

    def iniciar(self):
        for index in [0, 1]:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) #, cv2.CAP_DSHOW
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            time.sleep(1)

            if cap.isOpened():
                self.cap = cap
                print(f"Cámara abierta con índice {index}")
                break
        else:
            print("No se pudo abrir ninguna cámara.")
            return

        self.running = True
        self.ultimo_tiempo_activo = time.time()

        if self.label_video is None:
            self.label_video = tk.Label(self.parent, bg="black")
            self.label_video.pack(fill="both", expand=True, padx=10, pady=10)

        self.actualizar_frame()

    def actualizar_frame(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if ret:
            tiempo_actual = time.time()
            data, bbox, _ = self.detector_qr.detectAndDecode(frame)

            if data:
                if data != self.ultimo_qr:
                    self.ultimo_qr = data
                    self.ultimo_tiempo_qr = tiempo_actual
                    self.lectura_activa = True
                    self.ultimo_tiempo_activo = tiempo_actual
                elif self.lectura_activa:
                    cv2.putText(frame, "qr...", (5, 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            elif self.lectura_activa:
                cv2.putText(frame, "qr...", (5, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            if self.lectura_activa:
                if (tiempo_actual - self.ultimo_tiempo_qr) > self.tiempo_espera:
                    if self.ultimo_qr not in self.qr_leidos:
                        self.qr_leidos.add(self.ultimo_qr)
                        threading.Thread(
                            target=self.capturar_y_detectar,
                            args=(frame.copy(), self.ultimo_qr),
                            daemon=True
                        ).start()
                    else:
                        self.parent.after(0, lambda: self.mostrar_resultado(self.ultimo_qr, None, ya_existente=True))
                    self.lectura_activa = False

            results = self.model(frame, imgsz=640, conf=0.8)
            frame = results[0].plot()

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagen = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=imagen)
            self.label_video.imgtk = imgtk
            self.label_video.configure(image=imgtk)

        if (time.time() - self.ultimo_tiempo_activo) > self.tiempo_inactividad:
            print("Inactividad detectada. Suspendiendo cámara...")
            self.suspender_camara()
            return

        self.parent.after(30, self.actualizar_frame)

    def suspender_camara(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        self.running = False
        if self.label_video:
            self.label_video.configure(image="")
        print("Cámara inactiva.")

    def detener(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.label_video:
            self.label_video.configure(image="")
        print("cámara detenida")

    def reanudar_camara(self, event=None):
        if not self.running:
            print("Reactivando cámara por barra espaciadora...")
            self.iniciar()

    def capturar_y_detectar(self, frame=None, qr_data=None):
        if not self.running or self.cap is None:
            print("La cámara no está activa.")
            return

        if frame is None:
            ret, frame = self.cap.read()
            if not ret:
                print("No se pudo capturar la imagen.")
                return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_imagen = f"captura_{timestamp}.jpg"
        ruta_imagen_relativa = os.path.join("capturas", nombre_imagen)
        ruta_imagen_absoluta = self.resource_path(ruta_imagen_relativa)

        results = self.model(frame, imgsz=640, conf=0.75)
        frame_anotado = results[0].plot()
        cajas = results[0].boxes

        clases = results[0].names if hasattr(results[0], 'names') else self.model.names
        conteo = {}

        if cajas and len(cajas) > 0:
            for cls in results[0].boxes.cls:
                nombre_clase = clases[int(cls)]
                conteo[nombre_clase] = conteo.get(nombre_clase, 0) + 1

            num_belcros = conteo.get("Belcro", 0)
            num_listing = conteo.get("Listing", 0)
            
            estado = "OK" if (num_belcros == 3 and num_listing == 1) else "NO_OK"

            trazabilidad = {
                "fecha": timestamp,
                "qr": qr_data if qr_data else "sin QR",
                "imagen": ruta_imagen_relativa,
                "estado": estado,
                "conteo": conteo
            }
        else:
            trazabilidad = {
                "fecha": timestamp,
                "qr": qr_data if qr_data else "sin QR",
                "imagen": ruta_imagen_relativa,
                "estado": "NO_OK",
                "sin_informacion": True
            }

        nombre_json = f"trazabilidad_{timestamp}.json"
        ruta_json = self.resource_path(os.path.join("informacion_de_capturas", nombre_json))
        with open(ruta_json, "w") as f:
            json.dump(trazabilidad, f, indent=4)

        cv2.imwrite(ruta_imagen_absoluta, frame_anotado)

        self.parent.after(0, lambda: self.mostrar_resultado(qr_data, trazabilidad["estado"]))

        print(f"Imagen anotada guardada en {ruta_imagen_absoluta}")
        print(f"JSON guardado en {ruta_json}")

    def mostrar_resultado(self, qr_data, estado, ya_existente=False):
        if ya_existente:
            messagebox.showwarning("QR inválido", f"El QR '{qr_data}' ya fue leído.")
        else:
            messagebox.showinfo("QR leído", f"QR '{qr_data}' leído correctamente. Estado: {estado}")
