import os
import sys
import pygame

from video_utils import get_resource_path

pygame.init()
pygame.mixer.init()


# Загружаем изображение из указанной директории
def load_image(name):
    fullname = get_resource_path(os.path.join("data", name))
    image = pygame.image.load(fullname)
    return image.convert_alpha() if name.endswith('.png') else image


# Загружаем несколько изображений из указанного списка
def load_images(names):
    images = []

    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_path, "data")

    for name in names:
        fullname = os.path.join(data_path, name)

        if not os.path.exists(fullname):
            print(f"Файл не найден: {fullname}")
            continue

        image = pygame.image.load(fullname)
        images.append(image.convert_alpha() if name.endswith('.png') else image)

    return images


# Загружаем звуковой файл из указанной директории
def load_sound(name):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_path, "data")

    fullname = os.path.join(data_path, name)

    if not os.path.exists(fullname):
        print(f"Файл не найден: {fullname}")
        return None

    return pygame.mixer.Sound(fullname)


# Загружаем изображение уровня и карту коллизий для заданного номера уровня
def load_level(level_number):
    level_image = load_image(f'level_{level_number}.png')
    collision_map = load_image(f'collision_{level_number}.png')
    return level_image, collision_map
