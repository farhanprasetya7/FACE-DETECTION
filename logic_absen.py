# logic_absen.py
import cv2
import os
import csv
from datetime import datetime

# Import otak AI
from src.detector import FaceDetector
from src.embedder import FaceEmbedder
from src.recognizer import FaceRecognizer
from src.face_utils import crop_face, is_valid_face
from src.visualization import draw_recognitions

class AbsenBackend:
    def __init__(self):
        self.cap = None
        print("[INFO] Memuat model pengenalan wajah...")
        self.detector = FaceDetector(confidence_threshold=0.6)
        self.embedder = FaceEmbedder()
        self.recognizer = FaceRecognizer()
        self.recognizer.load()

        self.target_sebelumnya = None
        self.counter_stabil = 0
        self.sudah_proses = False

    def mulai_kamera(self):
        self.cap = cv2.VideoCapture(0)
        self.sudah_proses = False
        self.counter_stabil = 0
        self.target_sebelumnya = None

    def cek_sudah_absen_hari_ini(self, nama):
        if not os.path.exists("attendance.csv"):
            return False
        
        hari_ini = datetime.now().strftime("%Y-%m-%d")
        with open("attendance.csv", mode="r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    if row[0].lower() == nama.lower() and row[1].startswith(hari_ini):
                        return True
        return False

    def simpan_data_absen(self, nama):
        waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_ada = os.path.exists("attendance.csv")
        
        with open("attendance.csv", mode="a", newline="") as f:
            writer = csv.writer(f)
            if not file_ada:
                writer.writerow(["Nama", "Waktu"])
            writer.writerow([nama, waktu_sekarang])

    def proses_frame(self):
        if self.cap is None or self.sudah_proses:
            return False, None, "STOP", None, 0

        ret, frame = self.cap.read()
        if not ret:
            return False, None, "ERROR", None, 0

        frame = cv2.flip(frame, 1)
        
        detections = self.detector.detect(frame)
        recognitions = []
        nama_terdeteksi = None
        
        for det in detections:
            cropped = crop_face(frame, det["box"])
            if not is_valid_face(cropped):
                recognitions.append({"name": "?", "probability": 0.0, "recognized": False})
                continue

            embedding = self.embedder.get_embedding(cropped)
            pred = self.recognizer.predict(embedding)
            recognitions.append(pred)
            
            if pred["recognized"] and pred["probability"] > 0.7:
                nama_terdeteksi = pred["name"]

        output_frame = draw_recognitions(frame, detections, recognitions)

        # Logika Penentuan Status buat dikirim ke UI
        status = "SCANNING"
        
        if nama_terdeteksi:
            if nama_terdeteksi == self.target_sebelumnya:
                self.counter_stabil += 1
            else:
                self.target_sebelumnya = nama_terdeteksi
                self.counter_stabil = 1

            if self.counter_stabil >= 20:
                self.sudah_proses = True
                self.matikan_kamera()
                
                # Cek status user dari JSON dulu
                status_user = "Aktif"
                if os.path.exists("users_data.json"):
                    import json
                    with open("users_data.json", "r") as f:
                        data_status = json.load(f)
                        if nama_terdeteksi in data_status:
                            status_user = data_status[nama_terdeteksi]["status"]

                if status_user == "BAN":
                    status = "BANNED" # Bikin UI absen nampilin warna merah "Sedang di skor"
                elif status_user == "CUTI":
                    status = "ON_LEAVE" # Bikin UI absen nampilin warna orange "Sedang cuti"
                elif self.cek_sudah_absen_hari_ini(nama_terdeteksi):
                    status = "ALREADY_ABSEN"
                else:
                    self.simpan_data_absen(nama_terdeteksi)
                    status = "SUCCESS"
        else:
            self.counter_stabil = 0
            self.target_sebelumnya = None
            if len(detections) > 0:
                status = "UNKNOWN" # Ada wajah tapi ga kenal
            else:
                status = "NO_FACE" # Kosong ga ada orang

        return True, output_frame, status, self.target_sebelumnya, self.counter_stabil

    def matikan_kamera(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None