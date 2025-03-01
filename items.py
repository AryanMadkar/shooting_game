import pygame
from Setting import item_boxes, TILESIZE

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
            player.ammo += 10
            if player.ammo > player.startammo:
                player.ammo = player.startammo
        elif self.item_type == "Grenade":
            player.granades += 2
            if player.granades > player.maxgranades:
                player.granades = player.maxgranades
        elif self.item_type == "Health":
            player.health += 25
            if player.health > player.max_health:
                player.health = player.max_health