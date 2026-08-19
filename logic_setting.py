# logic_setting.py
import json
import os
import customtkinter as ctk

SETTINGS_FILE = "settings.json"

class SettingBackend:
    def __init__(self):
        self.settings = self.muat_settings()

    def muat_settings(self):
        # Kalau file settings belum ada, bikin default (light mode)
        if not os.path.exists(SETTINGS_FILE):
            default = {"appearance_mode": "light"}
            self.simpan_settings(default)
            return default

        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            default = {"appearance_mode": "light"}
            self.simpan_settings(default)
            return default

    def simpan_settings(self, data):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def get_appearance_mode(self):
        return self.settings.get("appearance_mode", "light")

    def set_appearance_mode(self, mode):
        # mode: "light" atau "dark"
        ctk.set_appearance_mode(mode)
        self.settings["appearance_mode"] = mode
        self.simpan_settings(self.settings)

    def toggle_appearance_mode(self):
        mode_sekarang = self.get_appearance_mode()
        mode_baru = "dark" if mode_sekarang == "light" else "light"
        self.set_appearance_mode(mode_baru)
        return mode_baru

    @staticmethod
    def terapkan_saat_startup():
        # Dipanggil sebelum Dashboard dibuat, biar app langsung kebuka
        # sesuai tema terakhir yang dipilih user
        backend = SettingBackend()
        mode = backend.get_appearance_mode()
        ctk.set_appearance_mode(mode)
        return mode
