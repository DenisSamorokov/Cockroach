import pygame
from controllers import game_loop

pygame.init()
pygame.mixer.init()

# Основной блок программы, запускающий игровой цикл и завершающий работу Pygame
if __name__ == '__main__':
    game_loop()
    pygame.quit()
