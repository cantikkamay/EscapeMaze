# scenes/gameover.py
import pygame
from utils.config import *
from utils import icons


def draw_gameover(surf, fonts, score, reason="YOU GOT CAUGHT!"):
    font_big, font_mid, font_small, font_tiny = fonts
    mx, my = pygame.mouse.get_pos()

    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surf.blit(overlay, (0, 0))

    box = pygame.Rect(SCREEN_W//2 - 310, SCREEN_H//2 - 205, 620, 410)
    pygame.draw.rect(surf, (55, 8, 8), box, border_radius=20)
    pygame.draw.rect(surf, RED, box, 4, border_radius=20)
    pygame.draw.rect(surf, (80, 15, 15), box.inflate(-16,-16), 1, border_radius=14)

    # ── Warning icon + judul ──────────────────────────────────────────────────
    icons.draw_icon(surf, "warning", 52, SCREEN_W//2 - 26, box.top + 18)
    go = font_big.render("GAME OVER", True, RED)
    surf.blit(go, (SCREEN_W//2 - go.get_width()//2, box.top + 76))

    r2 = font_mid.render(reason, True, ORANGE)
    surf.blit(r2, (SCREEN_W//2 - r2.get_width()//2, box.top + 148))

    sc = font_mid.render(f"SCORE : {score}", True, GOLD)
    surf.blit(sc, (SCREEN_W//2 - sc.get_width()//2, box.top + 200))

    hint = font_tiny.render("Tekan R atau klik RESTART untuk coba lagi", True, GRAY)
    surf.blit(hint, (SCREEN_W//2 - hint.get_width()//2, box.top + 258))

    # ── Tombol RESTART (dengan ikon) ─────────────────────────────────────────
    btn_r = pygame.Rect(SCREEN_W//2 - 160, box.bottom - 88, 150, 58)
    bc = (170, 35, 35) if btn_r.collidepoint(mx, my) else (110, 20, 20)
    pygame.draw.rect(surf, bc, btn_r, border_radius=12)
    pygame.draw.rect(surf, RED, btn_r, 2, border_radius=12)

    icon_sz = 26
    rt_txt = font_small.render("RESTART", True, WHITE)
    total_inner = icon_sz + 6 + rt_txt.get_width()
    bix = btn_r.centerx - total_inner // 2
    icons.draw_icon(surf, "restart", icon_sz, bix, btn_r.centery - icon_sz//2)
    surf.blit(rt_txt, (bix + icon_sz + 6, btn_r.centery - rt_txt.get_height()//2))

    # ── Tombol MAIN MENU (dengan ikon) ───────────────────────────────────────
    btn_m = pygame.Rect(SCREEN_W//2 + 10, box.bottom - 88, 150, 58)
    bmc = (25, 50, 130) if btn_m.collidepoint(mx, my) else (15, 32, 85)
    pygame.draw.rect(surf, bmc, btn_m, border_radius=12)
    pygame.draw.rect(surf, CYAN, btn_m, 2, border_radius=12)

    mt_txt = font_small.render("MENU", True, WHITE)
    total_m = icon_sz + 6 + mt_txt.get_width()
    mix = btn_m.centerx - total_m // 2
    icons.draw_icon(surf, "house", icon_sz, mix, btn_m.centery - icon_sz//2)
    surf.blit(mt_txt, (mix + icon_sz + 6, btn_m.centery - mt_txt.get_height()//2))

    return btn_r, btn_m
