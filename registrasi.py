# registrasi.py
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox
import theme

from logic_registrasi import RegistrasiBackend
from logic_form_fields import FormFieldsBackend

class RegistrasiWindow(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Registrasi")
        self.transient(master)
        self.configure(fg_color=theme.APP_BG)

        ctk.CTkLabel(self, text="Registrasi", font=theme.font_title(34),
                     text_color=theme.TEXT_PRIMARY).pack(pady=(24, 4))
        ctk.CTkLabel(self, text="Masukkan info mahasiswa", font=theme.font_body(13),
                     text_color=theme.TEXT_SECONDARY).pack(pady=(0, 20))

        # --- FORM INPUT (field wajib, selalu ada) ---
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(pady=10)

        def label(text, r, c):
            ctk.CTkLabel(form_frame, text=text, text_color=theme.ACCENT,
                         font=theme.font_body(11, bold=True)).grid(row=r, column=c, sticky="w", padx=20)

        def entry(r, c):
            e = ctk.CTkEntry(form_frame, width=300, corner_radius=10, fg_color=theme.ENTRY_BG,
                             border_color=theme.ENTRY_BORDER, text_color=theme.TEXT_PRIMARY)
            e.grid(row=r, column=c, padx=20, pady=(0, 15))
            return e

        label("Nama depan", 0, 0)
        self.entry_depan = entry(1, 0)

        label("Nama belakang", 0, 1)
        self.entry_belakang = entry(1, 1)

        label("NIM", 2, 0)
        self.entry_tag = entry(3, 0)

        # --- FIELD TAMBAHAN (dinamis, diatur dari Setting) ---
        self.form_fields_backend = FormFieldsBackend()
        self.extra_entries = {}

        baris = 2
        kolom = 1
        for field in self.form_fields_backend.get_fields():
            label(field["label"], baris, kolom)
            self.extra_entries[field["key"]] = entry(baris + 1, kolom)

            if kolom == 1:
                kolom = 0
                baris += 2
            else:
                kolom = 1

        # --- FRAME KAMERA ---
        cam_frame = ctk.CTkFrame(self, fg_color="transparent")
        cam_frame.pack(pady=10)

        self.btn_daftar = ctk.CTkButton(
            cam_frame, text="Pendaftaran Wajah (Klik Disini)", width=300, corner_radius=10,
            fg_color=theme.ACCENT, text_color=theme.ACCENT_TEXT, hover_color=theme.ACCENT_HOVER,
            font=theme.font_body(12, bold=True), command=self.tombol_mulai_kamera,
        )
        self.btn_daftar.grid(row=0, column=0, padx=20, sticky="n")

        self.video_label = ctk.CTkLabel(cam_frame, text="", fg_color=theme.CARD_BG, corner_radius=10)
        self.video_label.grid(row=0, column=1, padx=20)

        self.instruksi_frame = ctk.CTkFrame(self, width=400, corner_radius=12, fg_color=theme.CARD_BG,
                                             border_width=1, border_color=theme.BORDER)
        self.instruksi_frame.pack(pady=20)

        ctk.CTkLabel(self.instruksi_frame, text="Instruksi", font=theme.font_body(12, bold=True),
                     text_color=theme.ACCENT).pack(anchor="w", padx=12, pady=(8, 0))
        self.lbl_instruksi = ctk.CTkLabel(self.instruksi_frame, text="-", font=theme.font_body(13),
                                           text_color=theme.TEXT_PRIMARY)
        self.lbl_instruksi.pack(anchor="w", padx=12, pady=(0, 12))

        # --- SAMBUNGKAN KE LOGIKA BACKEND ---
        self.backend = RegistrasiBackend()

        tinggi = 700 + (len(self.form_fields_backend.get_fields()) // 2) * 90
        self.geometry(f"900x{min(tinggi, 950)}")

    def tombol_mulai_kamera(self):
        depan = self.entry_depan.get()
        tag = self.entry_tag.get()
        belakang = self.entry_belakang.get()

        if not depan or not tag:
            messagebox.showwarning("Peringatan", "Nama depan dan NIM wajib diisi euy!")
            return

        biodata_tambahan = {key: entry.get() for key, entry in self.extra_entries.items()}

        instruksi_awal = self.backend.mulai_kamera(tag, depan, belakang, biodata_tambahan)
        self.lbl_instruksi.configure(text=instruksi_awal)

        self.btn_daftar.configure(state="disabled", text="Sedang Merekam...")
        self.update_frame_ui()

    def update_frame_ui(self):
        ret, frame, teks_instruksi, is_done = self.backend.proses_frame()

        if ret:
            self.lbl_instruksi.configure(text=teks_instruksi)

            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ctk.CTkImage(light_image=img, size=(300, 225))
            self.video_label.configure(image=imgtk)
            self.video_label.image = imgtk

            if is_done:
                self.backend.matikan_kamera()
                self.video_label.configure(image="")

                self.btn_daftar.configure(text="Sistem Sedang Belajar... Mohon Tunggu", state="disabled")
                self.lbl_instruksi.configure(text="Melatih AI dengan data baru...")
                self.update()

                sukses, pesan = self.backend.latih_model_otomatis()

                self.btn_daftar.configure(state="normal", text="Pendaftaran Wajah (Klik Disini)")
                if sukses:
                    messagebox.showinfo("Mantap!", "Wajah lu udah terdaftar dan sistem udah hafal mukanya.")
                else:
                    messagebox.showerror("Waduh Error", f"Gagal training euy: {pesan}")
                return

        self.after(30, self.update_frame_ui)
