import pygame
from Setting import screen, clock, FPS, draw_bg, draw_text, bullet_img, grenade_img
from Player import Soldier
from enemy import Enemy
from items import Drops
from Bullets import Bullets
from Granade import Grenade
from explosion import Explosion

# Create player and enemy
player = Soldier("player", 200, 400, 3, 6, 20, 5)
enemy = Enemy(400, 600, 3, 6, 20, 0)
enemy2 = Enemy(600, 600, 3, 6, 20, 0)
enemy_group = pygame.sprite.Group()
enemy_group.add(enemy)
enemy_group.add(enemy2)

# Create drop items
ammo_drop = Drops(400, 600, "Ammo")
health_drop = Drops(500, 600, "Health")
grenade_drop = Drops(600, 600, "Grenade")
item_box_group = pygame.sprite.Group()
item_box_group.add(ammo_drop, health_drop, grenade_drop)

# Sprite groups
bullets_group = pygame.sprite.Group()
granade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

# Game loop
run = True
while run:
    clock.tick(FPS)

    # Drawing
    draw_bg()
    draw_text(f"AMMO:", font, (255, 255, 255), 10, 10)
    for x in range(player.ammo):
        screen.blit(bullet_img, (120 + (x * 20), 20))
    draw_text(f"GRANADES: ", font, (255, 255, 255), 10, 50)
    for x in range(player.granades):
        screen.blit(grenade_img, (190 + (x * 20), 55))
    draw_text(f"Health: ", font, (255, 255, 255), 10, 90)
    health_bar.draw(player.health)
    player.update()
    player.draw()
    item_box_group.update()
    item_box_group.draw(screen)
        
    for enemy in enemy_group:
        enemy.update()
        enemy.draw()

    bullets_group.update()
    bullets_group.draw(screen)
    granade_group.update()
    granade_group.draw(screen)
    explosion_group.update()
    explosion_group.draw(screen)

    if player.aliveplayer:
        if granade and player.granades > 0:
            player.granades -= 1
            grenade = Grenade(player.rect.centerx + (0.6 * player.rect.size[0] * player.direction), player.rect.centery, player.direction)
            granade_group.add(grenade)
            granade = False

        if player.insair:
            player.update_action(2)
        elif moving_left or moving_right:
            player.update_action(1)
        else:
            player.update_action(0)

        player.move(moving_left, moving_right, jump)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_SPACE and player.shoot_undecooldown == 0:
                player.shoot()
            if event.key == pygame.K_w and player.aliveplayer:
                jump = True
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_q:
                granade = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w and player.aliveplayer:
                jump = False
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_q:
                granade = False

    pygame.display.update()

pygame.quit()