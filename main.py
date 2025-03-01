import pygame
import os
import random 
import csv
pygame.init()

# Screen setup
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter")

clock = pygame.time.Clock()
FPS = 60
level = "1"
ROWS = 16
COLS = 150
TILESIZE = SCREEN_HEIGHT//ROWS
TILETYPES =21

# Movement flags
moving_left = False
moving_right = False
jump = False
grenade = False

image_list = []
for x in range(TILETYPES):
    img = pygame.image.load(f"game/Shooter/img/tile/{x}.png").convert_alpha()
    img = pygame.transform.scale(img,(TILESIZE,TILESIZE))
    image_list.append(img)


# Load images
bullet_img = pygame.image.load("game/Shooter/img/icons/bullet.png").convert_alpha()
grenade_img = pygame.image.load("game/Shooter/img/icons/grenade.png").convert_alpha()
ammo_box = pygame.image.load("game/Shooter/img/icons/ammo_box.png").convert_alpha()
grenade_box = pygame.image.load("game/Shooter/img/icons/grenade_box.png").convert_alpha()
health_box = pygame.image.load("game/Shooter/img/icons/health_box.png").convert_alpha()
item_boxes = {
    "Ammo": ammo_box,
    "Grenade": grenade_box,
    "Health": health_box    
}
font = pygame.font.SysFont("Futura", 40)
def draw_text(text,font,text_color,x,y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))
   
# Background function
def drawbg():
    screen.fill((0, 0, 0))

# Drop class
class Drops(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILESIZE // 2, y + (TILESIZE - self.image.get_height()) // 2)

    def update(self):
        # Check for collision with the player
        if pygame.sprite.collide_rect(self, player):
            self.apply_effect(player)
            self.kill()  # Remove the item after pickup

    def apply_effect(self, player):
        if self.item_type == "Ammo":
            player.ammo += 10  # Add 10 ammo
            if player.ammo > player.startammo:
                player.ammo = player.startammo  # Cap ammo to starting value
        elif self.item_type == "Grenade":
            player.grenades += 2  # Add 2 grenades
            if player.grenades > player.maxgrenades:
                player.grenades = player.maxgrenades  # Cap grenades to max value
        elif self.item_type == "Health":
            player.health += 25  # Add 25 health
            if player.health > player.max_health:
                player.health = player.max_health  # Cap health to max value

# Grenade class
class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11  # Initial upward velocity
        self.speed = 7  # Horizontal speed
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.gravity = 0.75  # Gravity for the grenade
        self.bounce_factor = 0.6  # Energy loss per bounce

    def update(self):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 10:  # Terminal velocity
            self.vel_y = 10

        # Update position
        self.rect.x += self.direction * self.speed
        self.rect.y += self.vel_y

        # Bounce off the ground
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT  # Ensure it stays on the screen
            self.vel_y = -self.vel_y * self.bounce_factor  # Reverse velocity with energy loss
            
            # Stop bouncing when velocity is too low
            if abs(self.vel_y) < 2:
                self.vel_y = 0
                self.speed = 0  # Stop moving horizontally too

        # Bounce off the sides
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.direction *= -1  # Reverse horizontal direction

        # Check for collision with player or enemy
        if pygame.sprite.collide_rect(self, player) and player.aliveplayer:
            player.health -= 20  # Reduce player health
            self.kill()  # Remove the grenade
            explosion = Explosion(self.rect.x, self.rect.y, 2)
            explosion_group.add(explosion)

        for enemy in enemy_group:
            if pygame.sprite.collide_rect(self, enemy) and enemy.aliveplayer:
                enemy.health -= 50  # Reduce enemy health
                self.kill()  # Remove the grenade
                explosion = Explosion(self.rect.x, self.rect.y, 2)
                explosion_group.add(explosion)
        
        # Countdown timer
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
                
enemy_group = pygame.sprite.Group()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"game/Shooter/img/explosion/exp{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
        
    def update(self):
        EXPLOSION_SPEED = 4
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]

explosion_group = pygame.sprite.Group()

# Bullets class
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, shooter):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.shooter = shooter  # Track who fired the bullet

    def update(self):
        self.rect.x += (self.direction * self.speed)
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # Check for collision with the player (if fired by enemy)
        if self.shooter == "enemy" and pygame.sprite.collide_rect(self, player) and player.aliveplayer:
            player.health -= 5  # Reduce player health
            self.kill()  # Remove the bullet

        # Check for collision with the enemy (if fired by player)
        if self.shooter == "player":
            for enemy in enemy_group:
                if pygame.sprite.collide_rect(self, enemy) and enemy.aliveplayer:
                    enemy.health -= 25  # Reduce enemy health
                    self.kill()  # Remove the bullet

