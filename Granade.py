import pygame 
pygame.init()

grenade_img = pygame.image.load("game/Shooter/img/icons/grenade.png").convert_alpha()
from Player import player, enemy, SCREEN_WIDTH, SCREEN_HEIGHT
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

    def update(self):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 10:  # Terminal velocity
            self.vel_y = 10

        # Update position
        self.rect.x += self.direction * self.speed
        self.rect.y += self.vel_y

        # Remove grenade if it goes off-screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom > SCREEN_HEIGHT:
            self.kill()

        # Check for collision with player or enemy
        if pygame.sprite.collide_rect(self, player) and player.aliveplayer:
            player.health -= 20  # Reduce player health
            self.kill()  # Remove the grenade

        if pygame.sprite.collide_rect(self, enemy) and enemy.aliveplayer:
            enemy.health -= 50  # Reduce enemy health
            print(f"Enemy health: {enemy.health}")  # Print enemy health for debugging
            self.kill()  # Remove the grenade

granade_group = pygame.sprite.Group()
