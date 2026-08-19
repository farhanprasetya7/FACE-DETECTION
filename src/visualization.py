"""
visualization.py
------------------
Fungsi-fungsi untuk menggambar hasil deteksi ke atas gambar:
bounding box, label kepercayaan, dan overlay FPS (untuk mode webcam).
"""

import cv2

from src import config


def draw_detections(frame, detections):
    """
    Menggambar kotak pembatas + label persentase kepercayaan
    untuk setiap wajah yang terdeteksi.

    Args:
        frame (np.ndarray): gambar asli
        detections (list[dict]): hasil dari detection.run_detection()

    Returns:
        np.ndarray: salinan gambar dengan anotasi
    """
    output = frame.copy()

    for det in detections:
        (x1, y1, x2, y2) = det["box"]
        confidence = det["confidence"]

        cv2.rectangle(output, (x1, y1), (x2, y2), config.BOX_COLOR, config.BOX_THICKNESS)

        label = f"{confidence * 100:.1f}%"
        label_y = y1 - 10 if y1 - 10 > 10 else y1 + 20
        cv2.putText(
            output, label, (x1, label_y),
            cv2.FONT_HERSHEY_SIMPLEX, config.LABEL_FONT_SCALE, config.LABEL_COLOR, 2
        )

    return output


def draw_recognitions(frame, detections, recognitions):
    """
    Menggambar kotak pembatas + nama identitas (hasil face recognition)
    untuk setiap wajah yang terdeteksi.

    Args:
        frame (np.ndarray): gambar asli
        detections (list[dict]): hasil dari detection.run_detection()
        recognitions (list[dict]): hasil dari recognizer.predict(), urutan sejajar dengan detections

    Returns:
        np.ndarray: salinan gambar dengan anotasi nama
    """
    output = frame.copy()

    for det, rec in zip(detections, recognitions):
        (x1, y1, x2, y2) = det["box"]
        color = config.BOX_COLOR if rec["recognized"] else (0, 0, 255)  # merah jika tidak dikenal

        cv2.rectangle(output, (x1, y1), (x2, y2), color, config.BOX_THICKNESS)

        label = f"{rec['name']} ({rec['probability'] * 100:.0f}%)"
        label_y = y1 - 10 if y1 - 10 > 10 else y1 + 20
        cv2.putText(
            output, label, (x1, label_y),
            cv2.FONT_HERSHEY_SIMPLEX, config.LABEL_FONT_SCALE, color, 2
        )

    return output


def draw_fps_overlay(frame, fps, face_count):
    """
    Menambahkan teks info FPS dan jumlah wajah terdeteksi
    di pojok kiri atas frame (dipakai pada mode webcam).
    """
    text = f"FPS: {fps:.1f}  Wajah: {face_count}"
    cv2.putText(
        frame, text, (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, config.FPS_TEXT_COLOR, 2
    )
    return frame
