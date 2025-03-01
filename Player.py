import pygame 
from Bullets import Bullets, bullets_group
from Granade import Grenade,granade_group
import os
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo,granades,screen):
        pygame.sprite.Sprite.__init__(self)
        self.screen =screen
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
    def shootgranade(self):
        if self.shoot_undecooldown == 0 and self.granades > 0:
            self.shoot_undecooldown = 100
            granade = Grenade(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            granade_group.add(granade)
            self.granades -= 1

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
        self.screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