# Sprite groups
bullets_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

class Healthbar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, (255, 255, 255), (self.x-2, self.y-2, 154, 24))
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, 150 * ratio, 20))


# Soldier class
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.aliveplayer = True
        self.animation_list = []
        self.index = 0
        self.grenades = grenades
        self.idealing = False
        self.idling_counter = 0
        self.maxgrenades = grenades
        self.health = 100
        self.vision = pygame.Rect(0,0,250,20)
        self.max_health = self.health
        self.ammo = ammo
        self.startammo = ammo
        self.insair = False
        self.action = 0
        self.shoot_undecooldown = 0
        self.update_time = pygame.time.get_ticks()
        self.speed = speed
        self.direction = 1
        self.flip = False
        self.vel_y = 0
        self.gravity = 0.75
        self.move_counter = 0

        # Load animations
        animation_types = ["Idle", "Run", "Jump", "Death"]
        for animation in animation_types:
            frame_list = []
            num_frames = len(os.listdir(f"game/Shooter/img/{self.char_type}/{animation}"))
            for i in range(num_frames):
                img = pygame.image.load(f"game/Shooter/img/{self.char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                frame_list.append(img)
            self.animation_list.append(frame_list)

        # Set initial image
        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        if self.shoot_undecooldown > 0:
            self.shoot_undecooldown -= 1
        self.check_alive()
        
    def move(self, moving_left, moving_right, jump):
        dx = 0
        dy = 0

        # Movement left/right
        if moving_left:
            dx -= self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx += self.speed
            self.flip = False
            self.direction = 1

        # Jumping
        if jump and not self.insair:
            self.vel_y = -12  # Jump force
            self.insair = True

        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 10:  # Terminal velocity
            self.vel_y = 10
        dy += self.vel_y

        # Check for collisions with tiles
        self.insair = True  # Assume player is in the air unless proven otherwise

        # Check collision in the x direction
        self.rect.x += dx
        for tile in world.opsticle_list:
            if tile[1].colliderect(self.rect):
                if dx > 0:  # Moving right
                    self.rect.right = tile[1].left
                elif dx < 0:  # Moving left
                    self.rect.left = tile[1].right
                dx = 0  # Stop horizontal movement after collision

        # Check collision in the y direction
        self.rect.y += dy
        for tile in world.opsticle_list:
            if tile[1].colliderect(self.rect):
                if self.vel_y > 0:  # Falling
                    self.rect.bottom = tile[1].top
                    self.vel_y = 0
                    self.insair = False  # Player is on the ground
                elif self.vel_y < 0:  # Jumping
                    self.rect.top = tile[1].bottom
                    self.vel_y = 0

        # Prevent player from moving off the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
            self.insair = False  # Player is on the ground

    
    def shoot(self):
        if self.shoot_undecooldown == 0 and self.ammo > 0:
            self.shoot_undecooldown = 20
            bullet = Bullets(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, self.char_type)
            bullets_group.add(bullet)
            self.ammo -= 1

    def ai(self):
        if self.aliveplayer:
            # Update vision rect position based on current position and direction
            self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
            
            # Random idle behavior
            if not self.idealing and random.randint(1, 200) == 1:
                self.update_action(0)  # Idle animation
                self.idealing = True
                self.idling_counter = 50

            # Player detection and combat logic
            if self.vision.colliderect(player.rect) and player.aliveplayer:
                # Face the player
                if player.rect.centerx < self.rect.centerx:
                    self.direction = -1
                    self.flip = True
                else:
                    self.direction = 1
                    self.flip = False
                
                # Continuous shooting while player is in vision
                if self.shoot_undecooldown == 0:
                    self.update_action(0)
                    self.shoot()
                    self.shoot_undecooldown = 20  # Adjust cooldown for firing rate (lower = faster)
                    
                # Stop movement while engaging player
                self.move_counter = 0
            else:
                # Regular patrol movement when not engaged
                if not self.idealing:
                    ai_moving_right = self.direction == 1
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right, False)
                    self.update_action(1)  # Walking animation

                    # Update movement counter
                    self.move_counter += 1

                    # Reverse direction at patrol boundaries
                    if self.move_counter > TILESIZE:
                        self.direction *= -1
                        self.move_counter = 0

        # Idle timeout handling
        if self.idealing:
            self.idling_counter -= 1
            if self.idling_counter <= 0:
                self.idealing = False
     
      
    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.index]

        # Update animation frame
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.index += 1

        # Reset animation if end reached
        if self.index >= len(self.animation_list[self.action]):
            if self.action == 3:  # Death animation
                self.index = len(self.animation_list[self.action]) - 1  # Freeze on the last frame
            else:
                self.index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.aliveplayer = False
            self.health = 0
            self.speed = 0
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        
class World():
    def __init__(self):
        self.opsticle_list = []
    def process_data(self,data):
        for y,row in enumerate(data):
            for x,tile in enumerate(row):
                if tile >= 0 :
                    img  = image_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x  *TILESIZE
                    img_rect.y = y  *TILESIZE
                    tile_data = (img,img_rect)
                    if tile >= 0 and tile <= 8:
                        self.opsticle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x*TILESIZE, y*TILESIZE)  # ✅ Lowercase variable
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x*TILESIZE, y*TILESIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = Soldier("player", x*TILESIZE, y*TILESIZE, 3, 6, 20, 5)
                        health_bar = Healthbar(120, 95, player.health, player.max_health)
                    elif tile == 16:
                        enemy = Soldier("enemy", x*TILESIZE, y*TILESIZE, 3, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:
                        ammo_drop = Drops(x*TILESIZE, y*TILESIZE, "Ammo")
                        item_box_group.add(ammo_drop)
                    elif tile == 18:
                        grenade_drop = Drops(x*TILESIZE, y*TILESIZE, "Grenade")
                        item_box_group.add(grenade_drop)
                    elif tile == 19:    
                        health_drop = Drops(x*TILESIZE, y*TILESIZE, "Health")
                        item_box_group.add(health_drop)
                    elif tile == 20:
                        exit_door = Exit(img, x*TILESIZE, y*TILESIZE)
                        exit_group.add(exit_door)
        return player,health_bar          
    
    def draw(self):
        for tile in self.opsticle_list:
            screen.blit(tile[0],tile[1])
            

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)  # ✅ Add Sprite init
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILESIZE//2, y + (TILESIZE - self.image.get_height()))

