# scenes/gameplay.py
import pygame
import math
from utils.config import *
from utils import icons


def draw_maze(surf, grid, fonts):
    font_tiny = fonts[3]
    for y in range(ROWS):
        for x in range(COLS):
            rx = MAZE_X + x * TILE
            ry = MAZE_Y + y * TILE
            if grid[y][x] == 1:
                pygame.draw.rect(surf, WALL_COLOR, (rx, ry, TILE, TILE))
                pygame.draw.rect(surf, WALL_TOP,   (rx+1, ry+1, TILE-3, TILE-3))
                pygame.draw.rect(surf, (35, 75, 145), (rx+1, ry+1, TILE-3, 4))
            else:
                pygame.draw.rect(surf, FLOOR_COLOR, (rx, ry, TILE, TILE))
                pygame.draw.rect(surf, FLOOR_DARK,  (rx+1, ry+1, TILE-2, TILE-2))

    # EXIT tile – animasi pulse + ikon door
    ex = MAZE_X + (COLS - 2) * TILE
    ey = MAZE_Y + (ROWS - 2) * TILE
    pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 40
    exit_color = (int(30 + pulse), int(180 + pulse//2), int(30 + pulse))
    pygame.draw.rect(surf, exit_color, (ex, ey, TILE, TILE))
    pygame.draw.rect(surf, GREEN, (ex+2, ey+2, TILE-4, TILE-4), 2)
    # Ikon door terpusat di tile exit
    icons.draw_icon(surf, "door", TILE - 6, ex + 3, ey + 3)

    # START tile
    pygame.draw.rect(surf, (50, 110, 55), (MAZE_X + TILE, MAZE_Y + TILE, TILE, TILE), 2)
    st = font_tiny.render("GO", True, GREEN)
    surf.blit(st, (MAZE_X + TILE + TILE//2 - st.get_width()//2,
                   MAZE_Y + TILE + TILE//2 - st.get_height()//2))


def draw_hud(surf, player, level, elapsed, fonts, cfg_title):
    font_big, font_mid, font_small, font_tiny = fonts

    pygame.draw.rect(surf, (10, 15, 40), (0, 0, SCREEN_W, 88))
    pygame.draw.line(surf, CYAN, (0, 88), (SCREEN_W, 88), 2)

    title = font_mid.render("ESCAPE MAZE", True, GOLD)
    surf.blit(title, (SCREEN_W//2 - title.get_width()//2, 12))

    # ── Nyawa: ikon heart PNG ─────────────────────────────────────────────────
    heart_sz = 34
    for i in range(3):
        hx = 16 + i * (heart_sz + 6)
        hy = 26
        if i < player.lives:
            icons.draw_icon(surf, "heart", heart_sz, hx, hy)
        else:
            # Hati abu-abu (surface diarsir)
            ghost = icons.get("heart", heart_sz)
            if ghost:
                dark = ghost.copy()
                dark.fill((60, 60, 60, 180), special_flags=pygame.BLEND_RGBA_MULT)
                surf.blit(dark, (hx, hy))
            else:
                pygame.draw.rect(surf, DARK_GRAY, (hx, hy, heart_sz, heart_sz), border_radius=4)

    # Score
    sc = font_small.render(f"SCORE: {player.score:04d}", True, GOLD)
    surf.blit(sc, (SCREEN_W - sc.get_width() - 18, 10))

    # Level
    lv = font_small.render(f"LEVEL {level}", True, CYAN)
    surf.blit(lv, (SCREEN_W - lv.get_width() - 18, 48))

    # Timer
    secs = int(elapsed)
    timer_col = RED if secs > 90 else WHITE
    tmr = font_small.render(f"{secs}s", True, timer_col)
    surf.blit(tmr, (18, 60))

    # Pause hint
    ph = font_tiny.render("P/ESC = Pause", True, GRAY)
    surf.blit(ph, (SCREEN_W//2 - ph.get_width()//2, 70))

    # Bottom bar
    lt = font_tiny.render(cfg_title, True, CYAN)
    surf.blit(lt, (SCREEN_W//2 - lt.get_width()//2, SCREEN_H - 22))
