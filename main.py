import pygame
import os
import time
import random

pygame.font.init()

WIDTH, HEIGHT = 750, 750
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader")

# images
SPACE_SHIP_RED = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
SPACE_SHIP_GREEN = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
SPACE_SHIP_BLUE = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# final boss ship
FINAL_BOSS = pygame.image.load(os.path.join("assets", "final_boss_ship.png"))

# main ship
SPACE_SHIP_YELLOW = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
FINAL_LASER = pygame.image.load(os.path.join("assets", "final_laser.png"))

# background
size = (WIDTH, HEIGHT)
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), size)


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (height > self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x_pos, y_pos, health=100):
        self.x = x_pos
        self.y = y_pos
        self.health = health
        self.ship_image = None
        self.laser_img = None
        self.lasers = []
        self.cooldown = 0

    def draw(self, window):
        window.blit(self.ship_image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown_func()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def get_width(self):
        return self.ship_image.get_width()

    def get_height(self):
        return self.ship_image.get_height()

    def cooldown_func(self):
        if self.cooldown >= self.COOLDOWN:
            self.cooldown = 0
        elif self.cooldown > 0:
            self.cooldown += 1

    def shoot(self):
        if self.cooldown == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown = 1


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_image = SPACE_SHIP_YELLOW
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(
            self.ship_image)  # mask helps us realize if we have actually hit a pixer or not
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown_func()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def lasers_for_boss(self, vel, obj):
        self.cooldown_func()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                if laser.collision(obj):
                    obj.health -= 5
                    if laser in self.lasers:
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (
            self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width(),
            10))  # drawing health bar below player
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.ship_image.get_height() + 10,
            self.ship_image.get_width() * (self.health / self.max_health),
            10))  # drawing health bar below player


class FinalBoss(Ship):
    def __init__(self, x, y, health=200):
        super().__init__(x, y, health)
        self.ship_image = FINAL_BOSS
        self.laser_img = RED_LASER
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.max_health = health
        self.laser_img_2 = FINAL_LASER
        self.laser_img_3 = BLUE_LASER

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cooldown == 0:
            laser = Laser(self.x + 150, self.y + 50, self.laser_img_2)
            self.lasers.append(laser)
            self.cooldown = 1

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (
            self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width(),
            10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.ship_image.get_height() + 10,
            self.ship_image.get_width() * ((self.health) / self.max_health),
            10))

    def shoot_edge_lasers(self):
        if self.cooldown == 0:
            edge_laser_1 = Laser(self.x + 10, self.y, self.laser_img_3)
            edge_laser_2 = Laser(self.x + 317, self.y, self.laser_img_3)
            self.lasers.append(edge_laser_1)
            self.lasers.append(edge_laser_2)
            self.cooldown = 1

    def shoot_other_lasers(self):
        if self.cooldown == 0:
            laser = Laser(self.x + 50, self.y + 50, self.laser_img)
            laser_2 = Laser(self.x + 250, self.y + 50, self.laser_img)
            self.lasers.append(laser)
            self.lasers.append(laser_2)
            self.cooldown = 1


class Enemy(Ship):
    COLOR_MAP = {
        "red": (SPACE_SHIP_RED, RED_LASER),
        "green": (SPACE_SHIP_GREEN, GREEN_LASER),
        "blue": (SPACE_SHIP_BLUE, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_image, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_image)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cooldown == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y

    return obj1.mask.overlap(obj2.mask,
                             (offset_x, offset_y)) is not None  # should return us a tuple that shows point of
    # intersection


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    FONT = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 80)
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    won = False
    won_count = 0

    enemies = []
    wave_length = 5
    enemy_vel = 1
    laser_vel = 5

    player = Player(300, 630)
    player_vel = 5

    final_boss = FinalBoss(150, -175)

    def redraw_window():
        WINDOW.blit(BACKGROUND, (0, 0))
        # draw text
        lives_text = FONT.render(f"Lives: {lives}", True, (255, 120, 0))
        level_text = FONT.render(f"Level: {level}", True, (255, 120, 0))

        WINDOW.blit(lives_text, (10, 10))
        WINDOW.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WINDOW)

        player.draw(WINDOW)

        if level > 5:
            final_boss.draw(WINDOW)

        pygame.display.update()

    while run:
        clock.tick(FPS)

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
            pygame.display.update()
        if lost:
            WINDOW.blit(BACKGROUND, (0, 0))
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            WINDOW.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))
            if lost_count > FPS * 4:
                run = False
            else:
                continue

        if final_boss.health <= 0:
            won = True
            won_count += 1
            pygame.display.update()
        if won:
            WINDOW.blit(BACKGROUND, (0, 0))
            final_font = pygame.font.SysFont("comicsans", 50)
            final_label = final_font.render("GOOD GAME!!!", 1, (255, 255, 255))
            WINDOW.blit(final_label, (WIDTH / 2 - final_label.get_width() / 2, 350))
            if won_count > FPS * 4:
                run = False
            else:
                continue

        if len(enemies) == 0 and level <= 5:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(0, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(['red', 'blue', 'green']))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()  # gives a dict that shows which keys are pressed which not
        if keys[pygame.K_a] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 10 < HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 100) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        if level > 5:
            final_boss.move_lasers(laser_vel, player)
            if final_boss.y < 0:
                final_boss.move(enemy_vel)
            elif final_boss.y == 100:
                final_boss.move(0)
            enemies = []
            if random.randrange(0, 3) == 1:
                final_boss.shoot()
            elif random.randrange(0, 4) == 2:
                final_boss.shoot_edge_lasers()
            else:
                final_boss.shoot_other_lasers()

            if collide(player, final_boss):
                player.health -= 50
                final_boss.health -= 10
            player.lasers_for_boss(-laser_vel, final_boss)

        player.move_lasers(-laser_vel, enemies)
        redraw_window()


def main_menu():
    run = True
    title_font = pygame.font.SysFont("comicsans", 50)
    while run:
        WINDOW.blit(BACKGROUND, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        WINDOW.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()


main_menu()
