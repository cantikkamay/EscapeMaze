import pygame, sys, os, random, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config   import *
from utils          import icons
from utils.enemy_ai import bfs_path, is_dead_end, is_on_critical_path
from utils.score    import calc_proximity_score, calc_win_bonus

from levels.level1 import LEVEL1_CONFIG
from levels.level2 import LEVEL2_CONFIG
from levels.level3 import LEVEL3_CONFIG

from scenes.menu     import draw_menu
from scenes.gameplay import draw_maze, draw_hud
from scenes.gameover import draw_gameover
from scenes.gamewin  import draw_win

# ─── INIT ─────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
try:
    pygame.mixer.init()
    AUDIO_OK = True
except Exception:
    AUDIO_OK = False

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption(TITLE)

_icon = pygame.Surface((32, 32), pygame.SRCALPHA)
pygame.draw.rect(_icon, (20, 50, 100), (0, 0, 32, 32))
pygame.draw.rect(_icon, (50, 200, 80), (0, 0, 32, 32), 2)
pygame.draw.circle(_icon, GOLD, (8, 22), 4)
pygame.draw.rect(_icon, GREEN, (22, 20, 8, 8))
pygame.display.set_icon(_icon)

clock = pygame.time.Clock()
icons.load_icons()

# ─── FONT ─────────────────────────────────────────────────────────────────────
def load_fonts():
    fp = os.path.join(os.path.dirname(__file__), "assets", "fonts", "main_font.ttf")
    if os.path.exists(fp):
        try:
            return (pygame.font.Font(fp, 56), pygame.font.Font(fp, 32),
                    pygame.font.Font(fp, 22), pygame.font.Font(fp, 16))
        except Exception:
            pass
    return (pygame.font.SysFont("consolas", 56, bold=True),
            pygame.font.SysFont("consolas", 32, bold=True),
            pygame.font.SysFont("consolas", 22),
            pygame.font.SysFont("consolas", 16))

FONTS = load_fonts()

# ─── AUDIO ────────────────────────────────────────────────────────────────────
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets", "audio")

def load_sound(fname):
    for ext in [fname, fname.replace(".wav", ".mp3"), fname.replace(".mp3", ".wav")]:
        p = os.path.join(AUDIO_DIR, ext)
        if AUDIO_OK and os.path.exists(p):
            try:
                return pygame.mixer.Sound(p)
            except Exception:
                continue
    return None

sfx_alarm     = load_sound("alarm.wav")
sfx_explosion = load_sound("explosion.wav")
sfx_footstep  = load_sound("footsteps.wav")
sfx_win       = load_sound("win.wav")
sfx_hit       = load_sound("hit.wav")
sfx_click     = load_sound("Menu Selection Click.wav")  

# ── BGM loop ──────────────────────────────────────────────────────────────────
_music_loaded = False
for snd_name in ["soundtrack.ogg", "soundtrack.ogg"]:
    snd_path = os.path.join(AUDIO_DIR, snd_name)
    if AUDIO_OK and os.path.exists(snd_path):
        try:
            pygame.mixer.music.load(snd_path)
            pygame.mixer.music.set_volume(0.38)
            pygame.mixer.music.play(-1)
            _music_loaded = True
            break
        except Exception as e:
            print(f"[audio] Gagal load {snd_name}: {e}")

if not _music_loaded:
    print("[audio] Soundtrack tidak ditemukan — game berjalan tanpa musik.")

def play_sfx(sound, vol=0.7):
    if sound:
        sound.set_volume(vol)
        sound.play()

def play_win_sfx():
    """Mainkan SFX menang. Jika win.wav tidak ada, pakai explosion dengan pitch effect."""
    if sfx_win:
        play_sfx(sfx_win, 0.8)
    elif sfx_alarm:
        # Fallback: alarm 2x sebagai simulasi 'fanfare'
        play_sfx(sfx_alarm, 0.6)

def play_hit_sfx():
    """Mainkan SFX saat kena rintangan/nyawa berkurang."""
    if sfx_hit:
        play_sfx(sfx_hit, 0.8)
    elif sfx_alarm:
        play_sfx(sfx_alarm, 0.5)
        
