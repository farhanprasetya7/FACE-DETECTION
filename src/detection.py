"""
detection.py
--------------
Logika inti deteksi: menjalankan forward pass CNN dan menyaring
hasil berdasarkan ambang batas kepercayaan.
"""

import numpy as np

from src import config
from src.preprocessing import frame_to_blob, get_frame_dimensions


def run_detection(net, frame, confidence_threshold=None):
    """
    Menjalankan deteksi wajah pada satu frame menggunakan model yang sudah dimuat.

    Args:
        net (cv2.dnn_Net): model yang sudah dimuat lewat model_loader
        frame (np.ndarray): gambar input (BGR)
        confidence_threshold (float, optional): ambang batas kepercayaan (0-1)

    Returns:
        list[dict]: daftar wajah terdeteksi, tiap item berisi
                    'box' (x1, y1, x2, y2) dan 'confidence'
    """
    confidence_threshold = confidence_threshold or config.DEFAULT_CONFIDENCE_THRESHOLD
    h, w = get_frame_dimensions(frame)

    # Preprocessing gambar menjadi blob
    blob = frame_to_blob(frame)

    # Forward pass melalui jaringan CNN
    net.setInput(blob)
    raw_detections = net.forward()

    return _filter_detections(raw_detections, w, h, confidence_threshold)


def _filter_detections(raw_detections, frame_width, frame_height, confidence_threshold):
    """
    Menyaring output mentah model: buang deteksi dengan confidence rendah,
    lalu skalakan koordinat kotak ke ukuran gambar asli.
    """
    results = []

    for i in range(raw_detections.shape[2]):
        confidence = raw_detections[0, 0, i, 2]

        if confidence <= confidence_threshold:
            continue

        box = raw_detections[0, 0, i, 3:7] * np.array(
            [frame_width, frame_height, frame_width, frame_height]
        )
        (x1, y1, x2, y2) = box.astype("int")

        # Jaga koordinat tetap dalam batas gambar
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(frame_width - 1, x2), min(frame_height - 1, y2)

        results.append({
            "box": (int(x1), int(y1), int(x2), int(y2)),
            "confidence": float(confidence),
        })

    return results
