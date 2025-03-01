import pygame

# Constants
TILESIZE = 50

# Load images
ammo_box = pygame.image.load(r"game/Shooter/img/icons/ammo_box.png")
grenade_box = pygame.image.load(r"game/Shooter/img/icons/grenade_box.png")
health_box = pygame.image.load(r"game/Shooter/img/icons/health_box.png")

# Item dictionary
item_boxes = {
    "Ammo": ammo_box,
    "Grenade": grenade_box,
    "Health": health_box    
}

class Drops(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.item_type = item_type
        self.image = item_boxes.get(self.item_type)  # Safer way to get item
        if self.image is None:
            raise ValueError(f"Invalid item type: {self.item_type}")

        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILESIZE // 2, y + (TILESIZE - self.image.get_height()) // 2)

    def update(self, players):  # Pass a list of players
        for player in players:
            if pygame.sprite.collide_rect(self, player):
                self.apply_effect(player)
                self.kill()  # Remove the item after pickup
                break  # Avoid applying to multiple players at once

    def apply_effect(self, player):
        effects = {
            "Ammo": ("ammo", 10, "startammo"),
            "Grenade": ("granades", 2, "maxgranades"),
            "Health": ("health", 25, "max_health"),
        }
        
        if self.item_type in effects:
            attr, value, max_attr = effects[self.item_type]
            current_value = getattr(player, attr, 0)
            max_value = getattr(player, max_attr, current_value)  # Default max to current if missing
            setattr(player, attr, min(current_value + value, max_value))