def play_click_sfx():
    play_sfx(sfx_click, 0.8)

# ─── LEVEL CONFIGS ────────────────────────────────────────────────────────────
LEVEL_CONFIGS = {1: LEVEL1_CONFIG, 2: LEVEL2_CONFIG, 3: LEVEL3_CONFIG}

# ─── GENERATE MAZE ────────────────────────────────────────────────────────────
def generate_maze(cols, rows):
    grid = [[1] * cols for _ in range(rows)]

    def carve(cx, cy):
        grid[cy][cx] = 0
        dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 1:
                grid[cy + dy // 2][cx + dx // 2] = 0
                carve(nx, ny)

    carve(1, 1)
    grid[1][1] = 0
    grid[rows - 2][cols - 2] = 0
    return grid

def add_extra_connections(grid, cols, rows, count=8):
    added = 0
    attempts = 0
    while added < count and attempts < 600:
        attempts += 1
        x = random.randrange(2, cols - 1)
        y = random.randrange(2, rows - 1)
        if grid[y][x] == 1:
            nb = sum(1 for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                     if 0 <= x + dx < cols and 0 <= y + dy < rows
                     and grid[y + dy][x + dx] == 0)
            if nb >= 2:
                grid[y][x] = 0
                added += 1

# ─── PARTICLE ─────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y   = x, y
        self.vx          = random.uniform(-4, 4)
        self.vy          = random.uniform(-6, -0.5)
        self.color       = color
        self.life        = random.randint(18, 48)
        self.max_life    = self.life
        self.r           = random.randint(2, 6)

    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vy += 0.22;   self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            r = max(1, int(self.r * (self.life / self.max_life)))
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), r)

particles = []

def spawn_particles(x, y, color, count=20):
    for _ in range(count):
        particles.append(Particle(x, y, color))

