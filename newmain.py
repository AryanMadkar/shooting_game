import pygame
from Player import SCREEN_WIDTH, SCREEN_HEIGHT,Soldier
from Bullets import Bullets, bullets_group
from Granade import Grenade, granade_group

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter")
clock = pygame.time.Clock()
FPS = 60
# Movement flags
moving_left = False
moving_right = False
jump = False
granade = False

def drawbg():
    screen.fill((0, 0, 0))
    
player = Soldier("player", 200, 400, 3, 6, 20,5,screen)
enemy = Soldier("enemy", 400, 500, 3, 6, 20,0,screen)


# Game loop
run = True
while run:
    clock.tick(FPS)

    # Drawing
    drawbg()
    player.update()
    enemy.update()
    player.draw()
    enemy.draw()

    bullets_group.update()
    bullets_group.draw(screen)
    granade_group.update()
    granade_group.draw(screen)

    if player.aliveplayer:
        if granade and player.granades > 0:
            player.granades -= 1
            grenade = Grenade(player.rect.centerx + (0.6 * player.rect.size[0] * player.direction), player.rect.centery, player.direction)
            granade_group.add(grenade)
            granade = False  # Reset the flag

        # Switch to jump animation if in air
        if player.insair:
            player.update_action(2)  # Jump animation
        elif moving_left or moving_right:
            player.update_action(1)  # Running animation
        else:
            player.update_action(0)  # Idle animation

        player.move(moving_left, moving_right, jump)

    # Event handling
    for event in pygame.event.get():
        # Quit event
        if event.type == pygame.QUIT:
            run = False
        # Key press
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
        # Key release
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