# Fix for Water class
class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)  # ✅ Add Sprite init
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILESIZE//2, y + (TILESIZE - self.image.get_height()))

# Fix for Exit class
class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)  # ✅ Add Sprite init
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILESIZE//2, y + (TILESIZE - self.image.get_height()))

#create tile list
WORLD_DATA  = []
for rows in range(ROWS):
    r = [-1] * COLS
    WORLD_DATA.append(r)
with open(f"game/Shooter/level{level}_data.csv",newline='')as csvfile:
    reader = csv.reader(csvfile,delimiter=",")
    for x,row in enumerate(reader):
        for y,tile in enumerate(row):
            WORLD_DATA[x][y] = int(tile)

world = World()
player ,health_bar = world.process_data(WORLD_DATA)


# Game loop
run = True
while run:
    clock.tick(FPS)

    # Drawing
    drawbg()
    world.draw()
    #show ammo
    draw_text(f"AMMO:", font, (255, 255, 255), 10, 10)
    for x in range(player.ammo):
        screen.blit(bullet_img, (120 + (x * 20), 20))    #show grenades
    draw_text(f"grenadeS: ", font, (255, 255, 255), 10, 50)
    for x in range(player.grenades):
        screen.blit(grenade_img, (190 + (x * 20), 55))
    #show health
    draw_text(f"Health: ", font, (255, 255, 255), 10, 90)
    health_bar.draw(player.health)
    player.update()
    player.draw()
    item_box_group.update()
    item_box_group.draw(screen)
        
   
    for enemy in enemy_group:
        if player.aliveplayer:  # Only run AI if player is alive
            enemy.ai()
        enemy.update()
        enemy.draw()

    bullets_group.update()
    bullets_group.draw(screen)
    grenade_group.update()
    grenade_group.draw(screen)
    explosion_group.update()
    explosion_group.draw(screen)
    decoration_group.update()
    water_group.update()
    exit_group.update()
    decoration_group.draw(screen)  # ✅ Add screen parameter
    water_group.draw(screen)       # ✅ Draw water tiles
    exit_group.draw(screen)        # ✅ Draw exit tiles

    if player.aliveplayer:
        if grenade and player.grenades > 0:
            player.grenades -= 1
            grenade = Grenade(player.rect.centerx + (0.6 * player.rect.size[0] * player.direction), player.rect.centery, player.direction)
            grenade_group.add(grenade)
            grenade = False  # Reset the flag

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
                grenade = True
        # Key release
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w and player.aliveplayer:
                jump = False
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_q:
                grenade = False

    pygame.display.update()

pygame.quit()