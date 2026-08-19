# edit_user.py
import customtkinter as ctk
import tkinter.messagebox as messagebox
import theme
from logic_dataset import DatasetBackend
from logic_form_fields import FormFieldsBackend

class EditUserWindow(ctk.CTkToplevel):
    def __init__(self, master, user_folder, on_saved=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title(f"Edit Data - {user_folder}")
        self.transient(master)
        self.configure(fg_color=theme.APP_BG)

        self.user_folder = user_folder
        self.on_saved = on_saved
        self.backend = DatasetBackend()
        self.form_fields_backend = FormFieldsBackend()

        ctk.CTkLabel(self, text="Edit Data Mahasiswa", font=theme.font_title(20),
                     text_color=theme.TEXT_PRIMARY).pack(pady=(20, 15))

        biodata = self.backend.get_biodata(user_folder)

        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(pady=10, padx=30, fill="x")

        def field_row(label_text, value=""):
            ctk.CTkLabel(form_frame, text=label_text, text_color=theme.ACCENT,
                         font=theme.font_body(11, bold=True)).pack(anchor="w")
            e = ctk.CTkEntry(form_frame, width=400, corner_radius=10, fg_color=theme.ENTRY_BG,
                             border_color=theme.ENTRY_BORDER, text_color=theme.TEXT_PRIMARY)
            e.insert(0, value)
            e.pack(pady=(0, 12))
            return e

        self.entry_depan = field_row("Nama Depan", biodata.get("nama_depan", ""))
        self.entry_belakang = field_row("Nama Belakang", biodata.get("nama_belakang", ""))
        self.entry_nim = field_row("NIM", biodata.get("nim", ""))

        self.extra_entries = {}
        for field in self.form_fields_backend.get_fields():
            self.extra_entries[field["key"]] = field_row(field["label"], biodata.get(field["key"], ""))

        ctk.CTkButton(
            self, text="Simpan Perubahan", width=200, corner_radius=10, height=36,
            fg_color=theme.ACCENT, text_color=theme.ACCENT_TEXT, hover_color=theme.ACCENT_HOVER,
            font=theme.font_body(13, bold=True), command=self.simpan,
        ).pack(pady=15)

        ctk.CTkLabel(
            self, text="Catatan: perubahan di sini tidak mengubah data wajah\nyang sudah terdaftar.",
            font=theme.font_body(10), text_color=theme.TEXT_SECONDARY,
        ).pack(pady=(0, 10))

        tinggi = 480 + len(self.form_fields_backend.get_fields()) * 55
        self.geometry(f"500x{min(tinggi, 850)}")

    def simpan(self):
        depan = self.entry_depan.get()
        nim = self.entry_nim.get()

        if not depan or not nim:
            messagebox.showwarning("Peringatan", "Nama depan dan NIM wajib diisi euy!")
            return

        biodata_baru = {
            "nama_depan": depan,
            "nama_belakang": self.entry_belakang.get(),
            "nim": nim
        }
        for key, entry in self.extra_entries.items():
            biodata_baru[key] = entry.get()

        self.backend.update_biodata(self.user_folder, biodata_baru)
        messagebox.showinfo("Tersimpan", "Data mahasiswa berhasil diperbarui!")

        if self.on_saved:
            self.on_saved()

        self.destroy()
