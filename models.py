import pygame
import random
from utils import load_images, load_image, get_resource_path
from constants import BLACK, SCREEN_WIDTH, SCREEN_HEIGHT
from pygame.time import Clock

clock = Clock()


# Класс для управления камерой в игре
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x + SCREEN_WIDTH // 2 - target.rect.width // 2
        y = -target.rect.y + SCREEN_HEIGHT // 2 - target.rect.height // 2

        x = max(-(self.width - SCREEN_WIDTH), min(0, x))
        y = max(-(self.height - SCREEN_HEIGHT), min(0, y))

        self.camera = pygame.Rect(x, y, SCREEN_WIDTH, SCREEN_HEIGHT)


player_image = load_image('tarakan.png')
crumb_image = load_image('crumb.png')
enemy_image = load_image('enemy.png')


# Класс игрока с методами для движения, анимации и взаимодействия
class Player:
    def __init__(self, x=322, y=212):
        self.images = load_images(['tarakan1.png', 'tarakan2.png', 'tarakan3.png', 'tarakan4.png'])
        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 3
        self.score = 0
        self.clock = pygame.time.Clock()

        self.frame_duration = 100
        self.last_update_time = pygame.time.get_ticks()

        self.rotation_angle = 0

        self.idle_timer = 0
        self.idle_threshold = 3000

        self.slap_images = load_images(['tapok1.png', 'tapok1.png', 'tapok1.png'])
        self.slap_frame = 0
        self.is_slapping = False
        self.slap_start_time = 0

    def check_idle(self, moving):
        if not moving:
            self.idle_timer += clock.get_time()
            if self.idle_timer >= self.idle_threshold and not self.is_slapping:
                self.start_slap()
        else:
            self.idle_timer = 0

    def draw_slap(self, screen):
        if self.is_slapping:
            slap_image = self.slap_images[self.slap_frame]
            slap_rect = slap_image.get_rect(center=self.rect.center)
            screen.blit(slap_image, slap_rect)

            current_time = pygame.time.get_ticks()
            if current_time - self.slap_start_time > 100:
                self.slap_frame += 1
                self.slap_start_time = current_time

            if self.slap_frame >= len(self.slap_images):
                self.is_slapping = False
                self.slap_frame = 0
                self.idle_timer = 0

    def start_slap(self):
        self.is_slapping = True
        self.slap_start_time = pygame.time.get_ticks()
        self.slap_frame = 0

    def check_collision(self, new_x, new_y, collision_map):
        if new_x < 0 or new_y < 0 or new_x >= collision_map.get_width() or new_y >= collision_map.get_height():
            return True

        for dx in [0, self.rect.width - 1]:
            for dy in [0, self.rect.height - 1]:
                x = new_x + dx
                y = new_y + dy
                if x < 0 or y < 0 or x >= collision_map.get_width() or y >= collision_map.get_height():
                    return True
                if collision_map.get_at((x, y)) == BLACK:
                    return True
        return False

    def update(self, keys, collision_map, crumbs):
        new_x, new_y = self.rect.x, self.rect.y
        moving = False

        if keys[pygame.K_LEFT] and not self.check_collision(new_x - self.speed, new_y, collision_map):
            new_x -= self.speed
            self.rotation_angle = 90
            moving = True
        if keys[pygame.K_RIGHT] and not self.check_collision(new_x + self.speed, new_y, collision_map):
            new_x += self.speed
            self.rotation_angle = -90
            moving = True
        if keys[pygame.K_UP] and not self.check_collision(new_x, new_y - self.speed, collision_map):
            new_y -= self.speed
            self.rotation_angle = 0
            moving = True
        if keys[pygame.K_DOWN] and not self.check_collision(new_x, new_y + self.speed, collision_map):
            new_y += self.speed
            self.rotation_angle = 180
            moving = True

        self.rect.x, self.rect.y = new_x, new_y
        hrust_sound = pygame.mixer.Sound(get_resource_path('data/hrust.mp3'))

        if moving:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update_time > self.frame_duration:
                self.current_frame = (self.current_frame + 1) % len(self.images)
                self.image = self.images[self.current_frame]
                self.last_update_time = current_time

        for crumb in crumbs[:]:
            if self.rect.colliderect(crumb.rect):
                crumbs.remove(crumb)
                self.score += 1
                hrust_sound.play()
        self.check_idle(moving)

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, self.rotation_angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, new_rect)

        self.draw_slap(screen)


# Класс для управления поведением враждебного таракана
class Enemy:
    def __init__(self, x, y):
        self.image = enemy_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2
        self.target = None
        self.direction = pygame.math.Vector2(0, 0)
        self.rect.topleft = (x, y)

    def check_collision(self, new_x, new_y, collision_map):
        new_x = int(new_x)
        new_y = int(new_y)

        if new_x < 0 or new_y < 0 or new_x >= collision_map.get_width() or new_y >= collision_map.get_height():
            return True

        for dx in [0, self.rect.width - 1]:
            for dy in [0, self.rect.height - 1]:
                x = new_x + dx
                y = new_y + dy
                if x < 0 or y < 0 or x >= collision_map.get_width() or y >= collision_map.get_height():
                    return True
                if collision_map.get_at((x, y)) == BLACK:
                    return True
        return False

    def choose_target(self, crumbs):
        if not self.target and crumbs:
            self.target = random.choice(crumbs)
            self.update_direction()

    def update_direction(self):
        if self.target:
            direction_vector = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
            if direction_vector.length() > 0:
                self.direction = direction_vector.normalize() * self.speed

    def move_towards(self, crumbs, collision_map):
        if self.target and self.target not in crumbs:
            self.target = None

        self.choose_target(crumbs)
        if self.target:
            self.update_direction()
            new_x = self.rect.x + self.direction.x
            new_y = self.rect.y + self.direction.y

            if not self.check_collision(new_x, new_y, collision_map):
                self.rect.x = new_x
                self.rect.y = new_y
            else:
                adjusted = False
                for angle in [15, -15, 30, -30, 45, -45]:
                    new_direction = self.direction.rotate(angle)
                    test_x = self.rect.x + new_direction.x
                    test_y = self.rect.y + new_direction.y
                    if not self.check_collision(test_x, test_y, collision_map):
                        self.direction = new_direction
                        self.rect.x = test_x
                        self.rect.y = test_y
                        adjusted = True
                        break
                if not adjusted:
                    self.target = None
                    self.direction = pygame.math.Vector2(0, 0)

            if self.target and self.rect.colliderect(self.target.rect):
                if self.target in crumbs:
                    crumbs.remove(self.target)
                self.target = None

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# Класс для появления крошек в игре
class Crumb:
    def __init__(self, x, y):
        self.image = crumb_image
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)
