# absen.py
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox
import theme

# Panggil backend logika absen
from logic_absen import AbsenBackend

class AbsenWindow(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Absen")
        self.geometry("800x720")
        self.transient(master)
        self.configure(fg_color=theme.APP_BG)

        ctk.CTkLabel(self, text="Absen", font=theme.font_title(34),
                     text_color=theme.TEXT_PRIMARY).pack(pady=(24, 4))
        ctk.CTkLabel(self, text="Paskan posisi wajah anda dalam bingkai", font=theme.font_body(13),
                     text_color=theme.TEXT_SECONDARY).pack(pady=(0, 20))

        self.video_label = ctk.CTkLabel(self, text="", fg_color=theme.CARD_BG, corner_radius=12)
        self.video_label.pack(pady=10)

        self.btn_validasi = ctk.CTkButton(
            self, text="Klik Disini Untuk Validasi", width=260, height=42, corner_radius=21,
            fg_color=theme.ACCENT, text_color=theme.ACCENT_TEXT, hover_color=theme.ACCENT_HOVER,
            font=theme.font_body(13, bold=True), command=self.tombol_mulai_kamera,
        )
        self.btn_validasi.pack(pady=10)

        status_frame = ctk.CTkFrame(self, corner_radius=16, fg_color=theme.CARD_BG,
                                     border_width=1, border_color=theme.BORDER)
        status_frame.pack(fill="x", padx=100, pady=20)

        ctk.CTkLabel(status_frame, text="Status :", font=theme.font_body(15, bold=True),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 0))
        ctk.CTkLabel(status_frame, text="Wajah terdeteksi :", font=theme.font_body(12),
                     text_color=theme.TEXT_SECONDARY).pack(anchor="w", padx=20, pady=(5, 0))

        self.lbl_hasil_nama = ctk.CTkLabel(status_frame, text="-", font=theme.font_body(15, bold=True),
                                            text_color=theme.ACCENT)
        self.lbl_hasil_nama.pack(anchor="w", padx=20, pady=(10, 2))

        self.lbl_hasil_divisi = ctk.CTkLabel(status_frame, text="-", font=theme.font_body(12),
                                              text_color=theme.TEXT_SECONDARY)
        self.lbl_hasil_divisi.pack(anchor="w", padx=20, pady=(0, 16))

        # Inisialisasi Backend
        self.backend = AbsenBackend()

    def tombol_mulai_kamera(self):
        if self.backend.cap is None:
            self.backend.mulai_kamera()
            self.btn_validasi.configure(text="Sedang Memindai...", state="disabled")
            self.update_frame_ui()

    def update_frame_ui(self):
        ret, frame, status, nama, counter = self.backend.proses_frame()

        if ret:
            if status == "SCANNING" and nama:
                self.lbl_hasil_nama.configure(text=f"Mendeteksi: {nama} ({counter}/20)", text_color=theme.WARNING)
                self.lbl_hasil_divisi.configure(text="Tahan posisi...", text_color=theme.WARNING)
            elif status == "UNKNOWN":
                self.lbl_hasil_nama.configure(text="Wajah Tidak Dikenal", text_color=theme.DANGER)
                self.lbl_hasil_divisi.configure(text="-", text_color=theme.DANGER)
            elif status == "NO_FACE":
                self.lbl_hasil_nama.configure(text="-", text_color=theme.ACCENT)
                self.lbl_hasil_divisi.configure(text="-", text_color=theme.TEXT_SECONDARY)

            if frame is not None:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ctk.CTkImage(light_image=img, size=(400, 300))
                self.video_label.configure(image=imgtk)
                self.video_label.image = imgtk

            if status == "ALREADY_ABSEN":
                self.video_label.configure(image="")
                self.btn_validasi.configure(text="Klik Disini Untuk Validasi", state="normal")
                self.lbl_hasil_nama.configure(text=f"{nama} - Sudah Absen", text_color=theme.DANGER)
                self.lbl_hasil_divisi.configure(text="Ditolak", text_color=theme.DANGER)
                messagebox.showwarning("Peringatan", "ANDA SUDAH ABSEN SEBELUMNYA")
                return
            elif status == "SUCCESS":
                self.video_label.configure(image="")
                self.btn_validasi.configure(text="Klik Disini Untuk Validasi", state="normal")
                self.lbl_hasil_nama.configure(text=f"{nama} - Berhasil!", text_color=theme.SUCCESS)
                self.lbl_hasil_divisi.configure(text="Tercatat di Sistem", text_color=theme.SUCCESS)
                messagebox.showinfo("Sukses", "BERHASIL ABSEN")
                return

            self.after(10, self.update_frame_ui)

    def destroy(self):
        self.backend.matikan_kamera()
        super().destroy()
