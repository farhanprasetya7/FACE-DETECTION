# theme.py
# Palet warna terpusat: hijau tua + emas (terinspirasi referensi travel dashboard)
# Setiap warna berupa tuple (mode_terang, mode_gelap) sesuai konvensi CustomTkinter,
# jadi otomatis ikut appearance_mode yang sudah diatur lewat SettingBackend.

# --- Warna dasar ---
SIDEBAR_BG      = ("#2F4139", "#182821")   # panel navigasi kiri, selalu gelap di 2 mode
APP_BG          = ("#F4EFE4", "#141F1A")   # latar utama window
CARD_BG         = ("#FFFFFF", "#1D2B24")   # kartu/konten
CARD_BG_HOVER   = ("#F7F3E9", "#243329")
BORDER          = ("#EDE7D6", "#33413A")

# --- Aksen ---
ACCENT          = "#D9A94B"                # emas, dipakai sama di kedua mode
ACCENT_HOVER    = "#C79A3F"
ACCENT_TEXT     = "#3B2E10"                # teks di atas latar emas

# --- Teks ---
TEXT_PRIMARY    = ("#2A2E28", "#F2F1E9")
TEXT_SECONDARY  = ("#7A8076", "#9BA79E")
TEXT_ON_SIDEBAR = ("#F4EFE4", "#F4EFE4")
TEXT_ON_SIDEBAR_MUTED = ("#C7CCC1", "#8A9186")

# --- Status semantik ---
SUCCESS         = ("#2F6B3E", "#5FBF77")
DANGER          = ("#B3512F", "#E08A63")
WARNING         = ("#8A6A1C", "#E3C57A")

# --- Avatar / badge ---
AVATAR_BG       = ("#F1E3BF", "#3B331C")
AVATAR_TEXT     = ("#8A6A1C", "#E3C57A")

# --- Form input ---
ENTRY_BG        = ("#FFFFFF", "#20302A")
ENTRY_BORDER    = ("#DED7C4", "#33413A")

# --- Tombol sekunder / netral (Hapus, Cancel, dll) ---
BUTTON_MUTED     = ("#5A5E58", "#3A3F38")
BUTTON_MUTED_HOVER = ("#484C44", "#2C302A")

# --- Font ---
FONT_FAMILY     = "Arial"

def font_title(size=22):
    return (FONT_FAMILY, size, "bold")

def font_body(size=13, bold=False):
    return (FONT_FAMILY, size, "bold" if bold else "normal")
