# kehadiran.py
import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog
from datetime import datetime
import theme
from logic_kehadiran import KehadiranBackend

class DatasetWindow(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Daftar Kehadiran")
        self.geometry("900x700")
        self.transient(master)
        self.configure(fg_color=theme.APP_BG)

        self.backend = KehadiranBackend()

        ctk.CTkLabel(self, text="Daftar Kehadiran", font=theme.font_title(30),
                     text_color=theme.TEXT_PRIMARY).pack(pady=(30, 16))

        # --- HEADER HARI DAN STATUS ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=50, pady=(6, 6))

        hari_dict = {
            "Monday": "SENIN", "Tuesday": "SELASA", "Wednesday": "RABU",
            "Thursday": "KAMIS", "Friday": "JUMAT", "Saturday": "SABTU", "Sunday": "MINGGU"
        }
        hari_ini = hari_dict.get(datetime.now().strftime("%A"), "HARI INI")

        ctk.CTkLabel(header_frame, text=hari_ini, font=theme.font_body(13, bold=True),
                     text_color=theme.ACCENT).pack(side="left")
        ctk.CTkLabel(header_frame, text="Status", font=theme.font_body(13, bold=True),
                     text_color=theme.ACCENT).pack(side="right")

        # --- TEMPAT LIST NAMA (Bisa di-scroll) ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=50, pady=10)

        # --- TOMBOL DOWNLOAD LAPORAN ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(5, 20))

        ctk.CTkButton(
            btn_frame, text="Download Laporan Hari Ini", corner_radius=10,
            fg_color=theme.ACCENT, text_color=theme.ACCENT_TEXT, hover_color=theme.ACCENT_HOVER,
            font=theme.font_body(12, bold=True), command=self.download_hari_ini,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="Download Laporan Semua", corner_radius=10,
            fg_color=theme.SIDEBAR_BG, text_color=theme.TEXT_ON_SIDEBAR, hover_color=theme.BUTTON_MUTED,
            font=theme.font_body(12, bold=True), command=self.download_semua,
        ).pack(side="left", padx=10)

        self.load_data()

    def load_data(self):
        data = self.backend.load_absen_hari_ini()

        if not data:
            ctk.CTkLabel(self.scroll_frame, text="Belum ada yang absen euy hari ini.",
                         font=theme.font_body(13), text_color=theme.TEXT_SECONDARY).pack(pady=20)
            return

        for d in data:
            status_lengkap = f"Sudah Absen\n{d['jam']}\n{d['status_teks']}"
            warna = theme.DANGER if d.get("telat") else theme.SUCCESS
            self.buat_kartu_absen(d["nama"], status_lengkap, warna)

    def buat_kartu_absen(self, nama, status_teks, warna):
        card = ctk.CTkFrame(self.scroll_frame, fg_color=theme.CARD_BG, border_width=1,
                            border_color=theme.BORDER, corner_radius=10)
        card.pack(fill="x", pady=5)

        ctk.CTkLabel(card, text=nama, font=theme.font_body(17, bold=True),
                     text_color=theme.TEXT_PRIMARY).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(card, text=status_teks, font=theme.font_body(11, bold=True),
                     text_color=warna, justify="right").pack(side="right", padx=20, pady=10)

    def download_hari_ini(self):
        self._download(mode="hari_ini", nama_default="laporan_kehadiran_hari_ini.csv")

    def download_semua(self):
        self._download(mode="semua", nama_default="laporan_kehadiran_semua.csv")

    def _download(self, mode, nama_default):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")],
            initialfile=nama_default,
            title="Simpan Laporan Kehadiran"
        )
        if not filepath:
            return

        sukses, pesan = self.backend.export_laporan(filepath, mode=mode)
        if sukses:
            messagebox.showinfo("Berhasil", pesan)
        else:
            messagebox.showerror("Gagal", pesan)
