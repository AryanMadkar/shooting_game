import pygame
from Setting import SCREEN_WIDTH

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