"""
dataset_loader.py
-------------------
Membaca struktur folder dataset dan mengubah tiap foto menjadi
embedding wajah (vektor 128-d) menggunakan model deep learning
(src/embedder.py), siap dipakai untuk melatih classifier (src/recognizer.py).

Struktur folder yang diharapkan:
    dataset/
    ├── budi/
    │   ├── foto1.jpg
    │   ├── foto2.jpg
    │   └── ...
    ├── siti/
    │   ├── foto1.jpg
    │   └── ...
    └── ...

Nama sub-folder = nama/identitas orang yang akan dikenali oleh sistem.
"""

import os
import cv2

from src import config
from src.detector import FaceDetector
from src.embedder import FaceEmbedder
from src.face_utils import crop_face, is_valid_face

VALID_EXTENSIONS = (".jpg", ".jpeg", ".png")


def list_people(dataset_dir=None):
    """Mengembalikan daftar nama orang (nama sub-folder) dalam dataset."""
    dataset_dir = dataset_dir or config.DATASET_DIR

    if not os.path.exists(dataset_dir):
        return []

    return sorted([
        name for name in os.listdir(dataset_dir)
        if os.path.isdir(os.path.join(dataset_dir, name))
    ])


def build_embeddings_dataset(dataset_dir=None, detector=None, embedder=None, verbose=True):
    """
    Membaca semua gambar dalam folder dataset, mendeteksi wajah pada tiap
    gambar (model deteksi SSD ResNet-10), lalu mengekstrak embedding-nya
    (model CNN OpenFace) untuk dipakai sebagai data training classifier.

    Args:
        dataset_dir (str, optional): path folder dataset
        detector (FaceDetector, optional): instance detektor wajah
        embedder (FaceEmbedder, optional): instance CNN embedding
        verbose (bool): tampilkan progres di terminal

    Returns:
        tuple: (embeddings, names)
            embeddings (list[np.ndarray]): daftar vektor embedding 128-d
            names (list[str]): nama pemilik tiap embedding
    """
    dataset_dir = dataset_dir or config.DATASET_DIR
    detector = detector or FaceDetector()
    embedder = embedder or FaceEmbedder()

    people = list_people(dataset_dir)
    if not people:
        raise ValueError(
            f"Dataset kosong atau tidak ditemukan di '{dataset_dir}'.\n"
            "Buat folder dataset/<nama_orang>/ berisi foto-foto wajah terlebih dahulu."
        )

    embeddings = []
    names = []

    for person_name in people:
        person_dir = os.path.join(dataset_dir, person_name)

        image_files = [
            f for f in os.listdir(person_dir)
            if f.lower().endswith(VALID_EXTENSIONS)
        ]

        if verbose:
            print(f"[INFO] Memproses '{person_name}' ({len(image_files)} foto)...")

        count_ok = 0
        for filename in image_files:
            image_path = os.path.join(person_dir, filename)
            frame = cv2.imread(image_path)

            if frame is None:
                if verbose:
                    print(f"  [WARNING] Gagal membaca: {filename}")
                continue

            detections = detector.detect(frame)
            if not detections:
                if verbose:
                    print(f"  [WARNING] Tidak ada wajah terdeteksi di: {filename}")
                continue

            # Ambil wajah dengan confidence tertinggi (asumsi 1 wajah utama per foto)
            best_detection = max(detections, key=lambda d: d["confidence"])
            cropped = crop_face(frame, best_detection["box"])

            if not is_valid_face(cropped):
                continue

            embedding = embedder.get_embedding(cropped)

            embeddings.append(embedding)
            names.append(person_name)
            count_ok += 1

        if verbose:
            print(f"  -> {count_ok}/{len(image_files)} foto berhasil diproses.")

    if not embeddings:
        raise ValueError(
            "Tidak ada wajah yang berhasil diekstrak dari dataset. "
            "Pastikan foto jelas dan wajah terlihat."
        )

    return embeddings, names
