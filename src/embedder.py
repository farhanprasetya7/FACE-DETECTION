"""
embedder.py
-------------
Modul inti DEEP LEARNING untuk face recognition.

Menggunakan model CNN pretrained (OpenFace nn4.small2.v1) yang mengubah
gambar wajah menjadi vektor numerik berdimensi 128 (disebut "embedding"
atau "face signature"). Arsitekturnya terinspirasi dari GoogLeNet/Inception,
dilatih dengan triplet loss -- pendekatan yang sama dipakai oleh FaceNet.

Sifat penting embedding ini: dua wajah dari ORANG YANG SAMA akan
menghasilkan vektor yang jaraknya (Euclidean distance) dekat, sedangkan
wajah dari orang BERBEDA akan menghasilkan vektor yang jaraknya jauh.
Inilah yang membedakannya dari metode klasik (LBPH/Eigenface): di sini
representasi wajah dipelajari sendiri oleh neural network dari jutaan
data wajah, bukan dihitung dengan rumus statistik tetap.
"""

import os
import cv2
import numpy as np

from src import config


class FaceEmbedder:
    def __init__(self, model_path=None):
        self.model_path = model_path or config.EMBEDDING_MODEL_PATH

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                "Model embedding tidak ditemukan. Jalankan 'python download_model.py' "
                f"terlebih dahulu.\n  - Dicari di: {self.model_path}"
            )

        # Memuat CNN pretrained (format Torch) ke OpenCV DNN engine
        self.net = cv2.dnn.readNetFromTorch(self.model_path)

    def get_embedding(self, face_image):
        """
        Menjalankan forward pass CNN untuk mengubah gambar wajah menjadi
        vektor embedding 128 dimensi.

        Args:
            face_image (np.ndarray): gambar wajah hasil crop (BGR, ukuran bebas)

        Returns:
            np.ndarray: vektor embedding berbentuk (128,)
        """
        # Preprocessing: resize ke 96x96, normalisasi ke rentang [0,1],
        # dan konversi BGR->RGB sesuai spesifikasi input model
        blob = cv2.dnn.blobFromImage(
            face_image,
            scalefactor=1.0 / 255,
            size=config.EMBEDDING_INPUT_SIZE,
            mean=(0, 0, 0),
            swapRB=True,
            crop=False,
        )

        self.net.setInput(blob)
        embedding = self.net.forward()

        return embedding.flatten()
