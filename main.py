import pygame
import os

pygame.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
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
TILESIZE = 50

# Background function
def drawbg():
    screen.fill((0, 0, 0))

# Grenade class
class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11  # Initial upward velocity
        self.speed = 7  # Horizontal speed
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.gravity = 0.75  # Gravity for the grenade
        self.bounce_factor = 0.6  # Energy loss per bounce

    def update(self):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 10:  # Terminal velocity
            self.vel_y = 10

        # Update position
        self.rect.x += self.direction * self.speed
        self.rect.y += self.vel_y

        # Bounce off the ground
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT  # Ensure it stays on the screen
            self.vel_y = -self.vel_y * self.bounce_factor  # Reverse velocity with energy loss
            
            # Stop bouncing when velocity is too low
            if abs(self.vel_y) < 2:
                self.vel_y = 0
                self.speed = 0  # Stop moving horizontally too

        # Bounce off the sides
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.direction *= -1  # Reverse horizontal direction

        # Check for collision with player or enemy
        if pygame.sprite.collide_rect(self, player) and player.aliveplayer:
            player.health -= 20  # Reduce player health
            self.kill()  # Remove the grenade
            explosion = Explosion(self.rect.x, self.rect.y, 2)
            explosion_group.add(explosion)

        for enemy in enemy_group:
            if pygame.sprite.collide_rect(self, enemy) and enemy.aliveplayer:
                enemy.health -= 50  # Reduce enemy health
                print(f"Enemy health: {enemy.health}")  # Debugging
                self.kill()  # Remove the grenade
                explosion = Explosion(self.rect.x, self.rect.y, 2)
                explosion_group.add(explosion)
        
        # Countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 2)
            explosion_group.add(explosion)
            if self.rect.centerx - player.rect.centerx < TILESIZE * 2 and self.rect.centerx - player.rect.centerx > -100:
                player.health -= 30
            for enemy in enemy_group:
                if self.rect.centerx - enemy.rect.centerx < TILESIZE * 2 and self.rect.centerx - enemy.rect.centerx > -100:
                    enemy.health -= 50
                
enemy_group = pygame.sprite.Group()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y,scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"game/Shooter/img/explosion/exp{num}.png").convert_alpha()
            img = pygame.transform.scale(img,(img.get_width() * scale, img.get_height() * scale))
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
        
        
        
explosion_group = pygame.sprite.Group()

# Bullets class
class Bullets(pygame.sprite.Sprite):
    
    def __init__(self, x, y, direction, shooter):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.shooter = shooter  # Track who fired the bullet

    def update(self):
        self.rect.x += (self.direction * self.speed)
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # Check for collision with the player (if fired by enemy)
        if self.shooter == "enemy" and pygame.sprite.collide_rect(self, player) and player.aliveplayer:
            player.health -= 5  # Reduce player health
            self.kill()  # Remove the bullet

        # Check for collision with the enemy (if fired by player)
        if self.shooter == "player":
            for enemy in enemy_group:
                if pygame.sprite.collide_rect(self, enemy) and enemy.aliveplayer:
                    enemy.health -= 25  # Reduce enemy health
                    print(f"Enemy health: {enemy.health}")  # Print enemy health for debugging
                    self.kill()  # Remove the bullet

# Sprite groups
bullets_group = pygame.sprite.Group()
granade_group = pygame.sprite.Group()

# Soldier class
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo,granades):
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

        # Load animations
        animation_types = ["Idle", "Run", "Jump", "Death"]
        for animation in animation_types:
            frame_list = []
            num_frames = len(os.listdir(f"game/Shooter/img/{self.char_type}/{animation}"))
            for i in range(num_frames):
                img = pygame.image.load(f"game/Shooter/img/{self.char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                frame_list.append(img)
            self.animation_list.append(frame_list)

        # Set initial image
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

        # Movement left/right
        if moving_left:
            dx -= self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx += self.speed
            self.flip = False
            self.direction = 1

        # Wall collision (prevents moving off the screen)
        if self.rect.left + dx < 0:  # Left boundary
            dx = -self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:  # Right boundary
            dx = SCREEN_WIDTH - self.rect.right

        # Jumping
        if jump and not self.insair:  # Only allow jumping if not already in air
            self.vel_y = -12  # Jump force
            self.insair = True

        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 10:  # Terminal velocity
            self.vel_y = 10
        dy += self.vel_y

        # Prevent falling below ground
        if self.rect.bottom + dy >= SCREEN_HEIGHT:
            dy = SCREEN_HEIGHT - self.rect.bottom
            self.vel_y = 0
            self.insair = False  # Reset air state

        # Update position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_undecooldown == 0 and self.ammo > 0:
            self.shoot_undecooldown = 20
            bullet = Bullets(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, self.char_type)
            bullets_group.add(bullet)
            self.ammo -= 1
              

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.index]

        # Update animation frame
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.index += 1

        # Reset animation if end reached
        if self.index >= len(self.animation_list[self.action]):
            if self.action == 3:  # Death animation
                self.index = len(self.animation_list[self.action]) - 1  # Freeze on the last frame
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

# Create player and enemy
player = Soldier("player", 200, 400, 3, 6, 20,5)
enemy = Soldier("enemy", 400, 500, 3, 6, 20,0)
enemy_group.add(enemy)

# Game loop
run = True
while run:
    clock.tick(FPS)

    # Drawing
    drawbg()
    player.update()
    enemy.update()
    player.draw()
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
            grenade = Grenade(player.rect.centerx + (0.6 * player.rect.size[0] * player.direction), player.rect.centery, player.direction)
            granade_group.add(grenade)
            granade = False  # Reset the flag

        # Switch to jump animation if in air
        if player.insair:
            player.update_action(2)  # Jump animation
        elif moving_left or moving_right:
            player.update_action(1)  # Running animation
        else:
            player.update_action(0)  # Idle animation

        player.move(moving_left, moving_right, jump)

    # Event handling
    for event in pygame.event.get():
        # Quit event
        if event.type == pygame.QUIT:
            run = False
        # Key press
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
        # Key release
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w and player.aliveplayer:
                jump = False
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_q:
                granade = False

    pygame.display.update()

pygame.quit()