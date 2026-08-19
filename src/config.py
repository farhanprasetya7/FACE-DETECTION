"""
config.py
----------
Semua pengaturan/konfigurasi sistem dikumpulkan di sini.
Kalau mau mengubah path model, ukuran input, atau nilai default,
cukup edit file ini — tidak perlu menyentuh kode logika di file lain.
"""

import os

# Direktori root proyek
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path file model deep learning
MODEL_DIR = os.path.join(BASE_DIR, "models")
PROTOTXT_PATH = os.path.join(MODEL_DIR, "deploy.prototxt")
WEIGHTS_PATH = os.path.join(MODEL_DIR, "res10_300x300_ssd_iter_140000.caffemodel")

# URL unduhan model (dipakai oleh download_model.py)
PROTOTXT_URL = (
    "https://raw.githubusercontent.com/opencv/opencv/master/"
    "samples/dnn/face_detector/deploy.prototxt"
)
WEIGHTS_URL = (
    "https://raw.githubusercontent.com/opencv/opencv_3rdparty/"
    "dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
)

# Ukuran input yang diharapkan model (lebar, tinggi) dalam piksel
INPUT_SIZE = (300, 300)

# Nilai mean subtraction untuk preprocessing (standar model SSD ResNet-10 ini)
MEAN_SUBTRACTION = (104.0, 177.0, 123.0)

# Ambang batas kepercayaan default (0-1). Semakin tinggi = semakin ketat.
DEFAULT_CONFIDENCE_THRESHOLD = 0.5

# Pengaturan tampilan bounding box hasil deteksi
BOX_COLOR = (0, 255, 0)       # Hijau (format BGR)
BOX_THICKNESS = 2
LABEL_COLOR = (0, 255, 0)
LABEL_FONT_SCALE = 0.5

# Pengaturan overlay FPS pada mode webcam
FPS_TEXT_COLOR = (0, 255, 255)  # Kuning

# ============================================================
# Konfigurasi FACE RECOGNITION (pengenalan identitas)
# Menggunakan model DEEP LEARNING (CNN) penghasil face embedding,
# BUKAN metode klasik seperti LBPH/Eigenface/Fisherface.
# ============================================================

# Folder dataset: dataset/<nama_orang>/foto1.jpg, foto2.jpg, ...
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

# Model CNN penghasil face embedding (OpenFace nn4.small2.v1, arsitektur
# terinspirasi Inception, dilatih dengan triplet loss -- pendekatan yang
# sama dengan FaceNet). Menghasilkan vektor 128 dimensi per wajah.
EMBEDDING_MODEL_PATH = os.path.join(MODEL_DIR, "openface_nn4.small2.v1.t7")
EMBEDDING_MODEL_URL = (
    "https://raw.githubusercontent.com/pyannote/pyannote-data/master/"
    "openface.nn4.small2.v1.t7"
)
EMBEDDING_INPUT_SIZE = (96, 96)   # ukuran input yang diharapkan model embedding
EMBEDDING_DIM = 128                # dimensi vektor embedding output

# Folder & file untuk menyimpan hasil training (embeddings + classifier)
TRAINED_MODEL_DIR = os.path.join(BASE_DIR, "trained_model")
EMBEDDINGS_PATH = os.path.join(TRAINED_MODEL_DIR, "embeddings.pickle")
CLASSIFIER_PATH = os.path.join(TRAINED_MODEL_DIR, "classifier.pickle")
LABEL_ENCODER_PATH = os.path.join(TRAINED_MODEL_DIR, "label_encoder.pickle")

# Ambang batas probabilitas classifier (0-1). Di bawah nilai ini,
# wajah dianggap "Tidak Dikenal" walau classifier tetap memberi tebakan.
RECOGNITION_PROBABILITY_THRESHOLD = 0.5

# Label untuk wajah yang tidak dikenali
UNKNOWN_LABEL = "Tidak Dikenal"
