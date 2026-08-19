# logic_dataset.py
import os
import shutil
import json
from src.dataset_loader import build_embeddings_dataset
from src.recognizer import FaceRecognizer

class DatasetBackend:
    def __init__(self):
        self.dataset_dir = "dataset"
        self.status_file = "users_data.json"
        self.pastikan_file_status_ada()

    def pastikan_file_status_ada(self):
        if not os.path.exists(self.status_file):
            with open(self.status_file, "w") as f:
                json.dump({}, f)

    def get_all_users(self):
        if not os.path.exists(self.dataset_dir):
            return []
        return [d for d in os.listdir(self.dataset_dir) if os.path.isdir(os.path.join(self.dataset_dir, d))]

    def load_statuses(self):
        with open(self.status_file, "r") as f:
            return json.load(f)

    def save_statuses(self, data):
        with open(self.status_file, "w") as f:
            json.dump(data, f, indent=4)

    def set_status(self, user_folder, status, batas_waktu=""):
        data = self.load_statuses()
        # Pertahankan biodata yang udah ada, cuma ganti status-nya
        biodata_lama = data.get(user_folder, {}).get("biodata", {})
        data[user_folder] = {"status": status, "sampai": batas_waktu, "biodata": biodata_lama}
        self.save_statuses(data)

    def get_biodata(self, user_folder):
        data = self.load_statuses()
        return data.get(user_folder, {}).get("biodata", {
            "nama_depan": "", "nama_belakang": "", "nim": ""
        })

    def update_biodata(self, user_folder, biodata_baru):
        data = self.load_statuses()
        if user_folder not in data:
            data[user_folder] = {"status": "Aktif", "sampai": ""}
        data[user_folder]["biodata"] = biodata_baru
        self.save_statuses(data)

    def hapus_user(self, user_folder):
        # 1. Hapus folder fisik secara permanen
        path = os.path.join(self.dataset_dir, user_folder)
        if os.path.exists(path):
            shutil.rmtree(path)

        # 2. Hapus dari catatan status
        data = self.load_statuses()
        if user_folder in data:
            del data[user_folder]
            self.save_statuses(data)

        # 3. Latih Ulang AI biar lupa ingatan
        try:
            embeddings, names = build_embeddings_dataset()
            if len(embeddings) > 0:
                recognizer = FaceRecognizer()
                recognizer.train(embeddings, names)
                recognizer.save()
            else:
                # Kalau semua user habis dihapus, reset modelnya
                if os.path.exists("trained_model/recognizer.pkl"):
                    os.remove("trained_model/recognizer.pkl")
            return True, "User berhasil dihapus dan AI sudah di-update!"
        except Exception as e:
            return False, f"Gagal update AI euy: {str(e)}"