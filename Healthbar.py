import pygame
class Healthbar():
    def __init__(self, x, y, health, max_health,screen):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
        self.screen = screen

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(self.screen, (255, 255, 255), (self.x-2, self.y-2, 154, 24))
        pygame.draw.rect(self.screen, (255, 0, 0), (self.x, self.y, 150, 20))
        pygame.draw.rect(self.screen, (0, 255, 0), (self.x, self.y, 150 * ratio, 20))

