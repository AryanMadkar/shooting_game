import pygame
# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH*0.8)
FPS = 60
level = "1"
THRESHOLD = 200
SCREEN_SCROLL = 0
BG_SCROLL =0
ROWS = 16
COLS = 150
TILESIZE = SCREEN_HEIGHT//ROWS
TILETYPES =21


# Movement flags
moving_left = False
moving_right = False
jump = False
grenade = False
