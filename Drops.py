import pygame
pygame.init()
from Setting import TILESIZE
from loadimages import ammo_box,grenade_box,health_box
item_boxes = {
    "Ammo": ammo_box,
    "Grenade": grenade_box,
    "Health": health_box    
}

class Drops(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type,player):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILESIZE // 2, y + (TILESIZE - self.image.get_height()) // 2)
        self.player = player
    def update(self):
        # Check for collision with the player
        if pygame.sprite.collide_rect(self, self.player):
            self.apply_effect(self.player)
            self.kill()  # Remove the item after pickup

    def apply_effect(self):
        if self.item_type == "Ammo":
            self.player.ammo += 10  # Add 10 ammo
            if self.player.ammo > self.player.startammo:
                self.player.ammo = self.player.startammo  # Cap ammo to starting value
        elif self.item_type == "Grenade":
            self.player.grenades += 2  # Add 2 grenades
            if self.player.grenades > self.player.maxgrenades:
                self.player.grenades = self.player.maxgrenades  # Cap grenades to max value
        elif self.item_type == "Health":
            self.player.health += 25  # Add 25 health
            if self.player.health > self.player.max_health:
                self.player.health = self.player.max_health  # Cap health to max value
