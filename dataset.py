# dataset.py
import customtkinter as ctk
import tkinter.messagebox as messagebox
import theme
from logic_dataset import DatasetBackend
from edit_user import EditUserWindow

class DatasetWindow(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Manajemen Dataset User")
        self.geometry("950x700")
        self.transient(master)
        self.configure(fg_color=theme.APP_BG)

        self.backend = DatasetBackend()

        ctk.CTkLabel(self, text="Manajemen User", font=theme.font_title(28),
                     text_color=theme.TEXT_PRIMARY).pack(pady=(24, 12))

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=36, pady=10)

        self.muat_daftar_user()

    def muat_daftar_user(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        users = self.backend.get_all_users()
        statuses = self.backend.load_statuses()

        if not users:
            ctk.CTkLabel(self.scroll_frame, text="Belum ada user yang terdaftar euy.",
                         font=theme.font_body(13), text_color=theme.TEXT_SECONDARY).pack(pady=20)
            return

        for user in users:
            card = ctk.CTkFrame(self.scroll_frame, corner_radius=12, fg_color=theme.CARD_BG,
                                border_width=1, border_color=theme.BORDER)
            card.pack(fill="x", pady=6, ipadx=10, ipady=10)

            status_info = statuses.get(user, {"status": "Aktif", "sampai": ""})
            teks_status = "Aktif"
            warna_status = theme.SUCCESS

            if status_info["status"] == "BAN":
                teks_status = f"Sedang di Skor (s/d {status_info['sampai']})"
                warna_status = theme.DANGER
            elif status_info["status"] == "CUTI":
                teks_status = "Sedang Ambil Cuti"
                warna_status = theme.WARNING

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10)

            ctk.CTkLabel(info_frame, text=user, font=theme.font_body(16, bold=True),
                         text_color=theme.TEXT_PRIMARY).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=teks_status, font=theme.font_body(11, bold=True),
                         text_color=warna_status).pack(anchor="w")

            biodata = self.backend.get_biodata(user)
            field_dikecualikan = {"nama_depan", "nama_belakang", "nim"}
            ringkasan_parts = [v for k, v in biodata.items() if k not in field_dikecualikan and v]
            if ringkasan_parts:
                ringkasan = " | ".join(ringkasan_parts[:3])
                ctk.CTkLabel(info_frame, text=ringkasan, font=theme.font_body(10),
                             text_color=theme.TEXT_SECONDARY).pack(anchor="w")

            # Tombol Aksi
            ctk.CTkButton(card, text="Edit", width=70, corner_radius=8,
                         fg_color=theme.ACCENT, text_color=theme.ACCENT_TEXT, hover_color=theme.ACCENT_HOVER,
                         font=theme.font_body(11, bold=True),
                         command=lambda u=user: self.aksi_edit(u)).pack(side="right", padx=5)

            ctk.CTkButton(card, text="Hapus", width=70, corner_radius=8,
                         fg_color=theme.BUTTON_MUTED, hover_color=theme.BUTTON_MUTED_HOVER, text_color="#FFFFFF",
                         font=theme.font_body(11),
                         command=lambda u=user: self.aksi_hapus(u)).pack(side="right", padx=5)

            ctk.CTkButton(card, text="BAN", width=70, corner_radius=8,
                         fg_color=theme.DANGER, hover_color=theme.DANGER, text_color="#FFFFFF",
                         font=theme.font_body(11),
                         command=lambda u=user: self.aksi_ban(u)).pack(side="right", padx=5)

            ctk.CTkButton(card, text="Cuti", width=70, corner_radius=8,
                         fg_color=theme.WARNING, hover_color=theme.WARNING, text_color="#FFFFFF",
                         font=theme.font_body(11),
                         command=lambda u=user: self.aksi_cuti(u)).pack(side="right", padx=5)

            ctk.CTkButton(card, text="Aktifkan", width=70, corner_radius=8,
                         fg_color=theme.SUCCESS, hover_color=theme.SUCCESS, text_color="#FFFFFF",
                         font=theme.font_body(11),
                         command=lambda u=user: self.aksi_aktif(u)).pack(side="right", padx=5)

    def aksi_edit(self, user):
        EditUserWindow(self, user, on_saved=self.muat_daftar_user)

    def aksi_aktif(self, user):
        self.backend.set_status(user, "Aktif")
        self.muat_daftar_user()

    def aksi_cuti(self, user):
        self.backend.set_status(user, "CUTI")
        self.muat_daftar_user()
        messagebox.showinfo("Update Status", f"Status {user} diubah jadi Sedang Ambil Cuti.")

    def aksi_ban(self, user):
        dialog = ctk.CTkInputDialog(text="Skor sampai tanggal berapa? (Format: YYYY-MM-DD)", title="BAN User")
        tanggal = dialog.get_input()
        if tanggal:
            self.backend.set_status(user, "BAN", tanggal)
            self.muat_daftar_user()
            messagebox.showwarning("User di-BAN", f"{user} sedang di skor sampai {tanggal}!")

    def aksi_hapus(self, user):
        konfirmasi = messagebox.askyesno("Hapus Permanen", f"Yakin mau hapus {user}?\nDia harus daftar muka lagi kalau mau absen.")
        if konfirmasi:
            sukses, pesan = self.backend.hapus_user(user)
            if sukses:
                messagebox.showinfo("Terhapus", pesan)
            else:
                messagebox.showerror("Error", pesan)
            self.muat_daftar_user()
