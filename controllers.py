import os
import sys

import pygame
import random
from models import Player, Enemy, Crumb, Camera
from video_utils import play_video_and_quit, video3_sound
from views import draw_text, show_main_menu, show_level_menu, show_level_complete_message
from utils import get_resource_path, load_level
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, font, BLACK
from pygamevideo import Video


# Воспроизводим музыку в меню
def play_music_on_menu():
    music_file = 'bats.mp3' if random.random() < 0.9 else 'kills.mp3'
    music_path = get_resource_path(os.path.join("data", music_file))
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)


# Воспроизводим музыку для текущего уровня
def play_level_music(level):
    level_sounds = {
        1: 'level1sound.mp3',
        2: 'level2sound.mp3',
        3: 'level3sound.mp3'
    }
    music_file = level_sounds.get(level, 'level1sound.mp3')
    music_path = get_resource_path(os.path.join("data", music_file))

    pygame.mixer.music.stop()

    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)


# Воспроизводим вступительное видео для третьего уровня
def play_video3():
    try:
        pygame.mixer.music.stop()
        pygame.mixer.stop()

        window = pygame.display.set_mode((735, 550))
        screen_width, screen_height = 735, 550

        video_width, video_height = 852, 640
        aspect_ratio = video_width / video_height

        if screen_width / aspect_ratio > screen_height:
            new_width = int(screen_height * aspect_ratio)
            new_height = screen_height
        else:
            new_width = screen_width
            new_height = int(screen_width / aspect_ratio)

        video_x = (screen_width - new_width) // 2
        video_y = (screen_height - new_height) // 2

        video = Video(get_resource_path(os.path.join("data", "video3.mp4")))
        video.play()
        video3_sound.play()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            window.fill((0, 0, 0))
            if video.is_playing:
                frame = video.get_frame()
                if frame:
                    scaled_frame = pygame.transform.scale(frame, (new_width, new_height))
                    window.blit(scaled_frame, (video_x, video_y))
            else:
                if not video3_sound.get_num_channels():
                    running = False
            pygame.display.flip()

    except Exception as e:
        import traceback
        traceback.print_exc()

    return True


# Генерируем крошки на уровне
def generate_crumbs(collision_map, num_crumbs):
    width, height = collision_map.get_size()

    white_positions = [
        (x, y) for x in range(width) for y in range(height)
        if collision_map.get_at((x, y)) == WHITE
    ]

    num_crumbs = min(num_crumbs, len(white_positions))
    selected_positions = random.sample(white_positions, num_crumbs)
    crumbs = [Crumb(x, y) for x, y in selected_positions]

    return crumbs


