# scenes/menu.py
import pygame
import math
from utils.config import *
from utils import icons


def draw_menu(surf, fonts, t, selected_level):
    font_big, font_mid, font_small, font_tiny = fonts
    mx, my = pygame.mouse.get_pos()

    surf.fill(DARK_BLUE)

    # ── Background: radial glow + grid ───────────────────────────────────────
    for r in range(480, 0, -40):
        alpha = max(0, 55 - r // 9)
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 20, 80, alpha), (r, r), r)
        surf.blit(s, (SCREEN_W // 2 - r, SCREEN_H // 2 - r))

    for x in range(0, SCREEN_W, 60):
        pygame.draw.line(surf, (18, 28, 65), (x, 0), (x, SCREEN_H), 1)
    for y in range(0, SCREEN_H, 60):
        pygame.draw.line(surf, (18, 28, 65), (0, y), (SCREEN_W, y), 1)

    # Bintang
    for i in range(50):
        bx = (i * 137 + 50) % SCREEN_W
        by = (i * 97 + 30) % (SCREEN_H - 80)
        br = 1 + i % 3
        alpha = int(abs(math.sin(t * 0.02 + i * 0.4)) * 200 + 55)
        s = pygame.Surface((br * 4, br * 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, alpha), (br * 2, br * 2), br)
        surf.blit(s, (bx - br * 2, by - br * 2))

    # ── Thief icon animasi ────────────────────────────────────────────────────
    thief_y_off = int(math.sin(t * 0.06) * 6)
    icons.draw_icon(surf, "thief", 72, SCREEN_W // 2, 52 + thief_y_off, center=True)

    # ── Judul ─────────────────────────────────────────────────────────────────
    gv = abs(math.sin(t * 0.03)) * 28
    for off in range(6, 0, -1):
        gs = font_big.render("ESCAPE MAZE", True,
                             (int(25 + gv), int(70 + gv), int(170 + gv)))
        surf.blit(gs, (SCREEN_W // 2 - gs.get_width() // 2 + off // 2, 98 + off // 2))
    title = font_big.render("ESCAPE MAZE", True, GOLD)
    surf.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 98))

    sub = font_small.render("Adventure + Maze  |  Single Player", True, CYAN)
    surf.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 166))
    pygame.draw.line(surf, (40, 80, 160), (SCREEN_W//2 - 360, 194), (SCREEN_W//2 + 360, 194), 1)

    # ── Deskripsi ─────────────────────────────────────────────────────────────
    desc = [
        "Kamu adalah PENCURI yang harus melarikan diri dari gedung!",
        "Hindari CCTV, BOM, dan SATPAM untuk kabur ke EXIT.",
    ]
    for i, line in enumerate(desc):
        dt = font_small.render(line, True, (185, 210, 255))
        surf.blit(dt, (SCREEN_W // 2 - dt.get_width() // 2, 212 + i * 32))

    # ── Level Selector ────────────────────────────────────────────────────────
    lv_txt = font_small.render("Pilih Level:", True, WHITE)
    surf.blit(lv_txt, (SCREEN_W // 2 - lv_txt.get_width() // 2, 288))

    lv_data = {1: ("LV 1", "Mudah", GREEN), 2: ("LV 2", "Normal", GOLD), 3: ("LV 3", "Sulit", RED)}
    btn_w, btn_h = 110, 62
    total_w = 3 * btn_w + 2 * 20
    start_x = SCREEN_W // 2 - total_w // 2
    level_rects = {}
    for lv in [1, 2, 3]:
        lbx = start_x + (lv - 1) * (btn_w + 20)
        lb_rect = pygame.Rect(lbx, 318, btn_w, btn_h)
        level_rects[lv] = lb_rect
        is_sel = (lv == selected_level)
        is_hov = lb_rect.collidepoint(mx, my)
        label, sub_label, accent = lv_data[lv]

        bg_col     = (30, 55, 130) if is_sel else ((25, 45, 100) if is_hov else (15, 30, 75))
        border_col = accent if is_sel else (CYAN if is_hov else (40, 65, 140))
        bw         = 3 if is_sel else (2 if is_hov else 1)
        pygame.draw.rect(surf, bg_col, lb_rect, border_radius=12)
        pygame.draw.rect(surf, border_col, lb_rect, bw, border_radius=12)

        lt = font_small.render(label, True, accent if is_sel else WHITE)
        surf.blit(lt, (lb_rect.centerx - lt.get_width() // 2, lb_rect.top + 6))
        st = font_tiny.render(sub_label, True, CYAN if is_sel else GRAY)
        surf.blit(st, (lb_rect.centerx - st.get_width() // 2, lb_rect.top + 34))

    # ── Tombol PLAY ───────────────────────────────────────────────────────────
    bounce = int(math.sin(t * 0.05) * 5)
    play_rect = pygame.Rect(SCREEN_W // 2 - 150, 408 + bounce, 300, 66)
    is_hov = play_rect.collidepoint(mx, my)

    # Glow
    glow_s = pygame.Surface((play_rect.width + 20, play_rect.height + 20), pygame.SRCALPHA)
    glow_a = int(abs(math.sin(t * 0.05)) * 80 + 40)
    pygame.draw.rect(glow_s, (50, 200, 80, glow_a),
                     (0, 0, play_rect.width + 20, play_rect.height + 20), border_radius=18)
    surf.blit(glow_s, (play_rect.x - 10, play_rect.y - 10))

    play_col = (45, 185, 70) if is_hov else (28, 140, 50)
    pygame.draw.rect(surf, play_col, play_rect, border_radius=14)
    pygame.draw.rect(surf, GREEN if is_hov else (60, 200, 90), play_rect, 3, border_radius=14)

    # Ikon play + teks
    icon_size = 32
    pt = font_mid.render("PLAY GAME", True, WHITE)
    total_w_inner = icon_size + 10 + pt.get_width()
    ix = play_rect.centerx - total_w_inner // 2
    iy = play_rect.centery - icon_size // 2
    icons.draw_icon(surf, "play", icon_size, ix, iy)
    surf.blit(pt, (ix + icon_size + 10, play_rect.centery - pt.get_height() // 2))

    # ── Panel Kontrol ─────────────────────────────────────────────────────────
    panel_rect = pygame.Rect(SCREEN_W // 2 - 360, 498, 720, 82)
    pygame.draw.rect(surf, (12, 22, 58), panel_rect, border_radius=12)
    pygame.draw.rect(surf, (30, 55, 120), panel_rect, 1, border_radius=12)

    ctrl_title = font_tiny.render("KONTROL", True, CYAN)
    surf.blit(ctrl_title, (panel_rect.centerx - ctrl_title.get_width() // 2, panel_rect.top + 8))

    ctrl_items = [("WASD / ↑↓←→", "Gerak"), ("ESC / P", "Pause"), ("R", "Restart"), ("Klik", "Interaksi")]
    item_w = panel_rect.width // len(ctrl_items)
    for i, (key, desc) in enumerate(ctrl_items):
        ix2 = panel_rect.left + i * item_w + item_w // 2
        ky = font_small.render(key, True, GOLD)
        dy2 = font_tiny.render(desc, True, GRAY)
        surf.blit(ky, (ix2 - ky.get_width() // 2, panel_rect.top + 28))
        surf.blit(dy2, (ix2 - dy2.get_width() // 2, panel_rect.top + 56))
        if i > 0:
            pygame.draw.line(surf, (30, 55, 120),
                             (panel_rect.left + i * item_w, panel_rect.top + 18),
                             (panel_rect.left + i * item_w, panel_rect.bottom - 8), 1)

    # ── Legend Bahaya (dengan emoticon PNG) ───────────────────────────────────
    leg_items = [
        ("cctv",    CYAN,   "CCTV",   "Deteksi visual"),
        ("guard",   RED,    "SATPAM", "Mengejar & menangkap"),
        ("bomb",    ORANGE, "BOM",    "Hindari kontak"),
        ("door",    GREEN,  "EXIT",   "Tujuan pelarian"),
    ]
    leg_y = 598
    icon_sz = 28
    leg_total = len(leg_items) * 210
    leg_start = SCREEN_W // 2 - leg_total // 2
    for i, (icon_key, col, name, desc) in enumerate(leg_items):
        lx = leg_start + i * 210
        icons.draw_icon(surf, icon_key, icon_sz, lx, leg_y, center=False)
        nm = font_small.render(name, True, col)
        surf.blit(nm, (lx + icon_sz + 6, leg_y))
        dc = font_tiny.render(desc, True, GRAY)
        surf.blit(dc, (lx + icon_sz + 6, leg_y + 22))

    # ── Footer ────────────────────────────────────────────────────────────────
    pygame.draw.line(surf, (30, 50, 110), (0, SCREEN_H - 36), (SCREEN_W, SCREEN_H - 36), 1)
    cr = font_tiny.render(
        "Kelompok 2  –  Praktik Pengembangan Gim  |  Python + Pygame", True, GRAY)
    surf.blit(cr, (SCREEN_W // 2 - cr.get_width() // 2, SCREEN_H - 24))

    return play_rect, level_rects
