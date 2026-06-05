# scenes/gamewin.py
import pygame
import math
from utils.config import *
from utils.score import check_badges, calc_win_bonus
from utils import icons


def draw_win(surf, fonts, score, level, elapsed, no_cctv_hit):
    font_big, font_mid, font_small, font_tiny = fonts
    mx, my = pygame.mouse.get_pos()

    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 188))
    surf.blit(overlay, (0, 0))

    box = pygame.Rect(SCREEN_W//2 - 330, SCREEN_H//2 - 250, 660, 500)
    pygame.draw.rect(surf, (8, 55, 18), box, border_radius=20)
    pygame.draw.rect(surf, GREEN, box, 4, border_radius=20)
    pygame.draw.rect(surf, (12, 75, 25), box.inflate(-16,-16), 1, border_radius=14)

    # ── Trophy + judul ────────────────────────────────────────────────────────
    icons.draw_icon(surf, "trophy", 56, SCREEN_W//2 - 28, box.top + 16)

    win = font_big.render("LEVEL COMPLETE!", True, GREEN)
    surf.blit(win, (SCREEN_W//2 - win.get_width()//2, box.top + 78))

    sub = font_mid.render("YOU ESCAPED THE MAZE!", True, GOLD)
    surf.blit(sub, (SCREEN_W//2 - sub.get_width()//2, box.top + 140))

    # Skor
    bonus = calc_win_bonus()
    sc = font_mid.render(f"SCORE: {score + bonus}", True, GOLD)
    surf.blit(sc, (SCREEN_W//2 - sc.get_width()//2, box.top + 192))

    bonus_txt = font_small.render(f"BONUS: +{bonus}  |  TIME: {elapsed:.1f}s", True, CYAN)
    surf.blit(bonus_txt, (SCREEN_W//2 - bonus_txt.get_width()//2, box.top + 240))

    # ── Badge (dengan ikon trophy) ────────────────────────────────────────────
    badges = check_badges(no_cctv_hit, elapsed)
    badge_y = box.top + 286
    if badges:
        bdg_title = font_small.render("BADGE DIRAIH:", True, ORANGE)
        surf.blit(bdg_title, (SCREEN_W//2 - bdg_title.get_width()//2, badge_y))
        badge_y += 34
        for name, desc in badges:
            # Ikon trophy kecil di samping badge
            icons.draw_icon(surf, "trophy", 22,
                            SCREEN_W//2 - 160, badge_y + 1)
            bt = font_small.render(f"{name}  —  {desc}", True, GOLD)
            surf.blit(bt, (SCREEN_W//2 - 130, badge_y))
            badge_y += 34

    # ── Tombol ────────────────────────────────────────────────────────────────
    has_next = level < 3
    icon_sz = 28

    if has_next:
        # NEXT LEVEL
        next_rect = pygame.Rect(SCREEN_W//2 - 280, box.bottom - 88, 260, 62)
        nc = (35, 165, 65) if next_rect.collidepoint(mx, my) else (20, 110, 42)
        pygame.draw.rect(surf, nc, next_rect, border_radius=12)
        pygame.draw.rect(surf, GREEN, next_rect, 3, border_radius=12)
        if next_rect.collidepoint(mx, my):
            pygame.draw.rect(surf, (120, 255, 140), next_rect, 1, border_radius=12)

        nt_txt = font_small.render("NEXT LEVEL", True, WHITE)
        total_n = icon_sz + 8 + nt_txt.get_width()
        nix = next_rect.centerx - total_n // 2
        icons.draw_icon(surf, "play", icon_sz, nix, next_rect.centery - icon_sz//2)
        surf.blit(nt_txt, (nix + icon_sz + 8, next_rect.centery - nt_txt.get_height()//2))

        # MAIN MENU
        menu_rect = pygame.Rect(SCREEN_W//2 + 20, box.bottom - 88, 260, 62)
        mc = (25, 55, 140) if menu_rect.collidepoint(mx, my) else (15, 35, 95)
        pygame.draw.rect(surf, mc, menu_rect, border_radius=12)
        pygame.draw.rect(surf, CYAN, menu_rect, 2, border_radius=12)

        mt_txt = font_small.render("MAIN MENU", True, WHITE)
        total_m = icon_sz + 8 + mt_txt.get_width()
        mix = menu_rect.centerx - total_m // 2
        icons.draw_icon(surf, "house", icon_sz, mix, menu_rect.centery - icon_sz//2)
        surf.blit(mt_txt, (mix + icon_sz + 8, menu_rect.centery - mt_txt.get_height()//2))

        return next_rect, True, menu_rect
    else:
        # Hanya menu button
        btn_rect = pygame.Rect(SCREEN_W//2 - 140, box.bottom - 88, 280, 62)
        bc = (30, 65, 160) if btn_rect.collidepoint(mx, my) else (18, 42, 110)
        pygame.draw.rect(surf, bc, btn_rect, border_radius=12)
        pygame.draw.rect(surf, CYAN, btn_rect, 2, border_radius=12)

        bt_txt = font_small.render("MAIN MENU", True, WHITE)
        total_b = icon_sz + 8 + bt_txt.get_width()
        bix = btn_rect.centerx - total_b // 2
        icons.draw_icon(surf, "house", icon_sz, bix, btn_rect.centery - icon_sz//2)
        surf.blit(bt_txt, (bix + icon_sz + 8, btn_rect.centery - bt_txt.get_height()//2))

        return btn_rect, False, None
