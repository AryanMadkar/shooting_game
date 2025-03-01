from Player import Soldier

class Enemy(Soldier):
    def __init__(self, x, y, scale, speed, ammo, granades):
        super().__init__("enemy", x, y, scale, speed, ammo, granades)