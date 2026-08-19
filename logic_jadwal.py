# logic_jadwal.py
import json
import os

JADWAL_FILE = "jadwal.json"

class JadwalBackend:
    def __init__(self):
        self.pastikan_file_ada()

    def pastikan_file_ada(self):
        if not os.path.exists(JADWAL_FILE):
            default = {"jam_masuk": "08:00", "toleransi_menit": 0}
            self.simpan_jadwal(default["jam_masuk"], default["toleransi_menit"])

    def get_jadwal(self):
        try:
            with open(JADWAL_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"jam_masuk": "08:00", "toleransi_menit": 0}

    def simpan_jadwal(self, jam_masuk, toleransi_menit):
        data = {"jam_masuk": jam_masuk, "toleransi_menit": int(toleransi_menit)}
        with open(JADWAL_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def cek_status_waktu(self, jam_absen_str):
        """Terima 'HH:MM' dari absen, balikin (status_teks, is_telat)"""
        jadwal = self.get_jadwal()
        jam_batas, menit_batas = map(int, jadwal["jam_masuk"].split(":"))
        toleransi = jadwal.get("toleransi_menit", 0)

        # Hitung total menit batas + toleransi
        total_menit_batas = (jam_batas * 60) + menit_batas + toleransi

        jam_absen, menit_absen = map(int, jam_absen_str.split(":"))
        total_menit_absen = (jam_absen * 60) + menit_absen

        if total_menit_absen <= total_menit_batas:
            return "Tepat Waktu !", False
        else:
            return "TERLAMBAT", True
