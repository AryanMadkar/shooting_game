import pygame
import os
import random 
import csv
pygame.init()

# Screen setup
SCREEN_WIDTH = 1366 
BG_SCROLL = 0  # Define BG_SCROLL as a global variable
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter")

clock = pygame.time.Clock()
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

image_list = []
for x in range(TILETYPES):
    img = pygame.image.load(f"game/Shooter/img/tile/{x}.png").convert_alpha()
    img = pygame.transform.scale(img,(TILESIZE,TILESIZE))
    image_list.append(img)

# Load images

pine1 = pygame.image.load(r"game\Shooter\img\background\pine1.png").convert_alpha()

pine2 = pygame.image.load(r"game\Shooter\img\background\pine2.png").convert_alpha()

mountain = pygame.image.load(r"game\Shooter\img\background\mountain.png").convert_alpha()
# mountain = pygame.transform.scale(mountain,(SCREEN_WIDTH,SCREEN_HEIGHT))

cloud = pygame.image.load(r"game\Shooter\img\background\sky_cloud.png").convert_alpha()
cloud = pygame.transform.scale(cloud,(SCREEN_WIDTH,SCREEN_HEIGHT))

skyimage = pygame.image.load(r"game\Shooter\img\background\sky.png").convert_alpha()
skyimage = pygame.transform.scale(skyimage,(SCREEN_WIDTH,SCREEN_HEIGHT))

bullet_img = pygame.image.load("game/Shooter/img/icons/bullet.png").convert_alpha()
grenade_img = pygame.image.load("game/Shooter/img/icons/grenade.png").convert_alpha()
ammo_box = pygame.image.load("game/Shooter/img/icons/ammo_box.png").convert_alpha()
grenade_box = pygame.image.load("game/Shooter/img/icons/grenade_box.png").convert_alpha()
health_box = pygame.image.load("game/Shooter/img/icons/health_box.png").convert_alpha()
item_boxes = {
    "Ammo": ammo_box,
    "Grenade": grenade_box,
    "Health": health_box    
}
font = pygame.font.SysFont("Futura", 40)
def draw_text(text,font,text_color,x,y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))
   
# Background function
def drawbg():
    screen.fill((0, 0, 0))
    screen.blit(skyimage, (0 - BG_SCROLL * 0.5, 0))
    screen.blit(mountain, (0 - BG_SCROLL * 0.6, SCREEN_HEIGHT-mountain.get_height()-300))
    screen.blit(pine1, (0 - BG_SCROLL * 0.7, SCREEN_HEIGHT-pine1.get_height()-150))
    screen.blit(pine2, (0 - BG_SCROLL * 0.8, SCREEN_HEIGHT-pine2.get_height()))

# Drop class
class Drops(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.item_type = item_type
        self.image = item_boxes[item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILESIZE // 2, y + (TILESIZE - self.image.get_height()) // 2)

    def update(self):
        if pygame.sprite.collide_rect(self, player):
            self.apply_effect(player)
            self.kill()

    def apply_effect(self, player):
        if self.item_type == "Ammo":
            player.ammo = min(player.ammo + 10, player.startammo)
        elif self.item_type == "Grenade":
            player.grenades = min(player.grenades + 2, player.maxgrenades)
        elif self.item_type == "Health":
            player.health = min(player.health + 25, player.max_health)
# Grenade class


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.gravity = 0.75
        self.bounce_factor = 0.6

    def update(self):
        self.vel_y += self.gravity
        self.vel_y = min(self.vel_y, 10)
        self.rect.x += self.direction * self.speed
        self.rect.y += self.vel_y

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                if self.direction > 0:
                    self.rect.right = tile[1].left
                    self.direction *= -1
                elif self.direction < 0:
                    self.rect.left = tile[1].right
                    self.direction *= -1
                if self.vel_y > 0:
                    self.rect.bottom = tile[1].top
                    self.vel_y = -self.vel_y * self.bounce_factor
                elif self.vel_y < 0:
                    self.rect.top = tile[1].bottom
                    self.vel_y = 0

        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.direction *= -1

        if abs(self.vel_y) < 2 and self.rect.bottom >= SCREEN_HEIGHT - 10:
            self.vel_y = 0
            self.speed = 0

        if pygame.sprite.collide_rect(self, player) and player.aliveplayer:
            player.health -= 20
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 2)
            explosion_group.add(explosion)

        for enemy in enemy_group:
            if pygame.sprite.collide_rect(self, enemy) and enemy.aliveplayer:
                enemy.health -= 50
                self.kill()
                explosion = Explosion(self.rect.x, self.rect.y, 2)
                explosion_group.add(explosion)

        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 2)
            explosion_group.add(explosion)
            if abs(self.rect.centerx - player.rect.centerx) < TILESIZE * 2:
                player.health -= 30
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILESIZE * 2:
                    enemy.health -= 50
                    
enemy_group = pygame.sprite.Group()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        super().__init__()
        self.images = [pygame.transform.scale(pygame.image.load(f"game/Shooter/img/explosion/exp{num}.png").convert_alpha(), 
                        (int(img.get_width() * scale), int(img.get_height() * scale))) for num in range(1, 6)]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]
                
