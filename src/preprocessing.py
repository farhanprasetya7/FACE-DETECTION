"""
preprocessing.py
------------------
Berisi fungsi-fungsi untuk mengolah gambar mentah menjadi format
yang siap "dimakan" oleh jaringan CNN (blob).
"""

import cv2

from src import config


def frame_to_blob(frame, input_size=None, mean=None):
    """
    Mengubah frame/gambar mentah (BGR, ukuran bebas) menjadi blob
    yang siap dimasukkan ke model DNN.

    Args:
        frame (np.ndarray): gambar input (hasil cv2.imread / VideoCapture)
        input_size (tuple, optional): ukuran resize, default dari config
        mean (tuple, optional): nilai mean subtraction, default dari config

    Returns:
        np.ndarray: blob 4D siap dipakai net.setInput()
    """
    input_size = input_size or config.INPUT_SIZE
    mean = mean or config.MEAN_SUBTRACTION

    resized = cv2.resize(frame, input_size)
    blob = cv2.dnn.blobFromImage(
        resized,
        scalefactor=1.0,
        size=input_size,
        mean=mean,
    )
    return blob


def get_frame_dimensions(frame):
    """Mengembalikan (height, width) dari sebuah frame."""
    (h, w) = frame.shape[:2]
    return h, w
