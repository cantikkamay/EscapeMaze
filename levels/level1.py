# ─── levels/level1.py ────────────────────────────────────────────────────────
# Level 1: Maze Sederhana
# Sesuai GDD: hanya ada bom, tanpa CCTV dan satpam

LEVEL1_CONFIG = {
    "level"       : 1,
    "title"       : "LEVEL 1 - Maze Sederhana",
    "subtitle"    : "Temukan jalan keluar dan hindari BOM!",
    "guards"      : 0,        # tidak ada satpam
    "cctvs"       : 0,        # tidak ada CCTV
    "bombs"       : 3,        # beberapa bom
    "guard_speed" : 1.0,
    "detect_range": 0,
    # Bom HANYA boleh di tile yang:
    # - bukan dead-end (punya >= 2 tetangga path)
    # - bukan jalur kritis (ada jalur alternatif jika bom ada di sana)
    # - jarak dari start >= min_bomb_dist
    "min_bomb_dist" : 4,
    "bg_color"      : (15, 25, 60),
}