explosion_group = pygame.sprite.Group()

# Bullets class
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, shooter):
        super().__init__()
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.shooter = shooter

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        if self.shooter == "enemy" and pygame.sprite.collide_rect(self, player) and player.aliveplayer:
            player.health -= 5
            self.kill()

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        if self.shooter == "player":
            for enemy in enemy_group:
                if pygame.sprite.collide_rect(self, enemy) and enemy.aliveplayer:
                    enemy.health -= 25
                    self.kill()
# Sprite groups
bullets_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

class Healthbar:
    def __init__(self, x, y, health, max_health, screen):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
        self.screen = screen

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(self.screen, (255, 255, 255), (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(self.screen, (255, 0, 0), (self.x, self.y, 150, 20))
        pygame.draw.rect(self.screen, (0, 255, 0), (self.x, self.y, 150 * ratio, 20))

# Soldier class
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        super().__init__()
        self.char_type = char_type
        self.aliveplayer = True
        self.animation_list = []
        self.index = 0
        self.grenades = grenades
        self.idealing = False
        self.idling_counter = 0
        self.maxgrenades = grenades
        self.health = 100
        self.vision = pygame.Rect(0, 0, 250, 20)
        self.max_health = self.health
        self.ammo = ammo
        self.startammo = ammo
        self.insair = False
        self.action = 0
        self.shoot_undecooldown = 0
        self.update_time = pygame.time.get_ticks()
        self.speed = speed
        self.direction = 1
        self.flip = False
        self.vel_y = 0
        self.gravity = 0.75
        self.move_counter = 0

        animation_types = ["Idle", "Run", "Jump", "Death"]
        for animation in animation_types:
            frame_list = []
            num_frames = len(os.listdir(f"game/Shooter/img/{self.char_type}/{animation}"))
            for i in range(num_frames):
                img = pygame.image.load(f"game/Shooter/img/{self.char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                frame_list.append(img)
            self.animation_list.append(frame_list)

        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        if self.shoot_undecooldown > 0:
            self.shoot_undecooldown -= 1
        self.check_alive()

    def move(self, moving_left, moving_right, jump):
        global BG_SCROLL  # Declare BG_SCROLL as global

        screen_scroll = 0
        dx = 0
        dy = 0

        if moving_left:
            dx -= self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx += self.speed
            self.flip = False
            self.direction = 1

        if jump and not self.insair:
            self.vel_y = -12
            self.insair = True

        self.vel_y += self.gravity
        self.vel_y = min(self.vel_y, 10)
        dy += self.vel_y

        self.insair = True

        self.rect.x += dx
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                if dx > 0:
                    self.rect.right = tile[1].left
                elif dx < 0:
                    self.rect.left = tile[1].right
                dx = 0

        self.rect.y += dy
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                if self.vel_y > 0:
                    self.rect.bottom = tile[1].top
                    self.vel_y = 0
                    self.insair = False
                elif self.vel_y < 0:
                    self.rect.top = tile[1].bottom
                    self.vel_y = 0

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
            self.insair = False

        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - THRESHOLD and BG_SCROLL < (world.level_length * TILESIZE) - SCREEN_WIDTH) \
                    or (self.rect.left < THRESHOLD and BG_SCROLL > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
                BG_SCROLL += screen_scroll

        return screen_scroll

    def shoot(self):
        if self.shoot_undecooldown == 0 and self.ammo > 0:
            self.shoot_undecooldown = 20
            bullet = Bullets(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, self.char_type)
            bullets_group.add(bullet)
            self.ammo -= 1

    def ai(self):
        if self.aliveplayer:
            self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

            if not self.idealing and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idealing = True
                self.idling_counter = 50

            if self.vision.colliderect(player.rect) and player.aliveplayer:
                if player.rect.centerx < self.rect.centerx:
                    self.direction = -1
                    self.flip = True
                else:
                    self.direction = 1
                    self.flip = False

                if self.shoot_undecooldown == 0:
                    self.update_action(0)
                    self.shoot()
                    self.shoot_undecooldown = 20

                self.move_counter = 0
            else:
                if not self.idealing:
                    ai_moving_right = self.direction == 1
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right, False)
                    self.update_action(1)

                    self.move_counter += 1

                    if self.move_counter > TILESIZE:
                        self.direction *= -1
                        self.move_counter = 0

        if self.idealing:
            self.idling_counter -= 1
            if self.idling_counter <= 0:
                self.idealing = False

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.index]

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.index += 1

        if self.index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.index = len(self.animation_list[self.action]) - 1
            else:
                self.index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.aliveplayer = False
            self.health = 0
            self.speed = 0
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - BG_SCROLL, self.rect.y))
class World:
    def __init__(self):
        self.obstacle_list = []  # Fixed typo: opsticle_list -> obstacle_list

    def process_data(self, data):
        player = None
        health_bar = None
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = image_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILESIZE
                    img_rect.y = y * TILESIZE
                    tile_data = (img, img_rect)
                    if 0 <= tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif 9 <= tile <= 10:
                        water = Water(img, x * TILESIZE, y * TILESIZE)
                        water_group.add(water)
                    elif 11 <= tile <= 14:
                        decoration = Decoration(img, x * TILESIZE, y * TILESIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:  # Player
                        player = Soldier("player", x * TILESIZE, y * TILESIZE, 2, 5, 20, 5)
                        health_bar = Healthbar(120, 95, player.health, player.max_health, screen)
                    elif tile == 16:  # Enemy
                        enemy = Soldier("enemy", x * TILESIZE, y * TILESIZE, 2, 2, 20, 0)
                        enemy_group.add(enemy)  # Removed duplicate addition
                    elif tile == 17:  # Ammo drop
                        ammo_drop = Drops(x * TILESIZE, y * TILESIZE, "Ammo")
                        item_box_group.add(ammo_drop)
                    elif tile == 18:  # Grenade drop
                        grenade_drop = Drops(x * TILESIZE, y * TILESIZE, "Grenade")
                        item_box_group.add(grenade_drop)
                    elif tile == 19:  # Health drop
                        health_drop = Drops(x * TILESIZE, y * TILESIZE, "Health")
                        item_box_group.add(health_drop)
                    elif tile == 20:  # Exit door
                        exit_door = Exit(img, x * TILESIZE, y * TILESIZE)
                        exit_group.add(exit_door)
        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            screen.blit(tile[0], (tile[1].x - BG_SCROLL, tile[1].y))


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILESIZE // 2, y + (TILESIZE - self.image.get_height()))


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILESIZE // 2, y + (TILESIZE - self.image.get_height()))


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILESIZE // 2, y + (TILESIZE - self.image.get_height()))


# Create tile list
WORLD_DATA = [[-1 for _ in range(COLS)] for _ in range(ROWS)]  # Simplified initialization
with open(f"game/Shooter/level{level}_data.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            WORLD_DATA[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(WORLD_DATA)

# Game loop
run = True
while run:
    clock.tick(FPS)

    # Draw background
    drawbg()
    world.draw()

    # Draw all sprites with BG_SCROLL adjustment
    for bullet in bullets_group:
        screen.blit(bullet.image, (bullet.rect.x - BG_SCROLL, bullet.rect.y))
    for grenade in grenade_group:
        screen.blit(grenade.image, (grenade.rect.x - BG_SCROLL, grenade.rect.y))
    for explosion in explosion_group:
        screen.blit(explosion.image, (explosion.rect.x - BG_SCROLL, explosion.rect.y))
    for item in item_box_group:
        screen.blit(item.image, (item.rect.x - BG_SCROLL, item.rect.y))
    for sprite in decoration_group:
        screen.blit(sprite.image, (sprite.rect.x - BG_SCROLL, sprite.rect.y))
    for sprite in water_group:
        screen.blit(sprite.image, (sprite.rect.x - BG_SCROLL, sprite.rect.y))
    for sprite in exit_group:
        screen.blit(sprite.image, (sprite.rect.x - BG_SCROLL, sprite.rect.y))

    # Show ammo
    draw_text(f"AMMO:", font, (255, 255, 255), 10, 10)
    for x in range(player.ammo):
        screen.blit(bullet_img, (120 + (x * 20), 20))

    # Show grenades
    draw_text(f"GRENADES:", font, (255, 255, 255), 10, 50)
    for x in range(player.grenades):
        screen.blit(grenade_img, (190 + (x * 20), 55))

    # Show health
    draw_text(f"HEALTH:", font, (255, 255, 255), 10, 90)
    health_bar.draw(player.health)

    # Update and draw player
    player.update()
    player.draw()

    # Update and draw item boxes
    item_box_group.update()
    item_box_group.draw(screen)

    # Update and draw enemies
    for enemy in enemy_group:
        if player.aliveplayer:  # Only run AI if player is alive
            enemy.ai()
        enemy.update()
        enemy.draw()

    # Update and draw bullets, grenades, and explosions
    bullets_group.update()
    bullets_group.draw(screen)
    grenade_group.update()
    grenade_group.draw(screen)
    explosion_group.update()
    explosion_group.draw(screen)

    # Update and draw decorations, water, and exit
    decoration_group.update()
    water_group.update()
    exit_group.update()
    decoration_group.draw(screen)
    water_group.draw(screen)
    exit_group.draw(screen)

    # Handle player actions
    if player.aliveplayer:

        # Switch to jump animation if in air
        if player.insair:
            player.update_action(2)  # Jump animation
        elif moving_left or moving_right:
            player.update_action(1)  # Running animation
        else:
            player.update_action(0)  # Idle animation

        screenscroll = player.move(moving_left, moving_right, jump)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_SPACE and player.shoot_undecooldown == 0 and player.aliveplayer:
                player.shoot()
            if event.key == pygame.K_w and player.aliveplayer:
                jump = True
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_q and player.grenades>0:
                player.grenades -= 1
                grenade = Grenade(player.rect.centerx + (0.6 * player.rect.size[0] * player.direction),
                              player.rect.centery, player.direction)
                grenade_group.add(grenade)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w and player.aliveplayer:
                jump = False
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_q:
                grenade = False

    pygame.display.update()

pygame.quit()