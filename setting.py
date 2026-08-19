# setting.py
import customtkinter as ctk
import tkinter.messagebox as messagebox
import theme
from logic_setting import SettingBackend
from logic_form_fields import FormFieldsBackend

class SettingWindow(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Setting")
        self.geometry("560x680")
        self.transient(master)
        self.configure(fg_color=theme.APP_BG)

        self.backend = SettingBackend()
        self.form_fields_backend = FormFieldsBackend()

        ctk.CTkLabel(self, text="Setting", font=theme.font_title(26),
                     text_color=theme.TEXT_PRIMARY).pack(pady=(24, 14))

        # --- KARTU 1: Mode Gelap ---
        card = ctk.CTkFrame(self, corner_radius=14, fg_color=theme.CARD_BG,
                             border_width=1, border_color=theme.BORDER)
        card.pack(pady=(0, 15), padx=36, fill="x")

        ctk.CTkLabel(card, text="Tampilan", font=theme.font_body(14, bold=True),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(18, 5))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkLabel(row, text="Mode Gelap", font=theme.font_body(13),
                     text_color=theme.TEXT_PRIMARY).pack(side="left")

        mode_aktif = self.backend.get_appearance_mode()
        self.switch_dark = ctk.CTkSwitch(
            row, text="", command=self.toggle_dark_mode,
            onvalue="dark", offvalue="light",
            progress_color=theme.ACCENT, button_color=theme.ACCENT, button_hover_color=theme.ACCENT_HOVER,
        )
        self.switch_dark.pack(side="right")

        if mode_aktif == "dark":
            self.switch_dark.select()
        else:
            self.switch_dark.deselect()

        self.lbl_status = ctk.CTkLabel(card, text=f"Mode aktif: {mode_aktif.capitalize()}",
                                        font=theme.font_body(11), text_color=theme.TEXT_SECONDARY)
        self.lbl_status.pack(anchor="w", padx=20, pady=(0, 18))

        # --- KARTU 2: Kelola Formulir Regist ---
        card2 = ctk.CTkFrame(self, corner_radius=14, fg_color=theme.CARD_BG,
                              border_width=1, border_color=theme.BORDER)
        card2.pack(pady=5, padx=36, fill="both", expand=True)

        ctk.CTkLabel(card2, text="Kelola Formulir Regist", font=theme.font_body(14, bold=True),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(card2, text="Field 'Nama', 'Nama Belakang', dan 'NIM' selalu ada.\nDi bawah ini kolom tambahan yang bisa diatur:",
                     font=theme.font_body(11), text_color=theme.TEXT_SECONDARY, justify="left").pack(anchor="w", padx=20, pady=(0, 10))

        self.list_frame = ctk.CTkScrollableFrame(card2, fg_color="transparent", height=200)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        add_frame = ctk.CTkFrame(card2, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.entry_field_baru = ctk.CTkEntry(add_frame, placeholder_text="Nama kolom baru, misal: Alamat",
                                              fg_color=theme.ENTRY_BG, border_color=theme.ENTRY_BORDER,
                                              text_color=theme.TEXT_PRIMARY, corner_radius=8)
        self.entry_field_baru.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(add_frame, text="Tambah", width=90, corner_radius=8,
                      fg_color=theme.ACCENT, text_color=theme.ACCENT_TEXT, hover_color=theme.ACCENT_HOVER,
                      font=theme.font_body(12, bold=True), command=self.tambah_field).pack(side="left")

        self.muat_daftar_field()

    def toggle_dark_mode(self):
        mode_baru = self.backend.toggle_appearance_mode()
        self.lbl_status.configure(text=f"Mode aktif: {mode_baru.capitalize()}")

    def muat_daftar_field(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        fields = self.form_fields_backend.get_fields()

        if not fields:
            ctk.CTkLabel(self.list_frame, text="Belum ada kolom tambahan.", font=theme.font_body(12),
                         text_color=theme.TEXT_SECONDARY).pack(pady=10)
            return

        for field in fields:
            row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(row, text=field["label"], font=theme.font_body(12),
                         text_color=theme.TEXT_PRIMARY).pack(side="left", padx=5)

            ctk.CTkButton(row, text="Hapus", width=70, corner_radius=8,
                          fg_color=theme.DANGER, hover_color=theme.DANGER, text_color="#FFFFFF",
                          font=theme.font_body(11),
                          command=lambda k=field["key"]: self.hapus_field(k)).pack(side="right", padx=5)

    def tambah_field(self):
        label = self.entry_field_baru.get()
        sukses, pesan = self.form_fields_backend.tambah_field(label)
        if sukses:
            self.entry_field_baru.delete(0, "end")
            self.muat_daftar_field()
            messagebox.showinfo("Berhasil", pesan)
        else:
            messagebox.showwarning("Gagal", pesan)

    def hapus_field(self, key):
        konfirmasi = messagebox.askyesno("Hapus Kolom", "Yakin mau hapus kolom ini dari formulir?\nData mahasiswa yang sudah ada untuk kolom ini tidak ikut terhapus.")
        if konfirmasi:
            self.form_fields_backend.hapus_field(key)
            self.muat_daftar_field()
