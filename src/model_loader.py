"""
model_loader.py
-----------------
Bertanggung jawab hanya untuk memuat model deep learning ke OpenCV DNN engine.
Dipisah agar jika suatu saat ingin ganti backend (mis. ONNX, TensorFlow, PyTorch),
cukup ubah file ini saja.
"""

import os
import cv2

from src import config


def load_face_detection_model(prototxt_path=None, weights_path=None):
    """
    Memuat model Caffe (SSD ResNet-10) ke dalam OpenCV DNN.

    Args:
        prototxt_path (str, optional): path ke file arsitektur (.prototxt)
        weights_path (str, optional): path ke file bobot (.caffemodel)

    Returns:
        cv2.dnn_Net: objek network yang siap dipakai untuk inferensi
    """
    prototxt_path = prototxt_path or config.PROTOTXT_PATH
    weights_path = weights_path or config.WEIGHTS_PATH

    if not os.path.exists(prototxt_path) or not os.path.exists(weights_path):
        raise FileNotFoundError(
            "File model tidak ditemukan. Jalankan 'python download_model.py' terlebih dahulu.\n"
            f"  - Dicari di: {prototxt_path}\n"
            f"  - Dicari di: {weights_path}"
        )

    net = cv2.dnn.readNetFromCaffe(prototxt_path, weights_path)
    return net
