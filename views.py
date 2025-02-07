import pygame
from constants import WHITE, SCREEN_HEIGHT
from utils import load_image
from constants import BLACK, SCREEN_WIDTH, font, screen
from video_utils import play_video_and_quit


# Отображаем текст на экране
def draw_text(text, pos):
    text_surface = font.render(text, True, BLACK)
    rect = text_surface.get_rect(center=pos)
    screen.blit(text_surface, rect)
    return rect


# Показываем главное меню игры
def show_main_menu():
    screen.fill(WHITE)
    ava_image = load_image('ava.png')
    start_game_image = load_image('play.png')
    screen.blit(ava_image, (SCREEN_WIDTH // 2 - ava_image.get_width() // 2, 50))
    start_rect = screen.blit(start_game_image, (SCREEN_WIDTH // 2 - start_game_image.get_width() // 2, 290))

    return {"start_game": start_rect}


# Отображаем меню выбора уровня
def show_level_menu():
    screen.fill(WHITE)
    level1_image = load_image('level1.png')
    level2_image = load_image('level2.png')
    level3_image = load_image('level3.png')

    level1_rect = screen.blit(level1_image, (SCREEN_WIDTH // 2 - level1_image.get_width() // 2, 150))
    level2_rect = screen.blit(level2_image, (SCREEN_WIDTH // 2 - level2_image.get_width() // 2, 250))
    level3_rect = screen.blit(level3_image, (SCREEN_WIDTH // 2 - level3_image.get_width() // 2, 350))
    back_image = load_image('back.png')
    back_rect = screen.blit(back_image, (20, 20))
    return {"level1": level1_rect, "level2": level2_rect, "level3": level3_rect, "back": back_rect}


# Показываем сообщение о завершении уровня
def show_level_complete_message(score, total_crumbs, level):
    if level == 3:
        start_time = pygame.time.get_ticks()
        screen.fill(WHITE)

        percentage = (score / total_crumbs) * 100 if total_crumbs > 0 else 0
        draw_text(f"Вы прошли уровень на {percentage:.2f}%", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

        if pygame.time.get_ticks() - start_time < 2000:
            pygame.display.update()
            return

        play_video_and_quit()
    else:
        screen.fill(WHITE)
        percentage = (score / total_crumbs) * 100 if total_crumbs > 0 else 0
        draw_text(f"Вы прошли уровень на {percentage:.2f}%", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        next_level_button = draw_text("Перейти на следующий уровень", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        back_image = load_image("back.png")
        back_rect = screen.blit(back_image, (
            20, SCREEN_HEIGHT - back_image.get_height() - 20))
        pygame.display.update()
        return {"next_level": next_level_button, "back": back_rect}
