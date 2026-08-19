import calendar
import json
import os
from datetime import datetime

import customtkinter as ctk
import tkinter.messagebox as messagebox

import theme
from absen import AbsenWindow
from registrasi import RegistrasiWindow
from setting import SettingWindow
from logic_setting import SettingBackend
from jadwal import JadwalWindow
from logic_jadwal import JadwalBackend
from logic_kehadiran import KehadiranBackend
from logic_dataset import DatasetBackend

# Akalin nama class yang bentrok pake alias (as) euy
from kehadiran import DatasetWindow as KehadiranWindow
from dataset import DatasetWindow as ManajemenUserWindow

# Terapkan tema tersimpan (light/dark) SEBELUM window dibuat
SettingBackend.terapkan_saat_startup()
ctk.set_default_color_theme("blue")


NAV_ITEMS = [
    ("Dashboard", None),        # halaman aktif, gak buka window baru
    ("Absen", "buka_absen"),
    ("Regist", "buka_regist"),
    ("Dataset", "buka_dataset"),
    ("Kehadiran", "buka_kehadiran"),
    ("Time", "buka_time"),
    ("Setting", "buka_setting"),
]

BULAN_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
            "Agustus", "September", "Oktober", "November", "Desember"]


class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Dashboard Absensi")
        self.geometry("1100x700")
        self.minsize(980, 640)
        self.configure(fg_color=theme.APP_BG)

        self.settings_backend = SettingBackend()
        self.jadwal_backend = JadwalBackend()
        self.kehadiran_backend = KehadiranBackend()
        self.dataset_backend = DatasetBackend()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()

    # ---------------------------------------------------------------
    # SIDEBAR
    # ---------------------------------------------------------------
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=190, corner_radius=0, fg_color=theme.SIDEBAR_BG)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        brand = ctk.CTkLabel(
            sidebar, text="FaceAbsen",
            font=theme.font_title(18), text_color=theme.TEXT_ON_SIDEBAR,
        )
        brand.pack(anchor="w", padx=20, pady=(22, 24))

        for label, handler_name in NAV_ITEMS:
            is_dashboard = handler_name is None
            btn = ctk.CTkButton(
                sidebar, text=label, anchor="w",
                font=theme.font_body(13, bold=is_dashboard),
                fg_color=theme.ACCENT if is_dashboard else "transparent",
                text_color=theme.ACCENT_TEXT if is_dashboard else theme.TEXT_ON_SIDEBAR_MUTED,
                hover_color=theme.ACCENT_HOVER if is_dashboard else ("#3A4D43", "#22322A"),
                corner_radius=8, height=36,
                command=(getattr(self, handler_name) if handler_name else None),
            )
            btn.pack(fill="x", padx=12, pady=2)

        promo = ctk.CTkFrame(sidebar, corner_radius=12, fg_color=("#25342D", "#20302A"))
        promo.pack(fill="x", padx=12, side="bottom", pady=18)

        mode_aktif = self.settings_backend.get_appearance_mode()
        self.lbl_promo = ctk.CTkLabel(
            promo,
            text=f"Mode aktif: {mode_aktif.capitalize()}",
            font=theme.font_body(11), text_color=theme.TEXT_ON_SIDEBAR,
            justify="left",
        )
        self.lbl_promo.pack(anchor="w", padx=14, pady=(14, 6))

        ctk.CTkButton(
            promo, text="Ganti tema", font=theme.font_body(11), height=28,
            fg_color=theme.ACCENT, text_color=theme.ACCENT_TEXT,
            hover_color=theme.ACCENT_HOVER, corner_radius=8,
            command=self.toggle_tema,
        ).pack(padx=14, pady=(0, 14), fill="x")

    def toggle_tema(self):
        mode_baru = self.settings_backend.toggle_appearance_mode()
        self.lbl_promo.configure(text=f"Mode aktif: {mode_baru.capitalize()}")

    # ---------------------------------------------------------------
    # MAIN AREA
    # ---------------------------------------------------------------
    def _build_main_area(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=0, column=1, sticky="nsew", padx=24, pady=22)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=0)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content, text="Dashboard", font=theme.font_title(22), text_color=theme.TEXT_PRIMARY,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        left = ctk.CTkFrame(content, fg_color="transparent")
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 16))
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        self._build_banner(left)
        self._build_table(left)

        right = ctk.CTkFrame(content, fg_color="transparent", width=240)
        right.grid(row=1, column=1, sticky="ns")

        self._build_calendar_card(right)
        self._build_profile_card(right)
        self._build_jadwal_card(right)

    def _build_banner(self, parent):
        stats = self._compute_stats()
        banner = ctk.CTkFrame(parent, corner_radius=16, fg_color=theme.SIDEBAR_BG)
        banner.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        ctk.CTkLabel(
            banner, text="Halo, Admin!", font=theme.font_title(19), text_color=theme.TEXT_ON_SIDEBAR,
        ).pack(anchor="w", padx=24, pady=(18, 4))
        ctk.CTkLabel(
            banner,
            text=f"Hari ini ada {stats['hadir']} orang sudah absen, "
                 f"{stats['terlambat']} terlambat, dan {stats['belum']} belum hadir.",
            font=theme.font_body(13), text_color=theme.TEXT_ON_SIDEBAR_MUTED,
            wraplength=460, justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 18))

    def _build_table(self, parent):
        card = ctk.CTkFrame(parent, fg_color=theme.CARD_BG, corner_radius=14,
                             border_width=1, border_color=theme.BORDER)
        card.grid(row=1, column=0, sticky="nsew")

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 8))
        ctk.CTkLabel(header, text="Riwayat kehadiran", font=theme.font_body(15, bold=True),
                     text_color=theme.TEXT_PRIMARY).pack(side="left")
        ctk.CTkButton(
            header, text="Lihat semua", font=theme.font_body(11), height=26, width=100,
            corner_radius=14, fg_color=theme.ACCENT, text_color=theme.ACCENT_TEXT,
            hover_color=theme.ACCENT_HOVER, command=self.buka_kehadiran,
        ).pack(side="right")

        col_head = ctk.CTkFrame(card, fg_color="transparent")
        col_head.pack(fill="x", padx=20)
        for text, expand in (("Nama", True), ("NIM/ID", False), ("Status", False)):
            ctk.CTkLabel(col_head, text=text, font=theme.font_body(10),
                         text_color=theme.TEXT_SECONDARY, anchor="w", width=90 if not expand else 0
                         ).pack(side="left", fill="x", expand=expand, padx=(0, 6))

        rows_frame = ctk.CTkScrollableFrame(card, fg_color="transparent")
        rows_frame.pack(fill="both", expand=True, padx=14, pady=(6, 16))

        data = self._ambil_riwayat_terbaru()
        if not data:
            ctk.CTkLabel(rows_frame, text="Belum ada data kehadiran.", font=theme.font_body(12),
                         text_color=theme.TEXT_SECONDARY).pack(pady=20)
            return

        for item in data:
            row = ctk.CTkFrame(rows_frame, fg_color="transparent")
            row.pack(fill="x", pady=6, padx=6)

            ctk.CTkLabel(
                row, text=item["inisial"], width=28, height=28, corner_radius=14,
                fg_color=theme.AVATAR_BG, text_color=theme.AVATAR_TEXT, font=theme.font_body(11),
            ).pack(side="left")

            ctk.CTkLabel(row, text=item["nama"], font=theme.font_body(12),
                         text_color=theme.TEXT_PRIMARY).pack(side="left", padx=10)

            status_color = theme.DANGER if item["telat"] else theme.SUCCESS
            ctk.CTkLabel(row, text=item["status"], font=theme.font_body(11),
                         text_color=status_color, width=90).pack(side="right")
            ctk.CTkLabel(row, text=item["id"], font=theme.font_body(11),
                         text_color=theme.TEXT_SECONDARY, width=90).pack(side="right")

    def _build_calendar_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=theme.CARD_BG, corner_radius=14, width=240,
                             border_width=1, border_color=theme.BORDER)
        card.pack(fill="x", pady=(0, 14))

        today = datetime.now()
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(header, text="Kalender", font=theme.font_body(13, bold=True),
                     text_color=theme.TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(header, text=f"{BULAN_ID[today.month - 1]} {today.year}", font=theme.font_body(10),
                     text_color=theme.TEXT_SECONDARY).pack(side="right")

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(padx=14, pady=(0, 16))

        for i, d in enumerate(["Sn", "Sl", "Rb", "Km", "Jm", "Sb", "Mg"]):
            ctk.CTkLabel(grid, text=d, font=theme.font_body(10), width=26,
                         text_color=theme.TEXT_SECONDARY).grid(row=0, column=i, pady=(0, 4))

        cal = calendar.Calendar(firstweekday=0)
        row_idx = 1
        for week in cal.monthdayscalendar(today.year, today.month):
            for col_idx, day in enumerate(week):
                if day == 0:
                    continue
                is_today = day == today.day
                ctk.CTkLabel(
                    grid, text=str(day), width=26, height=26, corner_radius=8,
                    fg_color=theme.ACCENT if is_today else "transparent",
                    text_color=theme.ACCENT_TEXT if is_today else theme.TEXT_PRIMARY,
                    font=theme.font_body(10),
                ).grid(row=row_idx, column=col_idx, pady=1)
            row_idx += 1

    def _build_profile_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=theme.CARD_BG, corner_radius=14, width=240,
                             border_width=1, border_color=theme.BORDER)
        card.pack(fill="x", pady=(0, 14))

        stats = self._compute_stats()
        total_absensi = self._hitung_total_absensi()

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 10))
        ctk.CTkLabel(header, text="AD", width=40, height=40, corner_radius=20,
                     fg_color=theme.AVATAR_BG, text_color=theme.AVATAR_TEXT,
                     font=theme.font_body(13, bold=True)).pack(side="left")
        text_col = ctk.CTkFrame(header, fg_color="transparent")
        text_col.pack(side="left", padx=10)
        ctk.CTkLabel(text_col, text="Admin", font=theme.font_body(13, bold=True),
                     text_color=theme.TEXT_PRIMARY, anchor="w").pack(anchor="w")
        ctk.CTkLabel(text_col, text="Pengelola sistem", font=theme.font_body(10),
                     text_color=theme.TEXT_SECONDARY, anchor="w").pack(anchor="w")

        icons_row = ctk.CTkFrame(card, fg_color="transparent")
        icons_row.pack(anchor="w", padx=16, pady=(0, 12))
        for symbol in ("\u260E", "\u2709", "\u270E"):  # telepon, email, pesan
            ctk.CTkLabel(
                icons_row, text=symbol, width=32, height=32, corner_radius=16,
                fg_color=theme.CARD_BG_HOVER, text_color=theme.TEXT_PRIMARY, font=theme.font_body(13),
            ).pack(side="left", padx=(0, 8))

        divider = ctk.CTkFrame(card, height=1, fg_color=theme.BORDER)
        divider.pack(fill="x", padx=16, pady=(0, 10))

        stat_rows = ctk.CTkFrame(card, fg_color="transparent")
        stat_rows.pack(fill="x", padx=16, pady=(0, 16))
        for label, val in (
            ("Total hadir", f"{stats['hadir']} orang"),
            ("Bergabung sejak", "12/08/2026"),
            ("Total absensi", f"{total_absensi} kali"),
        ):
            r = ctk.CTkFrame(stat_rows, fg_color="transparent")
            r.pack(fill="x", pady=3)
            ctk.CTkLabel(r, text=label, font=theme.font_body(11, bold=True),
                         text_color=theme.TEXT_PRIMARY, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=val, font=theme.font_body(11),
                         text_color=theme.TEXT_SECONDARY, anchor="e").pack(side="right")

    def _build_jadwal_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=theme.CARD_BG, corner_radius=14, width=240,
                             border_width=1, border_color=theme.BORDER)
        card.pack(fill="x")

        jadwal = self.jadwal_backend.get_jadwal()

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 4))
        ctk.CTkLabel(header, text="Time / Jadwal", font=theme.font_body(13, bold=True),
                     text_color=theme.TEXT_PRIMARY).pack(side="left")
        # Titik hijau kecil menandakan jam berjalan realtime
        ctk.CTkLabel(header, text="\u25CF", font=theme.font_body(10),
                     text_color=theme.SUCCESS).pack(side="right")

        # Jam realtime, update tiap detik lewat self.after (bukan waktu statis)
        self.lbl_jam_realtime = ctk.CTkLabel(
            card, text="--:--:--", font=theme.font_title(26), text_color=theme.TEXT_PRIMARY,
        )
        self.lbl_jam_realtime.pack(anchor="w", padx=16, pady=(0, 2))

        self.lbl_tanggal_realtime = ctk.CTkLabel(
            card, text="", font=theme.font_body(10), text_color=theme.TEXT_SECONDARY,
        )
        self.lbl_tanggal_realtime.pack(anchor="w", padx=16, pady=(0, 10))

        divider = ctk.CTkFrame(card, height=1, fg_color=theme.BORDER)
        divider.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkLabel(card, text="Jam masuk terjadwal", font=theme.font_body(10),
                     text_color=theme.TEXT_SECONDARY).pack(anchor="w", padx=16)
        ctk.CTkLabel(card, text=jadwal.get("jam_masuk", "-"), font=theme.font_body(16, bold=True),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=16)
        toleransi = jadwal.get("toleransi_menit", 0)
        ctk.CTkLabel(card, text=f"Toleransi keterlambatan {toleransi} menit", font=theme.font_body(10),
                     text_color=theme.TEXT_SECONDARY).pack(anchor="w", padx=16, pady=(2, 16))

        # Mulai loop update jam realtime
        self._update_jam_realtime()

    def _update_jam_realtime(self):
        """Update label jam & tanggal tiap detik pakai waktu sistem asli (bukan cache),
        jadi selalu akurat / tepat waktu."""
        now = datetime.now()
        hari_id = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        try:
            self.lbl_jam_realtime.configure(text=now.strftime("%H:%M:%S"))
            self.lbl_tanggal_realtime.configure(
                text=f"{hari_id[now.weekday()]}, {now.day} {BULAN_ID[now.month - 1]} {now.year}"
            )
        except Exception:
            # Widget mungkin sudah dihancurkan (window ditutup) - hentikan loop
            return
        # Jadwalkan update berikutnya persis di pergantian detik biar gak "ngambang"
        ms_sampai_detik_berikutnya = 1000 - now.microsecond // 1000
        self.after(ms_sampai_detik_berikutnya, self._update_jam_realtime)

    # ---------------------------------------------------------------
    # DATA HELPERS
    # ---------------------------------------------------------------
    def _compute_stats(self):
        try:
            data_hari_ini = self.kehadiran_backend.load_absen_hari_ini()
        except Exception:
            data_hari_ini = []

        hadir = len(data_hari_ini)
        terlambat = sum(1 for d in data_hari_ini if d.get("telat"))

        try:
            total_user = len(self.dataset_backend.get_all_users())
        except Exception:
            total_user = 0

        belum = max(total_user - hadir, 0)
        return {"hadir": hadir, "terlambat": terlambat, "belum": belum, "aktif": total_user}

    def _hitung_total_absensi(self):
        try:
            return len(self.kehadiran_backend.load_semua_absen())
        except Exception:
            return 0

    def _ambil_riwayat_terbaru(self, limit=6):
        try:
            data = self.kehadiran_backend.load_semua_absen()
        except Exception:
            data = []

        data = list(reversed(data))[:limit]
        hasil = []
        for d in data:
            nama_asli = d["nama"]
            id_bagian, _, nama_bagian = nama_asli.partition("_")
            nama_tampil = nama_bagian if nama_bagian else nama_asli
            inisial = "".join([w[0] for w in nama_tampil.replace("_", " ").split()[:2]]).upper() or "?"
            hasil.append({
                "nama": nama_tampil,
                "id": id_bagian if nama_bagian else "-",
                "inisial": inisial,
                "status": d["status"],
                "telat": d["status"] == "TERLAMBAT",
            })
        return hasil

    # ---------------------------------------------------------------
    # NAVIGASI
    # ---------------------------------------------------------------
    def buka_absen(self):
        AbsenWindow(self)

    def buka_regist(self):
        dialog = ctk.CTkInputDialog(text="Masukkan Kata Sandi Admin:", title="Keamanan")
        password = dialog.get_input()

        if password == "admin123":
            RegistrasiWindow(self)
        elif password is not None:
            messagebox.showerror("Akses Ditolak", "Password salah euy! Coba lagi.")

    def buka_dataset(self):
        ManajemenUserWindow(self)

    def buka_kehadiran(self):
        KehadiranWindow(self)

    def buka_setting(self):
        SettingWindow(self)

    def buka_time(self):
        JadwalWindow(self)


if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()
