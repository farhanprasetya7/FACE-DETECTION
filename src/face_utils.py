"""
face_utils.py
---------------
Fungsi bantu untuk memotong (crop) area wajah dari frame sebelum
dimasukkan ke model embedding CNN.
"""


def crop_face(frame, box):
    """
    Memotong area wajah dari frame berdasarkan bounding box hasil deteksi.

    Args:
        frame (np.ndarray): gambar asli (BGR)
        box (tuple): (x1, y1, x2, y2)

    Returns:
        np.ndarray: gambar wajah hasil crop (BGR)
    """
    x1, y1, x2, y2 = box
    return frame[y1:y2, x1:x2]


def is_valid_face(face_image, min_size=20):
    """Cek apakah hasil crop wajah cukup valid untuk diproses (tidak kosong/terlalu kecil)."""
    if face_image is None or face_image.size == 0:
        return False
    h, w = face_image.shape[:2]
    return h >= min_size and w >= min_size
