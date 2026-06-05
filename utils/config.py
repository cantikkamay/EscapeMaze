# ─── utils/config.py ─────────────────────────────────────────────────────────
# Konstanta global untuk seluruh game Escape Maze

# Layar — 1280x720
SCREEN_W  = 1280
SCREEN_H  = 720
FPS       = 60
TITLE     = "ESCAPE MAZE"

# Grid maze — disesuaikan dengan resolusi baru
TILE  = 38
COLS  = 21
ROWS  = 15
MAZE_X = (SCREEN_W - COLS * TILE) // 2
MAZE_Y = 95

# Warna
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK_BLUE  = (10,  18,  45)
BLUE       = (30,  80,  180)
CYAN       = (0,   200, 255)
GOLD       = (255, 200, 0)
RED        = (220, 50,  50)
GREEN      = (50,  200, 80)
ORANGE     = (255, 140, 0)
GRAY       = (120, 120, 140)
DARK_GRAY  = (40,  40,  55)
WALL_COLOR = (20,  50,  100)
WALL_TOP   = (25,  60,  120)
FLOOR_COLOR= (30,  35,  70)
FLOOR_DARK = (35,  40,  80)
PURPLE     = (150, 50,  200)

# State game
STATE_MENU     = "menu"
STATE_PLAYING  = "playing"
STATE_GAMEOVER = "gameover"
STATE_WIN      = "win"
STATE_PAUSE    = "pause"
STATE_PAUSED   = "pause"  
