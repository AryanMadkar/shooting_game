import pygame

# Initialize pygame
pygame.init()

# Screen setup
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter")

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Movement flags
moving_left = False
moving_right = False
jump = False
granade = False

# Load images
bullet_img = pygame.image.load("assets/img/icons/bullet.png").convert_alpha()
grenade_img = pygame.image.load("assets/img/icons/grenade.png").convert_alpha()
ammo_box = pygame.image.load("assets/img/icons/ammo_box.png").convert_alpha()
grenade_box = pygame.image.load("assets/img/icons/grenade_box.png").convert_alpha()
health_box = pygame.image.load("assets/img/icons/health_box.png").convert_alpha()

item_boxes = {
    "Ammo": ammo_box,
    "Grenade": grenade_box,
    "Health": health_box    
}

TILESIZE = 50
font = pygame.font.SysFont("Futura", 40)

def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

# Background function
def draw_bg():
    screen.fill((0, 0, 0))