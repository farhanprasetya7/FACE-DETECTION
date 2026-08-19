"""
detector.py
------------
Kelas FaceDetector adalah "pintu masuk" utama sistem — menggabungkan
model_loader, detection, dan visualization menjadi satu antarmuka
yang sederhana dipakai (dipanggil dari detect_image.py / detect_webcam.py).

File ini sengaja dibuat ringkas. Jika ingin mengubah:
- cara model dimuat        -> edit src/model_loader.py
- cara gambar diproses      -> edit src/preprocessing.py
- logika deteksi/threshold  -> edit src/detection.py
- tampilan kotak/label       -> edit src/visualization.py
- pengaturan umum (path, warna, dll) -> edit src/config.py
"""

from src import config
from src.model_loader import load_face_detection_model
from src.detection import run_detection
from src.visualization import draw_detections


class FaceDetector:
    def __init__(self, prototxt_path=None, model_path=None, confidence_threshold=None):
        """
        Args:
            prototxt_path (str, optional): path ke file arsitektur model
            model_path (str, optional): path ke file bobot model
            confidence_threshold (float, optional): ambang batas kepercayaan (0-1)
        """
        self.confidence_threshold = confidence_threshold or config.DEFAULT_CONFIDENCE_THRESHOLD
        self.net = load_face_detection_model(prototxt_path, model_path)

    def detect(self, frame):
        """Mendeteksi wajah pada satu frame. Lihat src/detection.py untuk detail."""
        return run_detection(self.net, frame, self.confidence_threshold)

    def draw_detections(self, frame, detections):
        """Menggambar hasil deteksi. Lihat src/visualization.py untuk detail."""
        return draw_detections(frame, detections)