# ─── PLAYER ───────────────────────────────────────────────────────────────────
class Player:
    def __init__(self, x, y):
        self.gx, self.gy   = x, y
        self.px             = MAZE_X + x * TILE + TILE // 2
        self.py             = MAZE_Y + y * TILE + TILE // 2
        self.tx, self.ty    = self.px, self.py
        self.moving         = False
        self.speed          = 4
        self.lives          = 3
        self.score          = 0
        self.invincible     = 0
        self.direction      = 1
        self.step_sfx_t     = 0

    def try_move(self, dx, dy, grid):
        if self.moving: return
        nx, ny = self.gx + dx, self.gy + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == 0:
            self.gx, self.gy = nx, ny
            self.tx = MAZE_X + nx * TILE + TILE // 2
            self.ty = MAZE_Y + ny * TILE + TILE // 2
            self.moving = True
            if dx > 0: self.direction = 1
            if dx < 0: self.direction = -1
            self.step_sfx_t -= 1
            if self.step_sfx_t <= 0:
                play_sfx(sfx_footstep, 0.25)
                self.step_sfx_t = 8

    def update(self):
        if self.moving:
            dx   = self.tx - self.px
            dy   = self.ty - self.py
            dist = math.hypot(dx, dy)
            if dist <= self.speed:
                self.px, self.py = self.tx, self.ty
                self.moving = False
            else:
                self.px += dx / dist * self.speed
                self.py += dy / dist * self.speed
        if self.invincible > 0:
            self.invincible -= 1

    def draw(self, surf):
        blink = self.invincible > 0 and (self.invincible // 5) % 2 == 0
        if blink: return
        cx, cy = int(self.px), int(self.py)
        r = TILE // 2 - 3
        thief_img = icons.get("thief", TILE - 4)
        if thief_img:
            if self.direction == -1:
                thief_img = pygame.transform.flip(thief_img, True, False)
            surf.blit(thief_img, (cx - thief_img.get_width() // 2,
                                   cy - thief_img.get_height() // 2))
        else:
            shad = pygame.Surface((r * 2, 10), pygame.SRCALPHA)
            pygame.draw.ellipse(shad, (0, 0, 0, 80), (0, 0, r * 2, 10))
            surf.blit(shad, (cx - r, cy + r - 4))
            body_rect = pygame.Rect(cx - r + 2, cy - 2, (r - 2) * 2, r + 5)
            pygame.draw.rect(surf, (22, 22, 22), body_rect, border_radius=5)
            for i in range(3):
                sx = body_rect.left + i * (body_rect.width // 3)
                pygame.draw.line(surf, WHITE, (sx, body_rect.top), (sx, body_rect.bottom), 2)
            pygame.draw.circle(surf, (255, 215, 175), (cx, cy - r + 4), r - 3)
            pygame.draw.rect(surf, (12, 12, 12), (cx - (r - 2), cy - r * 2 + 5, (r - 2) * 2, r - 2))
            pygame.draw.rect(surf, (12, 12, 12), (cx - r, cy - r - 4, r * 2, 6))
            eo = 4 if self.direction == 1 else -4
            pygame.draw.circle(surf, WHITE, (cx + eo, cy - r + 6), 3)
            pygame.draw.circle(surf, BLACK, (cx + eo + self.direction, cy - r + 6), 2)
        # nyawa mini
        for i in range(max(0, self.lives)):
            hx = cx - 10 + i * 10
            pygame.draw.circle(surf, RED, (hx - 2, cy - r - 9), 3)
            pygame.draw.circle(surf, RED, (hx + 2, cy - r - 9), 3)
            pygame.draw.polygon(surf, RED,
                                [(hx - 5, cy - r - 7), (hx + 5, cy - r - 7), (hx, cy - r - 2)])

# ─── GUARD ────────────────────────────────────────────────────────────────────
class Guard:
    def __init__(self, x, y, speed_mult=1.0, detect_range=5):
        self.gx, self.gy   = x, y
        self.px             = MAZE_X + x * TILE + TILE // 2
        self.py             = MAZE_Y + y * TILE + TILE // 2
        self.tx, self.ty    = self.px, self.py
        self.moving         = False
        self.speed          = 3.0 * speed_mult
        self.path           = []
        self.path_timer     = 0
        self.detect_range   = detect_range
        self.chasing        = False
        self.direction      = 1
        self.alarm_t        = 0

    def update(self, grid, pgx, pgy):
        self.alarm_t += 0.1
        self.chasing = math.hypot(pgx - self.gx, pgy - self.gy) <= self.detect_range
        self.path_timer -= 1
        if not self.moving and self.path_timer <= 0:
            if self.chasing:
                self.path = bfs_path(grid, (self.gx, self.gy), (pgx, pgy))
                self.path_timer = 6
                if self.alarm_t > 1:
                    play_sfx(sfx_alarm, 0.15)
                    self.alarm_t = 0
            else:
                dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                random.shuffle(dirs)
                for ddx, ddy in dirs:
                    nx, ny = self.gx + ddx, self.gy + ddy
                    if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == 0:
                        self.path = [(self.gx, self.gy), (nx, ny)]
                        self.path_timer = 28
                        break
            if self.path and len(self.path) > 1:
                prev = self.gx
                nx, ny = self.path[1]
                self.gx, self.gy = nx, ny
                self.tx = MAZE_X + nx * TILE + TILE // 2
                self.ty = MAZE_Y + ny * TILE + TILE // 2
                self.moving = True
                if nx > prev: self.direction = 1
                elif nx < prev: self.direction = -1
        if self.moving:
            dx = self.tx - self.px; dy = self.ty - self.py
            d  = math.hypot(dx, dy)
            if d <= self.speed:
                self.px, self.py = self.tx, self.ty
                self.moving = False
            else:
                self.px += dx / d * self.speed
                self.py += dy / d * self.speed

    def draw(self, surf):
        cx, cy = int(self.px), int(self.py)
        r = TILE // 2 - 3
        if self.chasing:
            aura = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
            pygame.draw.circle(aura, (255, 60, 60, 35), (r * 3, r * 3), r * 3)
            surf.blit(aura, (cx - r * 3, cy - r * 3))
        guard_img = icons.get("guard", TILE - 2)
        if guard_img:
            if self.direction == -1:
                guard_img = pygame.transform.flip(guard_img, True, False)
            if self.chasing:
                red_tint = guard_img.copy()
                red_tint.fill((255, 100, 100, 0), special_flags=pygame.BLEND_RGB_ADD)
                guard_img = red_tint
            surf.blit(guard_img, (cx - guard_img.get_width() // 2,
                                   cy - guard_img.get_height() // 2))
        else:
            pygame.draw.ellipse(surf, BLACK, (cx - r + 3, cy + r - 4, r * 2 - 4, 8))
            body_col = (28, 45, 140) if not self.chasing else (140, 28, 28)
            pygame.draw.rect(surf, body_col, (cx - r + 2, cy - 2, (r - 2) * 2, r + 5), border_radius=5)
            pygame.draw.circle(surf, (255, 205, 165), (cx, cy - r + 4), r - 3)
            pygame.draw.rect(surf, (18, 28, 75), (cx - (r - 4), cy - r * 2 + 5, (r - 4) * 2, r - 4))
            pygame.draw.rect(surf, (18, 28, 75), (cx - r + 2, cy - r - 3, (r - 2) * 2, 4))
            pygame.draw.circle(surf, GOLD, (cx, cy - r * 2 + 9), 4)
        lbl = FONTS[3].render("SATPAM", True, RED if self.chasing else GRAY)
        surf.blit(lbl, (cx - lbl.get_width() // 2, cy - r * 2 - 10))

# ─── CCTV ─────────────────────────────────────────────────────────────────────
class CCTV:
    def __init__(self, x, y):
        self.gx, self.gy = x, y
        self.px = MAZE_X + x * TILE + TILE // 2
        self.py = MAZE_Y + y * TILE + TILE // 2
        self.angle     = random.uniform(-60, 60)
        self.sweep_dir = random.choice([-1, 1])
        self.fov       = 90
        self.range     = 3

    def update(self):
        self.angle += 0.75 * self.sweep_dir
        if self.angle > 65 or self.angle < -65:
            self.sweep_dir *= -1

    def in_view(self, pgx, pgy, grid):
        dx   = pgx - self.gx; dy = pgy - self.gy
        dist = math.hypot(dx, dy)
        if dist > self.range or dist == 0: return False
        base = math.degrees(math.atan2(dy, dx))
        diff = (base - self.angle + 180) % 360 - 180
        return abs(diff) < self.fov / 2

    def draw(self, surf):
        cx, cy = int(self.px), int(self.py)
        cone_size = TILE * self.range * 2 + 40
        cone_surf = pygame.Surface((cone_size, cone_size), pygame.SRCALPHA)
        rad    = math.radians(self.angle)
        center = cone_size // 2
        pts    = [(center, center)]
        for a in range(-int(self.fov / 2), int(self.fov / 2) + 1, 4):
            ar = math.radians(a) + rad
            pts.append((center + math.cos(ar) * TILE * self.range,
                        center + math.sin(ar) * TILE * self.range))
        if len(pts) > 2:
            pygame.draw.polygon(cone_surf, (255, 60, 60, 38), pts)
        surf.blit(cone_surf, (cx - center, cy - center))
        cctv_img = icons.get("cctv", TILE - 6)
        if cctv_img:
            rot_img = pygame.transform.rotate(cctv_img, -self.angle)
            surf.blit(rot_img, (cx - rot_img.get_width() // 2,
                                cy - rot_img.get_height() // 2))
        else:
            pygame.draw.rect(surf, DARK_GRAY, (cx - 11, cy - 7, 22, 14), border_radius=3)
            pygame.draw.circle(surf, CYAN,  (cx, cy), 5)
            pygame.draw.circle(surf, BLACK, (cx, cy), 3)
        if int(pygame.time.get_ticks() / 420) % 2:
            pygame.draw.circle(surf, RED, (cx + 9, cy - 9), 4)
        lbl = FONTS[3].render("CCTV", True, CYAN)
        surf.blit(lbl, (cx - lbl.get_width() // 2, cy - TILE // 2 - 12))

# ─── BOMB ─────────────────────────────────────────────────────────────────────
class Bomb:
    def __init__(self, x, y):
        self.gx, self.gy = x, y
        self.px = MAZE_X + x * TILE + TILE // 2
        self.py = MAZE_Y + y * TILE + TILE // 2
        self.anim_t = random.uniform(0, math.pi * 2)
        self.active = True

    def draw(self, surf):
        if not self.active: return
        self.anim_t += 0.05
        cx, cy = int(self.px), int(self.py)
        b = int(math.sin(self.anim_t * 3) * 3)
        bomb_img = icons.get("bomb", TILE - 4)
        if bomb_img:
            surf.blit(bomb_img, (cx - bomb_img.get_width() // 2,
                                  cy - bomb_img.get_height() // 2 + b))
        else:
            pygame.draw.circle(surf, (18, 18, 18), (cx, cy + b), 12)
            pygame.draw.circle(surf, (38, 38, 38), (cx - 2, cy - 2 + b), 10)
            pygame.draw.line(surf, (95, 68, 28), (cx + 6, cy - 10 + b), (cx + 11, cy - 19 + b), 3)
            spark = int(self.anim_t * 10) % 3
            pygame.draw.circle(surf, [RED, ORANGE, GOLD][spark], (cx + 11, cy - 19 + b), 4)

# ─── SETUP LEVEL ──────────────────────────────────────────────────────────────
def setup_level(level: int):
    cfg  = LEVEL_CONFIGS.get(level, LEVEL3_CONFIG)
    grid = generate_maze(COLS, ROWS)
    add_extra_connections(grid, COLS, ROWS, count=8)
    player   = Player(1, 1)
    START    = (1, 1)
    EXIT     = (COLS - 2, ROWS - 2)
    min_bd   = cfg.get("min_bomb_dist", 4)
    free_tiles = [(x, y) for y in range(1, ROWS - 1) for x in range(1, COLS - 1)
                  if grid[y][x] == 0 and (x, y) != START and (x, y) != EXIT]
    random.shuffle(free_tiles)

    guards = []; guard_pos = set()
    for _ in range(cfg["guards"]):
        for gx, gy in free_tiles:
            if (gx, gy) not in guard_pos and math.hypot(gx - 1, gy - 1) > 5:
                guards.append(Guard(gx, gy, speed_mult=cfg["guard_speed"],
                                    detect_range=cfg.get("detect_range", 5)))
                guard_pos.add((gx, gy)); break

    cctvs = []; cctv_pos = set()
    for cx2, cy2 in free_tiles:
        if len(cctvs) >= cfg["cctvs"]: break
        if (cx2, cy2) not in guard_pos and (cx2, cy2) not in cctv_pos:
            cctvs.append(CCTV(cx2, cy2)); cctv_pos.add((cx2, cy2))

    bombs = []; bomb_pos = set()
    used  = guard_pos | cctv_pos | {START, EXIT}
    for bx, by in free_tiles:
        if len(bombs) >= cfg["bombs"]: break
        if (bx, by) in used or (bx, by) in bomb_pos: continue
        if math.hypot(bx - 1, by - 1) < min_bd: continue
        if is_dead_end(grid, bx, by): continue
        if is_on_critical_path(grid, bx, by, start=START): continue
        bombs.append(Bomb(bx, by)); bomb_pos.add((bx, by))

    return grid, player, guards, cctvs, bombs, cfg

# ─── PAUSE OVERLAY ────────────────────────────────────────────────────────────
def draw_pause(surf, fonts):
    font_big, font_mid, font_small, font_tiny = fonts
    mx, my = pygame.mouse.get_pos()

    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    surf.blit(overlay, (0, 0))

    box = pygame.Rect(SCREEN_W // 2 - 250, SCREEN_H // 2 - 195, 500, 390)
    pygame.draw.rect(surf, (12, 28, 68), box, border_radius=18)
    pygame.draw.rect(surf, CYAN, box, 3, border_radius=18)

    pause_t = font_big.render("PAUSED", True, CYAN)
    surf.blit(pause_t, (box.centerx - pause_t.get_width() // 2, box.top + 20))

    hint = font_small.render("Tekan P atau ESC untuk lanjut", True, GRAY)
    surf.blit(hint, (box.centerx - hint.get_width() // 2, box.top + 88))

    icon_sz = 26
    btn_data = [
        ("resume",  "play",    GREEN,  (18, 78, 32),  (30, 120, 50),  "LANJUTKAN"),
        ("restart", "restart", ORANGE, (78, 38, 10),  (120, 60, 18),  "RESTART LEVEL"),
        ("quit",    "house",   RED,    (65, 12, 12),  (100, 20, 20),  "MAIN MENU"),
    ]
    rects = {}
    for idx, (key, icon_key, border, col_n, col_h, label) in enumerate(btn_data):
        br     = pygame.Rect(box.centerx - 170, box.top + 138 + idx * 82, 340, 58)
        rects[key] = br
        is_h   = br.collidepoint(mx, my)
        pygame.draw.rect(surf, col_h if is_h else col_n, br, border_radius=12)
        pygame.draw.rect(surf, border, br, 2, border_radius=12)
        txt    = font_small.render(label, True, WHITE)
        total  = icon_sz + 8 + txt.get_width()
        ix     = br.centerx - total // 2
        icons.draw_icon(surf, icon_key, icon_sz, ix, br.centery - icon_sz // 2)
        surf.blit(txt, (ix + icon_sz + 8, br.centery - txt.get_height() // 2))

    return rects["resume"], rects["restart"], rects["quit"]

# ─── TIMER HELPERS ────────────────────────────────────────────────────────────
# Kita simpan waktu secara akumulatif:
#   elapsed_playing  = total detik yang dihabiskan dalam state PLAYING
# Cara kerjanya:
#   - Saat mulai/resume: catat session_start = time.time()
#   - Saat pause/win/gameover: elapsed_playing += time.time() - session_start
#   - elapsed yang ditampilkan = elapsed_playing (tidak ada kalkulasi on-the-fly di render)

def get_display_elapsed(elapsed_playing, session_start, state):
    """Kembalikan elapsed detik yang akurat untuk ditampilkan."""
    if state == STATE_PLAYING:
        return elapsed_playing + (time.time() - session_start)
    return elapsed_playing

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────
def main():
    global particles

    state          = STATE_MENU
    level          = 1
    menu_t         = 0
    selected_level = 1

    grid, player, guards, cctvs, bombs, cfg = setup_level(level)

    # ── Timer yang benar ──────────────────────────────────────────────────────
    elapsed_playing = 0.0   # akumulasi detik saat state == PLAYING
    session_start   = time.time()  # waktu mulai sesi PLAYING terakhir
    final_elapsed   = 0.0   # snapshot elapsed saat WIN/GAMEOVER (tidak berubah lagi)

    gameover_reason = "YOU GOT CAUGHT!"
    no_cctv_hit     = True

    # Rect tombol win disimpan setiap frame render
    _win_rects = {"next": None, "menu": None, "has_next": False}

    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── MENU ──────────────────────────────────────────────────────────
            if state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    bounce = int(math.sin(menu_t * 0.05) * 5)
                    play_r = pygame.Rect(SCREEN_W // 2 - 150, 408 + bounce, 300, 66)
                    if play_r.collidepoint(mx, my):
                        play_click_sfx()
                        level = selected_level
                        grid, player, guards, cctvs, bombs, cfg = setup_level(level)
                        elapsed_playing = 0.0
                        session_start   = time.time()
                        no_cctv_hit     = True
                        particles       = []
                        state           = STATE_PLAYING

                    btn_w   = 110
                    total_bw = 3 * btn_w + 2 * 20
                    sx      = SCREEN_W // 2 - total_bw // 2
                    for lv in [1, 2, 3]:
                        lbr = pygame.Rect(sx + (lv - 1) * (btn_w + 20), 318, btn_w, 62)
                        if lbr.collidepoint(mx, my):
                            play_click_sfx()
                            selected_level = lv

            # ── PLAYING ───────────────────────────────────────────────────────
            elif state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        # Akumulasi sebelum pause
                        elapsed_playing += time.time() - session_start
                        state = STATE_PAUSED
                    elif event.key == pygame.K_r:
                        grid, player, guards, cctvs, bombs, cfg = setup_level(level)
                        elapsed_playing = 0.0
                        session_start   = time.time()
                        no_cctv_hit     = True
                        particles       = []

            # ── PAUSE ─────────────────────────────────────────────────────────
            elif state == STATE_PAUSED:
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
                    session_start = time.time()   # reset session saat resume
                    state = STATE_PLAYING
                if event.type == pygame.MOUSEBUTTONDOWN:
                    box_top  = SCREEN_H // 2 - 195
                    box_cx   = SCREEN_W // 2
                    resume_r = pygame.Rect(box_cx - 170, box_top + 138,       340, 58)
                    restart_r= pygame.Rect(box_cx - 170, box_top + 138 + 82,  340, 58)
                    quit_r   = pygame.Rect(box_cx - 170, box_top + 138 + 164, 340, 58)
                    if resume_r.collidepoint(mx, my):
                        play_click_sfx()
                        session_start = time.time()
                        state = STATE_PLAYING
                    elif restart_r.collidepoint(mx, my):
                        play_click_sfx()
                        grid, player, guards, cctvs, bombs, cfg = setup_level(level)
                        elapsed_playing = 0.0
                        session_start   = time.time()
                        no_cctv_hit     = True
                        particles       = []
                        state           = STATE_PLAYING
                    elif quit_r.collidepoint(mx, my):
                        play_click_sfx()
                        state = STATE_MENU

            # ── GAME OVER ─────────────────────────────────────────────────────
            elif state == STATE_GAMEOVER:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    grid, player, guards, cctvs, bombs, cfg = setup_level(level)
                    elapsed_playing = 0.0
                    session_start   = time.time()
                    no_cctv_hit     = True
                    particles       = []
                    state           = STATE_PLAYING
                if event.type == pygame.MOUSEBUTTONDOWN:
                    box_bot  = SCREEN_H // 2 - 205 + 410
                    restart_r = pygame.Rect(SCREEN_W // 2 - 160, box_bot - 88, 150, 58)
                    menu_r    = pygame.Rect(SCREEN_W // 2 + 10,  box_bot - 88, 150, 58)
                    if restart_r.collidepoint(mx, my):
                        play_click_sfx()
                        grid, player, guards, cctvs, bombs, cfg = setup_level(level)
                        elapsed_playing = 0.0
                        session_start   = time.time()
                        no_cctv_hit     = True
                        particles       = []
                        state           = STATE_PLAYING
                    elif menu_r.collidepoint(mx, my):
                        play_click_sfx() 
                        state = STATE_MENU

            # ── WIN ───────────────────────────────────────────────────────────
            elif state == STATE_WIN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if _win_rects["has_next"] and _win_rects["next"] and \
                       _win_rects["next"].collidepoint(mx, my):
                        play_click_sfx()
                        level += 1
                        grid, player, guards, cctvs, bombs, cfg = setup_level(level)
                        elapsed_playing = 0.0
                        session_start   = time.time()
                        no_cctv_hit     = True
                        particles       = []
                        state           = STATE_PLAYING
                    elif _win_rects["menu"] and _win_rects["menu"].collidepoint(mx, my):
                        play_click_sfx()  
                        state = STATE_MENU

        # ── LOGIC PLAYING ─────────────────────────────────────────────────────
        if state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]  or keys[pygame.K_a]: player.try_move(-1,  0, grid)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player.try_move( 1,  0, grid)
            if keys[pygame.K_UP]    or keys[pygame.K_w]: player.try_move( 0, -1, grid)
            if keys[pygame.K_DOWN]  or keys[pygame.K_s]: player.try_move( 0,  1, grid)
            player.update()

            # CCTV
            for cctv in cctvs:
                cctv.update()
                if player.invincible == 0 and cctv.in_view(player.gx, player.gy, grid):
                    player.lives    -= 1
                    player.invincible = 90
                    no_cctv_hit     = False
                    spawn_particles(player.px, player.py, RED, 18)
                    play_hit_sfx()          # ← SFX kena rintangan
                    if player.lives <= 0:
                        # Snapshot elapsed sebelum pindah state
                        elapsed_playing += time.time() - session_start
                        final_elapsed    = elapsed_playing
                        gameover_reason  = "KENA CCTV!"
                        play_sfx(sfx_explosion)
                        state = STATE_GAMEOVER

            # Satpam
            for guard in guards:
                guard.update(grid, player.gx, player.gy)
                if math.hypot(guard.px - player.px, guard.py - player.py) < TILE * 0.78 \
                   and player.invincible == 0:
                    player.lives    -= 2
                    player.invincible = 120
                    spawn_particles(player.px, player.py, ORANGE, 28)
                    play_hit_sfx()          # ← SFX kena satpam
                    if player.lives <= 0:
                        elapsed_playing += time.time() - session_start
                        final_elapsed    = elapsed_playing
                        gameover_reason  = "TERTANGKAP SATPAM!"
                        play_sfx(sfx_explosion)
                        state = STATE_GAMEOVER

            # Bom
            for bomb in bombs:
                if bomb.active and \
                   math.hypot(bomb.px - player.px, bomb.py - player.py) < TILE * 0.68:
                    bomb.active  = False
                    player.lives = 0
                    spawn_particles(player.px, player.py, ORANGE, 50)
                    spawn_particles(player.px, player.py, RED, 25)
                    play_sfx(sfx_explosion, 1.0)
                    elapsed_playing += time.time() - session_start
                    final_elapsed    = elapsed_playing
                    gameover_reason  = "KENA BOM!"
                    state = STATE_GAMEOVER

            # Skor
            player.score = max(player.score, calc_proximity_score(player.gx, player.gy))

            # EXIT
            if player.gx == COLS - 2 and player.gy == ROWS - 2:
                player.score    += calc_win_bonus()
                # ── Snapshot elapsed yang BENAR saat menang ──────────────────
                elapsed_playing += time.time() - session_start
                final_elapsed    = elapsed_playing
                spawn_particles(player.px, player.py, GREEN, 50)
                spawn_particles(player.px, player.py, GOLD, 35)
                play_win_sfx()              # ← SFX menang
                state = STATE_WIN

            particles = [p for p in particles if p.life > 0]
            for p in particles:
                p.update()

        # ── RENDER ────────────────────────────────────────────────────────────
        screen.fill(DARK_BLUE)

        if state == STATE_MENU:
            menu_t += 1
            draw_menu(screen, FONTS, menu_t, selected_level)

        else:
            draw_maze(screen, grid, FONTS)
            for cctv  in cctvs:     cctv.draw(screen)
            for bomb  in bombs:     bomb.draw(screen)
            for guard in guards:    guard.draw(screen)
            for p     in particles: p.draw(screen)
            player.draw(screen)

            # ── Hitung elapsed yang ditampilkan di HUD ────────────────────────
            if state == STATE_PLAYING:
                display_elapsed = elapsed_playing + (time.time() - session_start)
            else:
                # PAUSED / GAMEOVER / WIN → tampilkan waktu yang sudah di-snapshot
                display_elapsed = elapsed_playing

            draw_hud(screen, player, level, display_elapsed, FONTS, cfg["title"])

            if state == STATE_GAMEOVER:
                draw_gameover(screen, FONTS, player.score, gameover_reason)

            elif state == STATE_WIN:
                # Selalu gunakan final_elapsed (snapshot saat menang)
                nr, has_next, mr = draw_win(
                    screen, FONTS, player.score, level, final_elapsed, no_cctv_hit)
                _win_rects["next"]     = nr
                _win_rects["menu"]     = mr if has_next else nr
                _win_rects["has_next"] = has_next

            elif state == STATE_PAUSED:
                draw_pause(screen, FONTS)

        pygame.display.flip()

if __name__ == "__main__":
    main()
