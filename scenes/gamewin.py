# scenes/gamewin.py
import pygame
import math
from utils.config import *
from utils.score import check_badges, calc_win_bonus
from utils import icons


def _draw_btn(surf, rect, icon_key, label, font, border_col, col_n, col_h, icon_sz=28):
    """Helper: gambar tombol dengan ikon + teks, auto-centered."""
    mx, my = pygame.mouse.get_pos()
    is_h = rect.collidepoint(mx, my)
    pygame.draw.rect(surf, col_h if is_h else col_n, rect, border_radius=14)
    pygame.draw.rect(surf, border_col, rect, 3 if is_h else 2, border_radius=14)
    if is_h:
        # Inner highlight
        inner = rect.inflate(-6, -6)
        glow  = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*border_col, 30), (0, 0, inner.width, inner.height),
                         border_radius=10)
        surf.blit(glow, (inner.x, inner.y))

    txt      = font.render(label, True, WHITE)
    total_w  = icon_sz + 8 + txt.get_width()
    ix       = rect.centerx - total_w // 2
    iy       = rect.centery - icon_sz // 2
    icons.draw_icon(surf, icon_key, icon_sz, ix, iy)
    surf.blit(txt, (ix + icon_sz + 8, rect.centery - txt.get_height() // 2))


def draw_win(surf, fonts, score, level, elapsed, no_cctv_hit):
    """
    Render panel Level Complete.
    Return: (next_rect, has_next, menu_rect)
    """
    font_big, font_mid, font_small, font_tiny = fonts
    mx, my = pygame.mouse.get_pos()
    t = pygame.time.get_ticks()

    # ── Overlay ───────────────────────────────────────────────────────────────
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 195))
    surf.blit(overlay, (0, 0))

    # ── Panel utama ───────────────────────────────────────────────────────────
    PW, PH = 680, 510
    box    = pygame.Rect(SCREEN_W // 2 - PW // 2, SCREEN_H // 2 - PH // 2, PW, PH)

    # Shadow
    shadow = pygame.Surface((PW + 20, PH + 20), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 90), (0, 0, PW + 20, PH + 20), border_radius=22)
    surf.blit(shadow, (box.x - 10, box.y + 10))

    # Body gradient-like (dua lapis)
    pygame.draw.rect(surf, (8, 60, 20),  box, border_radius=20)
    pygame.draw.rect(surf, (12, 80, 28), box.inflate(-12, -12), border_radius=16)

    # Animated border
    pulse_a = int(abs(math.sin(t * 0.003)) * 80 + 120)
    border_surf = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.rect(border_surf, (*GREEN, pulse_a), (0, 0, PW, PH), 4, border_radius=20)
    surf.blit(border_surf, (box.x, box.y))

    CX = box.centerx   # center X referensi untuk semua elemen

    # ── Trophy (animasi float) ────────────────────────────────────────────────
    trophy_y = box.top + 14 + int(math.sin(t * 0.004) * 4)
    icons.draw_icon(surf, "trophy", 58, CX, trophy_y, center=True)

    # ── Judul ─────────────────────────────────────────────────────────────────
    win_surf = font_big.render("LEVEL COMPLETE!", True, GREEN)
    surf.blit(win_surf, (CX - win_surf.get_width() // 2, box.top + 80))

    sub_surf = font_mid.render("YOU ESCAPED THE MAZE!", True, GOLD)
    surf.blit(sub_surf, (CX - sub_surf.get_width() // 2, box.top + 142))

    # ── Divider ───────────────────────────────────────────────────────────────
    pygame.draw.line(surf, (30, 120, 50),
                     (box.left + 40, box.top + 182), (box.right - 40, box.top + 182), 1)

    # ── Score & Bonus ─────────────────────────────────────────────────────────
    bonus    = calc_win_bonus()
    total_sc = score + bonus

    sc_surf  = font_mid.render(f"SCORE: {total_sc}", True, GOLD)
    surf.blit(sc_surf, (CX - sc_surf.get_width() // 2, box.top + 194))

    # Bonus + Time dalam satu baris, benar-benar centered
    bonus_str = f"BONUS: +{bonus}"
    time_str  = f"TIME: {elapsed:.1f}s"
    sep_str   = "  |  "
    full_str  = bonus_str + sep_str + time_str
    full_surf = font_small.render(full_str, True, CYAN)
    surf.blit(full_surf, (CX - full_surf.get_width() // 2, box.top + 242))

    # ── Divider ───────────────────────────────────────────────────────────────
    pygame.draw.line(surf, (30, 120, 50),
                     (box.left + 40, box.top + 276), (box.right - 40, box.top + 276), 1)

    # ── Badge ─────────────────────────────────────────────────────────────────
    badges  = check_badges(no_cctv_hit, elapsed)
    badge_y = box.top + 288

    if badges:
        bdg_title = font_small.render("BADGE DIRAIH:", True, ORANGE)
        surf.blit(bdg_title, (CX - bdg_title.get_width() // 2, badge_y))
        badge_y += 32
        for name, desc in badges:
            row_str  = f"{name}  —  {desc}"
            row_surf = font_small.render(row_str, True, GOLD)
            icon_total = 22 + 6 + row_surf.get_width()
            row_x    = CX - icon_total // 2
            icons.draw_icon(surf, "trophy", 22, row_x, badge_y + 1)
            surf.blit(row_surf, (row_x + 22 + 6, badge_y))
            badge_y += 34
    else:
        # Teks dorongan kecil jika tidak dapat badge
        tip = font_tiny.render("Selesaikan lebih cepat atau tanpa kena CCTV untuk badge!", True, GRAY)
        surf.blit(tip, (CX - tip.get_width() // 2, badge_y + 8))

    # ── Tombol ────────────────────────────────────────────────────────────────
    has_next  = level < 3
    BTN_W, BTN_H = 260, 58
    BTN_Y     = box.bottom - 76
    GAP       = 20

    if has_next:
        next_rect = pygame.Rect(CX - BTN_W - GAP // 2, BTN_Y, BTN_W, BTN_H)
        menu_rect = pygame.Rect(CX + GAP // 2,          BTN_Y, BTN_W, BTN_H)

        _draw_btn(surf, next_rect, "play",  "NEXT LEVEL", font_small,
                  GREEN,  (18, 110, 40), (30, 165, 65))
        _draw_btn(surf, menu_rect, "house", "MAIN MENU",  font_small,
                  CYAN,   (15, 35, 95),  (25, 55, 140))

        return next_rect, True, menu_rect
    else:
        # Level 3 selesai — hanya satu tombol
        menu_rect = pygame.Rect(CX - BTN_W // 2, BTN_Y, BTN_W, BTN_H)
        _draw_btn(surf, menu_rect, "house", "MAIN MENU", font_small,
                  CYAN, (15, 35, 95), (25, 55, 140))
        return menu_rect, False, None
