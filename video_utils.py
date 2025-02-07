import pygame
from pygamevideo import Video
import sys
import os


# Получаем путь к ресурсу
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


pygame.init()
pygame.mixer.init()
video_sound = pygame.mixer.Sound(get_resource_path('data/video_sound.MP3'))
video3_sound = pygame.mixer.Sound(get_resource_path('data/music3.MP3'))
fail_sound = pygame.mixer.Sound(get_resource_path('data/fail_sound.MP3'))


# Воспроизводим видео и завершаем программу
def play_video_and_quit(video_file):
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

        video = Video(get_resource_path(os.path.join("data", video_file)))
        video.play()

        if video_file == 'video.mp4':
            video_sound.play()
        elif video_file == 'fail.mp4':
            fail_sound.play()

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
                if video_file == 'video.mp4' and not video_sound.get_num_channels():
                    running = False
                elif video_file == 'fail.mp4' and not fail_sound.get_num_channels():
                    running = False
            pygame.display.flip()

    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()
