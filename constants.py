import pygame

# Размеры экрана
SCREEN_WIDTH, SCREEN_HEIGHT = 735, 550
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Таракан Евдокий')

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TILE_SIZE = 50  # Размер клетки на карте

# Шрифты
font = pygame.font.SysFont('Arial', 30)
