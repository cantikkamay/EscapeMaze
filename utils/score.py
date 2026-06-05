# ─── utils/score.py ──────────────────────────────────────────────────────────
# Sistem skor sesuai GDD:
#   +10 poin setiap langkah mendekati exit
#   +50 poin jika berhasil keluar (bonus)

import math
from utils.config import COLS, ROWS


def calc_proximity_score(player_gx, player_gy):
    """Hitung skor berdasarkan jarak ke exit (semakin dekat = lebih tinggi)."""
    exit_x, exit_y = COLS - 2, ROWS - 2
    dist = math.hypot(player_gx - exit_x, player_gy - exit_y)
    max_dist = math.hypot(COLS, ROWS)
    proximity = max(0, max_dist - dist)
    return int(proximity * 10)


def calc_win_bonus():
    """Bonus poin saat berhasil keluar."""
    return 50


def check_badges(no_cctv_hit: bool, elapsed: float, fast_threshold: float = 30.0):
    """
    Kembalikan list badge yang diraih.
    - 'Survivor' : menang tanpa pernah kena CCTV
    - 'Speed Runner' : menang dalam waktu <= fast_threshold detik
    """
    badges = []
    if no_cctv_hit:
        badges.append(("SURVIVOR", "Menang tanpa kena CCTV!"))
    if elapsed <= fast_threshold:
        badges.append(("SPEED RUNNER", f"Selesai dalam {elapsed:.1f}s!"))
    return badges
