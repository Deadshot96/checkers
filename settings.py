import os

WIDTH = 700
HEIGHT = 700
GAMEWIDTH = WIDTH - 100
GAMEHEIGHT = HEIGHT - 100
NROW, NCOL = 8, 8
PADDING = 15
SIZE = GAMEWIDTH // NROW
RADIUS = SIZE // 2 - PADDING
CROWN_PATH = os.path.join(os.getcwd(), r'assets_checkers/crown.png')
