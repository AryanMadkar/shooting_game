import pygame 
pygame.init()

bullet_img = pygame.image.load("game/Shooter/img/icons/bullet.png").convert_alpha()
from Player import player, enemy, SCREEN_WIDTH

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
        if self.shooter == "player" and pygame.sprite.collide_rect(self, enemy) and enemy.aliveplayer:
            enemy.health -= 25  # Reduce enemy health
            print(f"Enemy health: {enemy.health}")  # Print enemy health for debugging
            self.kill()  # Remove the bullet

bullets_group = pygame.sprite.Group()
