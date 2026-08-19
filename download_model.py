"""
download_model.py
-------------------
Mengunduh file model deep learning pretrained (SSD ResNet-10)
yang dibutuhkan oleh sistem deteksi wajah.

Semua path & URL diambil dari src/config.py — jika ingin ganti sumber model,
cukup edit di sana.

Jalankan sekali sebelum menggunakan detect_image.py / detect_webcam.py:
    python download_model.py
"""

import os
import urllib.request

from src import config

FILES = {
    config.PROTOTXT_PATH: config.PROTOTXT_URL,
    config.WEIGHTS_PATH: config.WEIGHTS_URL,
    config.EMBEDDING_MODEL_PATH: config.EMBEDDING_MODEL_URL,
}


def download():
    os.makedirs(config.MODEL_DIR, exist_ok=True)

    for dest_path, url in FILES.items():
        filename = os.path.basename(dest_path)

        if os.path.exists(dest_path):
            print(f"[SKIP] {filename} sudah ada.")
            continue

        print(f"[DOWNLOAD] Mengunduh {filename} ...")
        urllib.request.urlretrieve(url, dest_path)
        print(f"[OK] Tersimpan di {dest_path}")

    print("\nSemua file model siap digunakan.")


if __name__ == "__main__":
    download()
