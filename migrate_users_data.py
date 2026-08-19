# migrate_users_data.py
# Jalankan SEKALI SAJA untuk migrasi users_data.json lama (tanpa biodata)
# supaya kompatibel dengan fitur Edit yang baru. Aman dijalankan berkali-kali.
import json
import os

FILE = "users_data.json"

if os.path.exists(FILE):
    with open(FILE, "r") as f:
        data = json.load(f)

    changed = False
    for user, info in data.items():
        if "biodata" not in info:
            info["biodata"] = {
                "nama_depan": "", "nama_belakang": "", "nim": "",
                "jurusan": "", "no_hp": "", "semester": ""
            }
            changed = True

    if changed:
        with open(FILE, "w") as f:
            json.dump(data, f, indent=4)
        print("Migrasi selesai, users_data.json sudah diupdate.")
    else:
        print("Tidak ada yang perlu dimigrasi.")
else:
    print("users_data.json belum ada, tidak perlu migrasi.")