# Основной игровой цикл
def game_loop():
    player = Player()
    clock = pygame.time.Clock()
    game_state = "main_menu"
    current_level = 1
    unlocked_levels = 1
    level3_start_time = None
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    current_level_image = None
    current_collision_map = None
    crumbs = []
    evil_tarakan = None
    camera = None
    pygame.mixer.init()
    buttons = {}

    while True:
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if game_state == "main_menu":
            buttons = show_main_menu()
            if pygame.mixer.music.get_busy() == 0:
                play_music_on_menu()

        elif game_state == "level_select":
            buttons = show_level_menu()

        if game_state == "playing":
            if current_level == 3:
                if level3_start_time is None:
                    level3_start_time = pygame.time.get_ticks()
                else:
                    current_time = pygame.time.get_ticks()
                    time_left = 42000 - (current_time - level3_start_time)

                    pygame.draw.rect(screen, WHITE, (200, 5, 120, 30))
                    timer_text = font.render(f"Время: {time_left // 1000}", True, BLACK)
                    screen.blit(timer_text, (200, 20))

                    if time_left <= 0:
                        play_video_and_quit('fail.mp4')
                    elif player.score >= 3:
                        play_video_and_quit('video.mp4')

            if not crumbs and current_level < 3:
                unlocked_levels = max(unlocked_levels, current_level + 1)
                game_state = "level_complete"

            camera.update(player)
            screen.blit(current_level_image, camera.camera)
            rotated_player = pygame.transform.rotate(player.image, player.rotation_angle)
            screen.blit(rotated_player, camera.apply(player))
            if evil_tarakan:
                screen.blit(evil_tarakan.image, camera.apply(evil_tarakan))
            for crumb in crumbs:
                screen.blit(crumb.image, camera.apply(crumb))
            if player.is_slapping:
                slap_image = player.slap_images[player.slap_frame]
                slap_rect = slap_image.get_rect(center=camera.apply(player).center)
                screen.blit(slap_image, slap_rect)
            player.update(keys, current_collision_map, crumbs)
            if evil_tarakan:
                evil_tarakan.move_towards(crumbs, current_collision_map)
            draw_text(f'Крошки: {player.score}', (80, 20))

        elif game_state == "level_complete":
            buttons = show_level_complete_message(player.score, 20 if current_level != 2 else 1, current_level)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "main_menu":
                    if "start_game" in buttons and buttons["start_game"].collidepoint(mouse_pos):
                        game_state = "level_select"
                elif game_state == "level_select":
                    if "back" in buttons and buttons["back"].collidepoint(mouse_pos):
                        game_state = "main_menu"
                    else:
                        for i in range(1, 4):
                            key = f"level{i}"
                            if key in buttons and buttons[key].collidepoint(mouse_pos):
                                if i <= unlocked_levels:
                                    if i == 3:
                                        play_video3()
                                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                                        current_level_image, current_collision_map = load_level(3)
                                        camera = Camera(current_level_image.get_width(),
                                                        current_level_image.get_height())
                                        crumbs = generate_crumbs(current_collision_map, num_crumbs=3)
                                        player = Player(800, 340)
                                        evil_tarakan = None
                                        level3_start_time = None
                                        player.score = 0
                                        current_level = 3
                                        game_state = "playing"
                                        pygame.mixer.music.stop()
                                        play_level_music(3)
                                    else:
                                        current_level_image, current_collision_map = load_level(i)
                                        if i == 1:
                                            num_crumbs = 20
                                        elif i == 2:
                                            num_crumbs = 1
                                        elif i == 3:
                                            num_crumbs = 3
                                        camera = Camera(current_level_image.get_width(),
                                                        current_level_image.get_height())
                                        crumbs = generate_crumbs(current_collision_map, num_crumbs=num_crumbs)
                                        if i == 1:
                                            player = Player(322, 212)
                                            evil_tarakan = Enemy(340, 400)
                                        elif i == 2:
                                            player = Player(203, 240)
                                            evil_tarakan = Enemy(500, 430)
                                        player.score = 0
                                        current_level = i
                                        game_state = "playing"
                                        pygame.mixer.music.stop()
                                        play_level_music(i)

                elif game_state == "level_complete":
                    if "back" in buttons and buttons["back"].collidepoint(mouse_pos):
                        game_state = "level_select"
                    if "next_level" in buttons and buttons["next_level"].collidepoint(mouse_pos):
                        current_level += 1
                        if current_level > 3:
                            play_video_and_quit('video.mp4')
                        else:
                            if current_level == 3:
                                play_video3()
                            current_level_image, current_collision_map = load_level(current_level)
                            camera = Camera(current_level_image.get_width(), current_level_image.get_height())
                            if current_level == 1:
                                num_crumbs = 20
                            elif current_level == 2:
                                num_crumbs = 1
                            elif current_level == 3:
                                num_crumbs = 3
                            crumbs = generate_crumbs(current_collision_map, num_crumbs=num_crumbs)

                            if current_level == 1:
                                player = Player(322, 212)
                                evil_tarakan = Enemy(340, 400)
                            elif current_level == 2:
                                player = Player(203, 240)
                                evil_tarakan = Enemy(500, 430)
                            elif current_level == 3:
                                player = Player(800, 340)
                                evil_tarakan = None
                            player.score = 0
                            game_state = "playing"
                            pygame.mixer.music.stop()
                            play_level_music(current_level)

        pygame.display.flip()
        clock.tick(60)
