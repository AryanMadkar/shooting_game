import pygame
from Setting import SCREEN_HEIGHT,SCREEN_WIDTH,TILETYPES,TILESIZE
pygame.init()

pine1 = pygame.image.load(r"game\Shooter\img\background\pine1.png")

pine2 = pygame.image.load(r"game\Shooter\img\background\pine2.png")

mountain = pygame.image.load(r"game\Shooter\img\background\mountain.png")
# mountain = pygame.transform.scale(mountain,(SCREEN_WIDTH,SCREEN_HEIGHT))

cloud = pygame.image.load(r"game\Shooter\img\background\cloud.png")
cloud = pygame.transform.scale(cloud,(SCREEN_WIDTH,SCREEN_HEIGHT))

skyimage = pygame.image.load(r"game\Shooter\img\background\sky.png")
skyimage = pygame.transform.scale(skyimage,(SCREEN_WIDTH,SCREEN_HEIGHT))

bullet_img = pygame.image.load(r"game/Shooter/img/icons/bullet.png")
grenade_img = pygame.image.load(r"game/Shooter/img/icons/grenade.png")
ammo_box = pygame.image.load(r"game/Shooter/img/icons/ammo_box.png")
grenade_box = pygame.image.load(r"game/Shooter/img/icons/grenade_box.png")
health_box = pygame.image.load(r"game/Shooter/img/icons/health_box.png")


image_list = []
for x in range(TILETYPES):
    img = pygame.image.load(f"game/Shooter/img/tile/{x}.png")
    img = pygame.transform.scale(img,(TILESIZE,TILESIZE))
    image_list.append(img)
