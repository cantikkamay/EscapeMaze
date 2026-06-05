"""
utils/icons.py
Sistem pemuatan emoticon PNG terpusat.
Semua scene mengimport ICONS dari sini.
"""
import os
import pygame

_EMOTICON_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "assets", "images", "emoticon"
)

# Mapping nama logis → nama file PNG
_FILES = {
    "bomb"       : "bomb.png",
    "cctv"       : "camera-with-flash.png",
    "door"       : "door.png",
    "house"      : "house.png",
    "guard"      : "man-police.png",
    "play"       : "play-button.png",
    "heart"      : "red-heart.png",
    "restart"    : "restart.png",
    "thief"      : "thief.png",
    "trophy"     : "trophy.png",
    "warning"    : "warning.png",
}

ICONS: dict[str, pygame.Surface | None] = {}

def load_icons():
    """Panggil sekali setelah pygame.init(). Isi dict ICONS."""
    for key, fname in _FILES.items():
        path = os.path.join(_EMOTICON_DIR, fname)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                ICONS[key] = img
            except Exception as e:
                print(f"[icons] Gagal load {fname}: {e}")
                ICONS[key] = None
        else:
            print(f"[icons] File tidak ditemukan: {path}")
            ICONS[key] = None

def get(key: str, size: int) -> pygame.Surface | None:
    """
    Kembalikan Surface emoticon yang sudah di-scale ke `size x size`.
    Return None jika tidak tersedia.
    """
    img = ICONS.get(key)
    if img is None:
        return None
    return pygame.transform.smoothscale(img, (size, size))

def draw_icon(surf: pygame.Surface, key: str, size: int, x: int, y: int,
              center: bool = False):
    """
    Gambar emoticon `key` dengan ukuran `size` pada posisi (x,y).
    Jika center=True, (x,y) adalah titik tengah gambar.
    Kembalikan lebar gambar yang dipakai (size jika ada, 0 jika tidak).
    """
    img = get(key, size)
    if img is None:
        return 0
    bx = x - size // 2 if center else x
    by = y - size // 2 if center else y
    surf.blit(img, (bx, by))
    return size
