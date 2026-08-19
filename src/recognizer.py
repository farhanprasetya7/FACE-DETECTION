"""
recognizer.py
---------------
Lapisan KLASIFIKASI di atas embedding CNN (lihat src/embedder.py).

Alur:
1. embedder.py (CNN deep learning) mengubah wajah -> vektor 128 dimensi
2. recognizer.py (SVM) mempelajari batas antar-kelas dari vektor-vektor
   tersebut, lalu dipakai untuk mengklasifikasikan wajah baru

Kenapa masih perlu SVM di atas CNN? Karena embedding CNN sifatnya
generik (bisa merepresentasikan wajah SIAPAPUN, bukan cuma yang ada di
dataset kita). SVM-lah yang mempelajari secara spesifik "vektor seperti
apa yang termasuk si A, dan seperti apa yang termasuk si B" berdasarkan
dataset yang kita siapkan. Pendekatan CNN-embedding + SVM classifier ini
adalah pipeline standar pada banyak riset face recognition modern
(FaceNet, OpenFace, dsb).
"""

import os
import pickle
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder

from src import config


class FaceRecognizer:
    def __init__(self):
        self.classifier = None
        self.label_encoder = None

    def train(self, embeddings, names):
        """
        Melatih SVM classifier dari daftar embedding wajah dan nama pemiliknya.

        Args:
            embeddings (list[np.ndarray]): daftar vektor embedding 128-d
            names (list[str]): nama/identitas untuk tiap embedding
        """
        self.label_encoder = LabelEncoder()
        encoded_labels = self.label_encoder.fit_transform(names)

        # SVM dengan kernel linear -- pilihan umum untuk klasifikasi
        # embedding wajah karena ruang embeddingnya sudah cukup terpisah
        # secara linear hasil pembelajaran CNN sebelumnya.
        self.classifier = SVC(C=1.0, kernel="linear", probability=True)
        self.classifier.fit(np.array(embeddings), encoded_labels)

    def save(self):
        """Menyimpan classifier + label encoder hasil training ke disk."""
        os.makedirs(config.TRAINED_MODEL_DIR, exist_ok=True)

        with open(config.CLASSIFIER_PATH, "wb") as f:
            pickle.dump(self.classifier, f)

        with open(config.LABEL_ENCODER_PATH, "wb") as f:
            pickle.dump(self.label_encoder, f)

    def load(self):
        """Memuat classifier yang sudah dilatih sebelumnya dari disk."""
        if not os.path.exists(config.CLASSIFIER_PATH) or not os.path.exists(config.LABEL_ENCODER_PATH):
            raise FileNotFoundError(
                "Model recognizer belum ditemukan. Jalankan 'python train_recognizer.py' "
                "terlebih dahulu setelah menyiapkan folder dataset/."
            )

        with open(config.CLASSIFIER_PATH, "rb") as f:
            self.classifier = pickle.load(f)

        with open(config.LABEL_ENCODER_PATH, "rb") as f:
            self.label_encoder = pickle.load(f)

    def predict(self, embedding, probability_threshold=None):
        """
        Mengklasifikasikan satu vektor embedding wajah menjadi identitas.

        Args:
            embedding (np.ndarray): vektor embedding 128-d dari FaceEmbedder
            probability_threshold (float, optional): ambang batas probabilitas

        Returns:
            dict: {'name': str, 'probability': float, 'recognized': bool}
        """
        probability_threshold = probability_threshold or config.RECOGNITION_PROBABILITY_THRESHOLD

        probabilities = self.classifier.predict_proba([embedding])[0]
        best_index = np.argmax(probabilities)
        best_probability = probabilities[best_index]

        recognized = best_probability >= probability_threshold
        name = self.label_encoder.classes_[best_index] if recognized else config.UNKNOWN_LABEL

        return {
            "name": name,
            "probability": float(best_probability),
            "recognized": bool(recognized),
        }
