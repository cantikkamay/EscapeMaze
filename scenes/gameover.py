# scenes/gameover.py
import pygame
import math
from utils.config import *
from utils import icons


def draw_gameover(surf, fonts, score, reason="YOU GOT CAUGHT!"):
    font_big, font_mid, font_small, font_tiny = fonts
    mx, my = pygame.mouse.get_pos()
    t      = pygame.time.get_ticks()

    # ── Overlay ───────────────────────────────────────────────────────────────
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surf.blit(overlay, (0, 0))

    # ── Panel ─────────────────────────────────────────────────────────────────
    PW, PH = 620, 400
    box    = pygame.Rect(SCREEN_W // 2 - PW // 2, SCREEN_H // 2 - PH // 2, PW, PH)

    # Shadow
    shadow = pygame.Surface((PW + 20, PH + 20), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 90), (0, 0, PW + 20, PH + 20), border_radius=22)
    surf.blit(shadow, (box.x - 10, box.y + 10))

    pygame.draw.rect(surf, (58, 8, 8),  box, border_radius=20)
    pygame.draw.rect(surf, (82, 14, 14), box.inflate(-12, -12), border_radius=16)

    # Animated red border
    pulse_a = int(abs(math.sin(t * 0.005)) * 100 + 100)
    b_surf  = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.rect(b_surf, (*RED, pulse_a), (0, 0, PW, PH), 4, border_radius=20)
    surf.blit(b_surf, (box.x, box.y))

    CX = box.centerx

    # ── Warning icon ──────────────────────────────────────────────────────────
    warn_y = box.top + 20 + int(math.sin(t * 0.006) * 3)
    icons.draw_icon(surf, "warning", 54, CX, warn_y, center=True)

    # ── Teks ──────────────────────────────────────────────────────────────────
    go_surf = font_big.render("GAME OVER", True, RED)
    surf.blit(go_surf, (CX - go_surf.get_width() // 2, box.top + 82))

    pygame.draw.line(surf, (120, 20, 20),
                     (box.left + 40, box.top + 136), (box.right - 40, box.top + 136), 1)

    r2 = font_mid.render(reason, True, ORANGE)
    surf.blit(r2, (CX - r2.get_width() // 2, box.top + 148))

    sc = font_mid.render(f"SCORE: {score}", True, GOLD)
    surf.blit(sc, (CX - sc.get_width() // 2, box.top + 196))

    pygame.draw.line(surf, (120, 20, 20),
                     (box.left + 40, box.top + 242), (box.right - 40, box.top + 242), 1)

    hint = font_tiny.render("Tekan R atau klik RESTART untuk coba lagi", True, GRAY)
    surf.blit(hint, (CX - hint.get_width() // 2, box.top + 254))

    # ── Tombol ────────────────────────────────────────────────────────────────
    BTN_W, BTN_H = 200, 58
    BTN_Y  = box.bottom - 74
    GAP    = 20
    icon_sz = 26

    btn_r  = pygame.Rect(CX - BTN_W - GAP // 2, BTN_Y, BTN_W, BTN_H)
    btn_m  = pygame.Rect(CX + GAP // 2,          BTN_Y, BTN_W, BTN_H)

    # RESTART
    is_hr = btn_r.collidepoint(mx, my)
    pygame.draw.rect(surf, (170, 35, 35) if is_hr else (110, 20, 20), btn_r, border_radius=13)
    pygame.draw.rect(surf, RED, btn_r, 2, border_radius=13)
    rt_txt  = font_small.render("RESTART", True, WHITE)
    r_total = icon_sz + 6 + rt_txt.get_width()
    r_ix    = btn_r.centerx - r_total // 2
    icons.draw_icon(surf, "restart", icon_sz, r_ix, btn_r.centery - icon_sz // 2)
    surf.blit(rt_txt, (r_ix + icon_sz + 6, btn_r.centery - rt_txt.get_height() // 2))

    # MENU
    is_hm = btn_m.collidepoint(mx, my)
    pygame.draw.rect(surf, (25, 50, 130) if is_hm else (15, 32, 85), btn_m, border_radius=13)
    pygame.draw.rect(surf, CYAN, btn_m, 2, border_radius=13)
    mt_txt  = font_small.render("MAIN MENU", True, WHITE)
    m_total = icon_sz + 6 + mt_txt.get_width()
    m_ix    = btn_m.centerx - m_total // 2
    icons.draw_icon(surf, "house", icon_sz, m_ix, btn_m.centery - icon_sz // 2)
    surf.blit(mt_txt, (m_ix + icon_sz + 6, btn_m.centery - mt_txt.get_height() // 2))

    return btn_r, btn_m
