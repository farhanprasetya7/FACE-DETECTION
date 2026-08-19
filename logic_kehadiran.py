# logic_kehadiran.py
import csv
import os
from datetime import datetime
from logic_jadwal import JadwalBackend

class KehadiranBackend:
    def __init__(self):
        self.jadwal_backend = JadwalBackend()

    def load_absen_hari_ini(self):
        """Balikin list of dict: nama, jam, status_teks, status_warna, telat (bool)"""
        hasil = []
        if not os.path.exists("attendance.csv"):
            return hasil

        hari_ini_date = datetime.now().strftime("%Y-%m-%d")

        with open("attendance.csv", mode="r") as f:
            reader = csv.reader(f)
            next(reader, None)  # Lewatin header

            for row in reader:
                if len(row) >= 2:
                    nama = row[0]
                    waktu_full = row[1]

                    if waktu_full.startswith(hari_ini_date):
                        jam_absen = waktu_full.split(" ")[1][:5]
                        status_teks, telat = self.jadwal_backend.cek_status_waktu(jam_absen)
                        status_warna = "#FF4C4C" if telat else "#4F75FF"

                        hasil.append({
                            "nama": nama,
                            "jam": jam_absen,
                            "status_teks": status_teks,
                            "status_warna": status_warna,
                            "telat": telat
                        })
        return hasil

    def load_semua_absen(self):
        """Balikin semua data absen (bukan cuma hari ini), dengan status per baris"""
        hasil = []
        if not os.path.exists("attendance.csv"):
            return hasil

        with open("attendance.csv", mode="r") as f:
            reader = csv.reader(f)
            next(reader, None)

            for row in reader:
                if len(row) >= 2:
                    nama = row[0]
                    waktu_full = row[1]
                    tanggal = waktu_full.split(" ")[0]
                    jam_absen = waktu_full.split(" ")[1][:5]
                    status_teks, telat = self.jadwal_backend.cek_status_waktu(jam_absen)

                    hasil.append({
                        "nama": nama,
                        "tanggal": tanggal,
                        "jam": jam_absen,
                        "status": "TERLAMBAT" if telat else "Tepat Waktu"
                    })
        return hasil

    def export_laporan(self, filepath, mode="semua"):
        """mode: 'hari_ini' atau 'semua'. Simpan laporan ke filepath (CSV)"""
        try:
            data = self.load_absen_hari_ini() if mode == "hari_ini" else self.load_semua_absen()

            if not data:
                return False, "Gak ada data absen buat di-export euy!"

            with open(filepath, mode="w", newline="") as f:
                writer = csv.writer(f)
                if mode == "hari_ini":
                    writer.writerow(["Nama", "Jam Absen", "Status"])
                    for d in data:
                        writer.writerow([d["nama"], d["jam"], d["status_teks"]])
                else:
                    writer.writerow(["Nama", "Tanggal", "Jam Absen", "Status"])
                    for d in data:
                        writer.writerow([d["nama"], d["tanggal"], d["jam"], d["status"]])

            return True, f"Laporan berhasil disimpan ke {filepath}"
        except Exception as e:
            return False, str(e)
