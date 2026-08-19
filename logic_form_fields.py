# logic_form_fields.py
import json
import os
import re

FORM_FIELDS_FILE = "form_fields.json"

# Field default kalau file belum ada (pertama kali dijalankan)
DEFAULT_FIELDS = [
    {"key": "jurusan", "label": "Jurusan/Prodi"},
    {"key": "no_hp", "label": "No. HP/WhatsApp"},
    {"key": "semester", "label": "Semester"}
]

class FormFieldsBackend:
    def __init__(self):
        self.pastikan_file_ada()

    def pastikan_file_ada(self):
        if not os.path.exists(FORM_FIELDS_FILE):
            self.simpan_fields(DEFAULT_FIELDS)

    def get_fields(self):
        try:
            with open(FORM_FIELDS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return DEFAULT_FIELDS

    def simpan_fields(self, fields):
        with open(FORM_FIELDS_FILE, "w") as f:
            json.dump(fields, f, indent=4)

    def buat_key(self, label):
        # Ubah "Nomor KTM" jadi "nomor_ktm" biar aman dipakai sebagai key JSON
        key = label.strip().lower()
        key = re.sub(r"[^a-z0-9]+", "_", key).strip("_")
        return key

    def tambah_field(self, label):
        label = label.strip()
        if not label:
            return False, "Nama kolom gak boleh kosong euy!"

        key = self.buat_key(label)
        fields = self.get_fields()

        if any(f["key"] == key for f in fields):
            return False, "Kolom dengan nama itu udah ada!"

        fields.append({"key": key, "label": label})
        self.simpan_fields(fields)
        return True, "Kolom formulir berhasil ditambahin!"

    def hapus_field(self, key):
        fields = self.get_fields()
        fields = [f for f in fields if f["key"] != key]
        self.simpan_fields(fields)
