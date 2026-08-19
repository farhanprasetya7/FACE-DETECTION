# logic_registrasi.py
import cv2
import os
import json
from src.dataset_loader import build_embeddings_dataset
from src.recognizer import FaceRecognizer

STATUS_FILE = "users_data.json"

class RegistrasiBackend:
    def __init__(self):
        self.cap = None
        self.step = 0
        self.capture_count = 0
        self.person_dir = ""
        self.saved_count = 0
        self.folder_name = ""
        
        # Daftar instruksi gaya Face Unlock
        self.instructions = [
            "Hadap depan dan tahan",
            "Menoleh perlahan ke kiri",
            "Menoleh perlahan ke kanan",
            "Senyum sedikit",
            "Selesai! Memproses data..."
        ]

    def mulai_kamera(self, tag_nomor, nama_depan, nama_belakang, biodata_tambahan=None):
        # Bikin nama folder gabungan Tag dan Nama
        self.folder_name = f"{tag_nomor}_{nama_depan}{nama_belakang}"
        self.person_dir = os.path.join("dataset", self.folder_name)
        os.makedirs(self.person_dir, exist_ok=True)

        # Simpan biodata mahasiswa ke users_data.json
        self.simpan_biodata(nama_depan, nama_belakang, tag_nomor, biodata_tambahan or {})

        self.cap = cv2.VideoCapture(0)
        self.step = 0
        self.capture_count = 0
        self.saved_count = 0
        
        return self.instructions[self.step]

    def simpan_biodata(self, nama_depan, nama_belakang, nim, biodata_tambahan):
        # Baca data lama biar gak ketimpa
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, "r") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError):
                data = {}
        else:
            data = {}

        # Pertahankan status lama kalau user ini udah pernah ada (misal registrasi ulang)
        status_lama = data.get(self.folder_name, {}).get("status", "Aktif")
        sampai_lama = data.get(self.folder_name, {}).get("sampai", "")

        biodata = {"nama_depan": nama_depan, "nama_belakang": nama_belakang, "nim": nim}
        biodata.update(biodata_tambahan)  # Field dinamis dari Setting nempel di sini

        data[self.folder_name] = {
            "status": status_lama,
            "sampai": sampai_lama,
            "biodata": biodata
        }

        with open(STATUS_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def proses_frame(self):
        if self.cap is None:
            return False, None, "", False

        ret, frame = self.cap.read()
        if not ret:
            return False, None, "", False

        frame = cv2.flip(frame, 1)
        
        # Cek apakah sudah di instruksi terakhir
        is_done = (self.step == len(self.instructions) - 1)
        if is_done:
            return True, frame, self.instructions[self.step], True

        # Jepret dan simpan foto tiap 5 frame (realtime ke dataset)
        self.capture_count += 1
        if self.capture_count % 5 == 0:
            filename = f"{self.saved_count:03d}.jpg"
            filepath = os.path.join(self.person_dir, filename)
            cv2.imwrite(filepath, frame)
            self.saved_count += 1

        # Pindah instruksi tiap 30 frame
        if self.capture_count > 30:
            self.step += 1
            self.capture_count = 0

        return True, frame, self.instructions[self.step], False

    def matikan_kamera(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    # --- FUNGSI AUTO-TRAINING BARU ---
    def latih_model_otomatis(self):
        try:
            embeddings, names = build_embeddings_dataset()
            if len(embeddings) == 0:
                return False, "Dataset masih kosong euy!"
            
            recognizer = FaceRecognizer()
            recognizer.train(embeddings, names)
            recognizer.save()
            return True, "Sistem berhasil mempelajari wajah baru!"
        except Exception as e:
            return False, str(e)