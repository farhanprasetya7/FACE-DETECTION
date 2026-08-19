"""
train_recognizer.py
----------------------
Melatih sistem FACE RECOGNITION berbasis DEEP LEARNING menggunakan
foto-foto di dalam folder dataset/.

Alur:
1. Setiap foto dilewatkan model deteksi wajah CNN (SSD ResNet-10)
   untuk menemukan lokasi wajah.
2. Wajah yang ditemukan dilewatkan model embedding CNN (OpenFace)
   untuk diubah menjadi vektor 128 dimensi.
3. Seluruh vektor + label nama dipakai untuk melatih SVM classifier.

Jalankan setiap kali dataset berubah (nambah orang baru / nambah foto):
    python train_recognizer.py
"""

from src.dataset_loader import build_embeddings_dataset
from src.recognizer import FaceRecognizer


def main():
    print("[INFO] Membaca dataset dan mengekstrak embedding wajah (CNN)...")
    embeddings, names = build_embeddings_dataset()

    unique_names = sorted(set(names))
    print(f"\n[INFO] Total data wajah untuk training: {len(embeddings)}")
    print(f"[INFO] Daftar identitas: {unique_names}")

    print("\n[INFO] Melatih SVM classifier di atas embedding CNN...")
    recognizer = FaceRecognizer()
    recognizer.train(embeddings, names)
    recognizer.save()

    print("\n[SELESAI] Model tersimpan di folder trained_model/")
    print("Sistem siap dipakai untuk pengenalan wajah (recognize_image.py / recognize_webcam.py).")


if __name__ == "__main__":
    main()
