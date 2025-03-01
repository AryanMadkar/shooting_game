import pygame
from Setting import SCREEN_HEIGHT, SCREEN_WIDTH, TILESIZE,grenade_img


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
        if self.vel_y > 10:
            self.vel_y = 10

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
            if self.rect.centerx - player.rect.centerx < TILESIZE * 2 and self.rect.centerx - player.rect.centerx > -100:
                player.health -= 30
            for enemy in enemy_group:
                if self.rect.centerx - enemy.rect.centerx < TILESIZE * 2 and self.rect.centerx - enemy.rect.centerx > -100:
                    enemy.health -= 50