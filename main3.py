import pygame
import os

pygame.init()

# Screen setup
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter")

clock = pygame.time.Clock()
FPS = 60

# Movement flags
moving_left = False
moving_right = False
jump = False
granade = False

# Load images
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
TILESIZE = 50
font = pygame.font.SysFont("Futura", 40)

def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

def drawbg():
    screen.fill((0, 0, 0))

class Drops(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
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
            player.granades = min(player.granades + 2, player.maxgranades)
        elif self.item_type == "Health":
            player.health = min(player.health + 25, player.max_health)

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
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

        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = -self.vel_y * self.bounce_factor
            if abs(self.vel_y) < 2:
                self.vel_y = 0
                self.speed = 0

        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.direction *= -1

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

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"game/Shooter/img/explosion/exp{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
            self.images.append(img)
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

class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, shooter):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.shooter = shooter

    def update(self):
        self.rect.x += (self.direction * self.speed)
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        if self.shooter == "enemy" and pygame.sprite.collide_rect(self, player) and player.aliveplayer:
            player.health -= 5
            self.kill()

        if self.shooter == "player":
            for enemy in enemy_group:
                if pygame.sprite.collide_rect(self, enemy) and enemy.aliveplayer:
                    enemy.health -= 25
                    self.kill()

class Healthbar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, (255, 255, 255), (self.x-2, self.y-2, 154, 24))
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, 150 * ratio, 20))

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, granades):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.aliveplayer = True
        self.animation_list = []
        self.index = 0
        self.granades = granades
        self.maxgranades = granades
        self.health = 100
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

        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right

        if jump and not self.insair:
            self.vel_y = -12
            self.insair = True

        self.vel_y += self.gravity
        self.vel_y = min(self.vel_y, 10)
        dy += self.vel_y

        if self.rect.bottom + dy >= SCREEN_HEIGHT:
            dy = SCREEN_HEIGHT - self.rect.bottom
            self.vel_y = 0
            self.insair = False

        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_undecooldown == 0 and self.ammo > 0:
            self.shoot_undecooldown = 20
            bullet = Bullets(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, self.char_type)
            bullets_group.add(bullet)
            self.ammo -= 1

    def ai(self):
        if self.aliveplayer and player.aliveplayer:
            ai_moving_right = self.direction == 1
            self.move(ai_moving_right=False, moving_left=not ai_moving_right, jump=False)
            self.update_action(1)
            self.move_counter += 1
            
            if abs(self.move_counter) > TILESIZE:
                self.direction *= -1
                self.move_counter = 0

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
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

# Initialize game objects
player = Soldier("player", 200, 400, 3, 6, 20, 5)
health_bar = Healthbar(120, 95, player.health, player.max_health)
enemy_group = pygame.sprite.Group()
enemy = Soldier("enemy", 400, 710, 3, 6, 20, 0)
enemy2 = Soldier("enemy", 800, 710, 3, 6, 20, 0)
enemy_group.add(enemy, enemy2)

item_box_group = pygame.sprite.Group()
ammo_drop = Drops(400, 600, "Ammo")
health_drop = Drops(500, 600, "Health")
grenade_drop = Drops(600, 600, "Grenade")
item_box_group.add(ammo_drop, health_drop, grenade_drop)

bullets_group = pygame.sprite.Group()
granade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

# Game loop
run = True
while run:
    clock.tick(FPS)
    drawbg()

    # Draw UI elements
    draw_text(f"AMMO:", font, (255, 255, 255), 10, 10)
    for x in range(player.ammo):
        screen.blit(bullet_img, (120 + (x * 20), 20))
    draw_text(f"GRANADES: ", font, (255, 255, 255), 10, 50)
    for x in range(player.granades):
        screen.blit(grenade_img, (190 + (x * 20), 55))
    draw_text(f"Health: ", font, (255, 255, 255), 10, 90)
    health_bar.draw(player.health)

    # Update and draw sprites
    player.update()
    player.draw()
    item_box_group.update()
    item_box_group.draw(screen)
    
    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()

    bullets_group.update()
    bullets_group.draw(screen)
    granade_group.update()
    granade_group.draw(screen)
    explosion_group.update()
    explosion_group.draw(screen)

    if player.aliveplayer:
        if granade and player.granades > 0:
            player.granades -= 1
            granade_group.add(Grenade(player.rect.centerx + (0.6 * player.rect.size[0] * player.direction), 
                                    player.rect.centery, player.direction))
            granade = False

        if player.insair:
            player.update_action(2)
        elif moving_left or moving_right:
            player.update_action(1)
        else:
            player.update_action(0)

        player.move(moving_left, moving_right, jump)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_SPACE and player.shoot_undecooldown == 0:
                player.shoot()
            if event.key == pygame.K_w and player.aliveplayer:
                jump = True
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_q:
                granade = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                jump = False
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_q:
                granade = False

    pygame.display.update()

pygame.quit()