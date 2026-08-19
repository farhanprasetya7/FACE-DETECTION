# jadwal.py
import customtkinter as ctk
import tkinter.messagebox as messagebox
import theme
from logic_jadwal import JadwalBackend

class JadwalWindow(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Time / Jadwal")
        self.geometry("480x420")
        self.transient(master)
        self.configure(fg_color=theme.APP_BG)

        self.backend = JadwalBackend()

        ctk.CTkLabel(self, text="Time / Jadwal", font=theme.font_title(24),
                     text_color=theme.TEXT_PRIMARY).pack(pady=(30, 4))
        ctk.CTkLabel(self, text="Atur jam masuk buat penentuan status kehadiran",
                     font=theme.font_body(12), text_color=theme.TEXT_SECONDARY).pack(pady=(0, 20))

        card = ctk.CTkFrame(self, corner_radius=14, fg_color=theme.CARD_BG,
                             border_width=1, border_color=theme.BORDER)
        card.pack(padx=40, pady=10, fill="x")

        ctk.CTkLabel(card, text="Jam Masuk (format HH:MM)", font=theme.font_body(12, bold=True),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(20, 5))
        self.entry_jam = ctk.CTkEntry(card, width=150, placeholder_text="08:00",
                                       fg_color=theme.ENTRY_BG, border_color=theme.ENTRY_BORDER,
                                       text_color=theme.TEXT_PRIMARY, corner_radius=8)
        self.entry_jam.pack(anchor="w", padx=20)

        ctk.CTkLabel(card, text="Toleransi Keterlambatan (menit)", font=theme.font_body(12, bold=True),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(20, 5))
        self.entry_toleransi = ctk.CTkEntry(card, width=150, placeholder_text="0",
                                             fg_color=theme.ENTRY_BG, border_color=theme.ENTRY_BORDER,
                                             text_color=theme.TEXT_PRIMARY, corner_radius=8)
        self.entry_toleransi.pack(anchor="w", padx=20, pady=(0, 20))

        jadwal_sekarang = self.backend.get_jadwal()
        self.entry_jam.insert(0, jadwal_sekarang["jam_masuk"])
        self.entry_toleransi.insert(0, str(jadwal_sekarang.get("toleransi_menit", 0)))

        ctk.CTkButton(
            self, text="Simpan Jadwal", corner_radius=10, height=38,
            fg_color=theme.ACCENT, text_color=theme.ACCENT_TEXT, hover_color=theme.ACCENT_HOVER,
            font=theme.font_body(13, bold=True), command=self.simpan,
        ).pack(pady=25)

        self.lbl_info = ctk.CTkLabel(self, text="", font=theme.font_body(11), text_color=theme.TEXT_SECONDARY)
        self.lbl_info.pack()

    def simpan(self):
        jam = self.entry_jam.get().strip()
        toleransi = self.entry_toleransi.get().strip()

        try:
            parts = jam.split(":")
            if len(parts) != 2:
                raise ValueError
            jam_int, menit_int = int(parts[0]), int(parts[1])
            if not (0 <= jam_int <= 23 and 0 <= menit_int <= 59):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Format Salah", "Jam masuk harus format HH:MM, contoh: 08:00")
            return

        if not toleransi.isdigit():
            messagebox.showwarning("Format Salah", "Toleransi harus berupa angka (menit)")
            return

        self.backend.simpan_jadwal(jam, toleransi)
        messagebox.showinfo("Tersimpan", f"Jadwal berhasil disimpan!\nJam masuk: {jam} (toleransi {toleransi} menit)")
        self.lbl_info.configure(text=f"Aktif: masuk sebelum {jam} + toleransi {toleransi} menit = Tepat Waktu")
