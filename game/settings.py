''' PySpaceX, a simple game shooter made in Pygame

Inspired by the wonderful KidsCanCode videos on youtube
https://www.youtube.com/channel/UCNaPQ5uLX5iIEHUCLmfAgKg

Settings file : mainly constants
'''
import os

# PYGAME settings
# Frame per seconds
FPS = 60

# FILES
# to keep columns short enough to comply with pep8 when
# graphics are loaded, needed to create a EXPLOD_PATH constant
FILE_PATH = os.path.dirname('__file__')
IMG_PATH = os.path.join(FILE_PATH, 'img')
EXPLOD_PATH = os.path.join(IMG_PATH, 'Explosions')
SND_PATH = os.path.join(FILE_PATH, 'snd')
# FONT_NAME = pg.font.match_font('arial')

# WINDOW
WIDTH = 800
HEIGHT = 600

# GAME
LIVES = 3
SHIELD_MAX = 100
SHOTDELAY_INIT = 500
SHOTDELAY_MAX = 200
POWER_LEVEL_INIT = 1
POWER_LEVEL_TIME = 10000
TITLE = "PYSPACEX"
BONUS_ODD = 0.95
RESPAWN_TIME = 3000
BIG_STARS_SPEED = 0.4
BIG_STARS_SIZE = 2.2
MEDIUM_STARS_SPEED = 0.2
MEDIUM_STARS_SIZE = 1.1
SMALL_STARS_SPEED = 0.1
SMALL_STARS_SIZE = 0.8
