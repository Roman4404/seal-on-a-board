import pygame
import random
import time
import sqlite3
import json

# Функция для инициализации базы данных
def init_db():
    conn = sqlite3.connect('highscore.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY,
            high_score INTEGER NOT NULL
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM scores')
    if cursor.fetchone()[0] == 0:  # Если таблица пуста, добавляем начальный high score
        cursor.execute('INSERT INTO scores (high_score) VALUES (0)')
    conn.commit()
    conn.close()

def update_high_score(new_high_score):
    conn = sqlite3.connect('highscore.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE scores SET high_score = ? WHERE id = 1', (new_high_score,))
    conn.commit()
    conn.close()

def get_high_score():
    conn = sqlite3.connect('highscore.db')
    cursor = conn.cursor()
    cursor.execute('SELECT high_score FROM scores WHERE id = 1')
    high_score = cursor.fetchone()[0]
    conn.close()
    return high_score

def save_settings(volume, track='track1'):
    settings = {
        'volume': volume,
        'track': track
    }
    with open('settings.json', 'w') as f:
        json.dump(settings, f)

def load_settings():
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            return (settings.get('volume', 0.5),
                    settings.get('track', 'track1'))
    except (FileNotFoundError, json.JSONDecodeError):
        return (0.5, 'track1')  # Возвращаем значения по умолчанию, если файл не найден или поврежден

pygame.init()
pygame.mixer.init()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
paused = False  # Переменная для отслеживания состояния паузы
COUNTDOWN_DURATION = 1000 # для обратного отсчета

# Загрузка изображений
penguin_image = pygame.image.load('data/Pingein_player2.png')
penguin_down_image = pygame.image.load('data/Pingein_concept2_animated _down_player.png')
cloud_image = pygame.image.load('data/cloud1.png')
water_image = pygame.image.load('data/water_concept.png')
sky_image = pygame.image.load('data/sky_concept2.png')
big_wave_image = pygame.image.load('data/wave.png')
small_wave_image = pygame.image.load('data/small_wave.png')
down_kant_image = pygame.image.load('data/Pingein_concept_animated_down_kant_player.png')
bird_image = pygame.image.load('data/bird_concept.png')
seal_image = pygame.image.load('data/kotik.png')
seal_damag = pygame.image.load('data/kotik_damag.png')

# Группы спрайтов
all_sprites = pygame.sprite.Group()
player_sprites = pygame.sprite.Group()
waves_sprites = pygame.sprite.Group()
cloud_sprites = pygame.sprite.Group()
bird_sprites = pygame.sprite.Group()
seals_sprites = pygame.sprite.Group()

# Класс для пингвина
class Penguin(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = penguin_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 - 100  # Начальная позиция по оси X
        self.start_y = SCREEN_HEIGHT // 2 + 115  # Позиция по оси Y
        self.rect.y = self.start_y
        self.initial_x = self.rect.x  # Сохраняем начальную позицию
        self.sit_down = False
        self.is_jumping = False  # Состояние прыжка
        self.jump_height = 22  # Высота прыжка
        self.gravity = 1  # Гравитация
        self.velocity_y = 0  # Вертикальная скорость
        self.is_catching_bird = False  # Новое состояние для захвата птицы
        self.catch_start_time = 0  # Время начала захвата
        self.hanging = False  # Новое состояние для зависания
        self.hang_start_time = 0  # Время начала зависания
        # Энергия
        self.max_energy = 100  # Максимальная энергия
        self.current_energy = self.max_energy  # Текущая энергия
        self.energy_recovery_rate = self.max_energy / 22  # Восстановление энергии в секунду
        self.last_energy_update_time = pygame.time.get_ticks()  # Время последнего обновления энергии

    def animated_down(self):
        self.image = penguin_down_image
        self.sit_down = True

    def animated_up(self):
        self.image = penguin_image
        self.sit_down = False

    def animated_kant(self):
        self.image = down_kant_image

    def jump(self):
        if self.is_jumping:
            # Обновляем вертикальную скорость
            self.velocity_y += self.gravity
            self.rect.y += self.velocity_y

            # Проверяем, достиг ли пингвин максимальной высоты
            if self.rect.y >= self.start_y:
                self.rect.y = self.start_y  # Возвращаем на начальную высоту
                self.is_jumping = False  # Завершаем прыжок
                self.velocity_y = 0  # Сбрасываем вертикальную скорость

        else:
            # Если не прыгаем, то возвращаемся на начальную высоту
            if self.rect.y < self.start_y:
                self.velocity_y += self.gravity
                self.rect.y += self.velocity_y

    def update(self):
        if self.hanging:
            if pygame.time.get_ticks() - self.hang_start_time >= 1000:  # 1 секунда
                self.hanging = False  # Завершаем зависание
                self.rect.y = self.start_y  # Возвращаем на начальную высоту
            return  # Прерываем обновление, чтобы не изменять позицию

        # Остальная логика обновления
        self.rect = self.rect.move(0, 0)

        # Восстановление энергии
        current_time = pygame.time.get_ticks()
        if current_time - self.last_energy_update_time >= 1000:  # Каждую секунду
            if self.current_energy < self.max_energy:
                self.current_energy += self.energy_recovery_rate
                if self.current_energy > self.max_energy:
                    self.current_energy = self.max_energy
            self.last_energy_update_time = current_time

        self.jump()  # Обновляем состояние прыжка


# Класс для препятствий
class Wave(pygame.sprite.Sprite):
    def __init__(self, id_obstacle, image, type_wave, x=-SCREEN_WIDTH, y=SCREEN_HEIGHT - 300, *group):
        super().__init__(*group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x  # Начальная позиция волны (за левым краем экрана)
        self.rect.y = y  # Положение препятствия
        self.id = id_obstacle
        self.type = type_wave  # Маленькая волна = "small_wave", Большая волна = "big_wave"

    def update(self, speed):
        self.rect = self.rect.move(speed, 0)  # Движение препятствия вправо


class Water:
    def __init__(self):
        self.image = pygame.transform.scale(water_image, (96 * 1.5, 96 * 1.5))

    def draw(self, screen):
        for x in range(0, 1280, 96):
            screen.blit(self.image, (x, SCREEN_HEIGHT - 96))


class Cloud(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = cloud_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - 500  # Положение препятствия

    def update(self, speed):
        self.rect = self.rect.move(-speed, 0)


class Bird(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = bird_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH  # Начальная позиция по оси X
        self.rect.y = SCREEN_HEIGHT - 480
        self.caught = False  # Новое состояние для отслеживания, поймана ли птица
        self.catch_time = 0  # Время, когда птица была поймана

    def update(self):
        if self.caught:
            # Если птица поймана, она остается на месте с пингвином
            if pygame.time.get_ticks() - self.catch_time > 2000:  # 2 секунды
                self.caught = False  # Птица улетает
                self.rect.x -= 5  # Птица продолжает двигаться влево
        else:
            self.rect.x -= 5  # Движение птицы влево

        # Удаление птицы, если она вышла за экран
        if self.rect.x < -self.rect.width:
            self.kill()


class Seal(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = seal_image
        self.damag_image = seal_damag
        self.rect = self.image.get_rect()
        self.rect.x = -self.rect.width
        self.rect.y = SCREEN_HEIGHT - 175
        self.is_damaged = False
        self.damage_time = 0  # Добавляем новое свойство

    def update(self, speed):
        # Восстанавливаем текстуру через 1 секунду
        if self.is_damaged and pygame.time.get_ticks() - self.damage_time > 1000:
            self.is_damaged = False
            self.image = seal_image
        if self.is_damaged:
            self.image = self.damag_image

        self.rect.x += speed
        if self.rect.x > SCREEN_WIDTH:
            self.kill()


# Занимается небом
class Sky:
    def __init__(self):
        self.image = pygame.transform.scale(sky_image, (540 * 1.5, 540 * 1.5))
        self.clouds = []

    def draw_sky(self, screen):
        for x in range(0, 1280, 512):
            screen.blit(self.image, (x, 0))

    def draw_cloud(self, screen):
        if random.randint(1, 100) < 2 and len(self.clouds) < 4:
            self.clouds.append(Cloud(cloud_sprites))

        cloud_sprites.update(5)
        cloud_sprites.draw(screen)

        for cloud in self.clouds:
            if cloud.rect.x < 0:  # Удаление облака, вышедших за экран
                self.clouds.remove(cloud)


# Частицы воды(Сырая)
class Particle_Water(pygame.sprite.Sprite):
    fire = [pygame.image.load("data/water_particle.png")]  # Исходное размер текстуры
    for scale in (3, 6, 9):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy, penguin):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)  # Изображение
        self.rect = self.image.get_rect()  # Размеры
        self.penguin = penguin  # Пингвин (нужен для получения координат)

        # У каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # И свои координаты
        self.rect.x, self.rect.y = pos

        # Гравитация будет одинаковой (значение константы)
        self.gravity = -0.4

    def update(self):
        # Применяем гравитационный эффект:
        self.velocity[1] += self.gravity
        self.rect.x -= self.velocity[0]
        self.rect.y += self.velocity[1]

        # Убиваем, если частица ушла за экран
        if not self.rect.colliderect((self.penguin.rect.x - self.penguin.rect.width, self.penguin.rect.y + 110,
                                      self.penguin.rect.x, self.penguin.rect.y)):
            self.kill()

def draw_energy_bar(screen, penguin):
    bar_width = 300
    bar_height = 20
    energy_ratio = penguin.current_energy / penguin.max_energy
    # Создаем прозрачный фон
    bar_background = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
    # Рисуем фон прогресс-бара
    pygame.draw.rect(bar_background, (255, 0, 0, 128), (0, 0, bar_width, bar_height))  # Полупрозрачный фон
    # Рисуем прогресс-бар
    pygame.draw.rect(bar_background, (0, 255, 0), (0, 0, bar_width * energy_ratio, bar_height))  # Энергия
    # Переливающийся цвет
    if energy_ratio > 0.67:
        border_color = (255, 255, 255)  # Белый, если больше 67%
    elif energy_ratio > 0.33:
        border_color = (0, 0, 255)  # Синий, если между 33% и 67%
    else:
        border_color = (255, 0, 0)  # Красный, если меньше 33%

    # Рисуем обводку с изменяющимся цветом
    pygame.draw.rect(screen, border_color, (10, 250, bar_width, bar_height), 2)  # Обводка
    # Рисуем прогресс-бар на экране
    screen.blit(bar_background, (10, 250))  # Отображаем прогресс-бар
    # Отображение текста "Jump Energy" на шкале
    font = pygame.font.Font(None, 30)  # Создаем объект шрифта
    jump_energy_text = font.render("JUMP ENERGY", True, BLUE)
    # Получаем прямоугольник текста
    text_rect = jump_energy_text.get_rect(center=(10 + bar_width // 2, 250 + bar_height // 2))
    screen.blit(jump_energy_text, text_rect)  # Отображаем текст на шкале

def show_loading_screen(screen):
    font = pygame.font.Font(None, 74)
    loading_text = font.render("Loading...", True, WHITE)
    loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

    progress = 0
    total_steps = 100
    bar_width = 600
    bar_height = 50
    bar_x = (SCREEN_WIDTH - bar_width) // 2
    bar_y = SCREEN_HEIGHT // 2 + 20

    penguin_x = bar_x
    penguin_y = bar_y + 5

    bird_x = bar_x
    bird_y = bar_y - 50

    toggle_penguin = True
    toggle_bird = True

    while progress <= total_steps:
        screen.fill(BLUE)
        screen.blit(loading_text, loading_rect)

        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        pygame.draw.rect(screen, WHITE,
                         (bar_x + 2, bar_y + 2, (bar_width - 4) * (progress / total_steps), bar_height - 4))

        percent_text = font.render(f"{progress}%", True, (255, 0, 0))
        percent_rect = percent_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        screen.blit(percent_text, percent_rect)

        if toggle_penguin:
            screen.blit(penguin_image, (penguin_x, penguin_y))
        else:
            screen.blit(penguin_down_image, (penguin_x, penguin_y))

        if toggle_bird:
            screen.blit(bird_image, (bird_x, bird_y))
        else:
            screen.blit(bird_image, (bird_x, bird_y))

        toggle_penguin = not toggle_penguin
        toggle_bird = not toggle_bird
        pygame.display.flip()
        time.sleep(0.05)
        progress += 1
        # Двигаем пингвина по прогресс-бару
        penguin_x = bar_x + (bar_width - 4) * (progress / total_steps) - penguin_image.get_width() // 2
        # Двигаем птицу в противоположном направлении
        bird_x = bar_x + bar_width - (bar_width - 4) * (progress / total_steps) - bird_image.get_width() // 2

    time.sleep(1)

def draw_rounded_rect(surface, color, rect, radius):
    """Рисует скругленный прямоугольник."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def show_pause_menu(screen):
    # Сохраняем состояние музыки
    was_playing = pygame.mixer.music.get_busy()
    if was_playing:
        pygame.mixer.music.pause()

    font = pygame.font.Font(None, 74)
    pause_text = font.render("Paused", True, WHITE)
    pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))

    font_small = pygame.font.Font(None, 36)
    resume_text = font_small.render("Продолжить", True, (0, 255, 0))
    resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))

    restart_text = font_small.render("Рестарт", True, (255, 186, 0))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))

    settings_text = font_small.render("Настройки", True, (70, 120, 50))
    settings_rect = settings_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))

    exit_text = font_small.render("Выход", True, (255, 0, 0))
    exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))

    while True:
        screen.fill((0, 0, 0, 0))
        screen.blit(pause_text, pause_rect)

        # Рисуем скругленные прямоугольники
        draw_rounded_rect(screen, (255, 255, 255), resume_rect.inflate(20, 10), 15)
        draw_rounded_rect(screen, (255, 255, 255), restart_rect.inflate(20, 10), 15)
        draw_rounded_rect(screen, (255, 255, 255), settings_rect.inflate(20, 10), 15)
        draw_rounded_rect(screen, (255, 255, 255), exit_rect.inflate(20, 10), 15)

        screen.blit(resume_text, resume_rect)
        screen.blit(restart_text, restart_rect)
        screen.blit(settings_text, settings_rect)
        screen.blit(exit_text, exit_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                if was_playing:
                    pygame.mixer.music.stop()
                return "exit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if resume_rect.collidepoint(mouse_pos):
                    if was_playing:
                        pygame.mixer.music.unpause()
                    return "resume"
                if restart_rect.collidepoint(mouse_pos):
                    if was_playing:
                        pygame.mixer.music.stop()
                    return "restart"
                if settings_rect.collidepoint(mouse_pos):
                    show_settings_menu(screen)
                if exit_rect.collidepoint(mouse_pos):
                    if show_exit_confirmation(screen):
                        pygame.quit()
                        return "exit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if was_playing:
                        pygame.mixer.music.unpause()
                    return "resume"

# Функция для отображения заставки
def show_start_screen(screen):
    font = pygame.font.Font(None, 74)
    title_text = font.render("Seal on a Board", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))

    font_small = pygame.font.Font(None, 36)
    play_text = font_small.render("Играть", True, (100, 0, 255))
    play_rect = play_text.get_rect(center=(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))  # Кнопка "Играть" слева

    exit_text = font_small.render("Выход", True, (255, 0, 0))
    exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2))  # Кнопка "Выход" справа

    settings_text = font_small.render("Настройки", True, (70, 120, 50))
    settings_rect = settings_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))  # Кнопка "Настройки" под ними

    while True:
        screen.fill(BLUE)
        screen.blit(title_text, title_rect)

        # Рисуем скругленные прямоугольники вокруг текста
        draw_rounded_rect(screen, (255, 255, 255), play_rect.inflate(20, 10), 15)
        draw_rounded_rect(screen, (255, 255, 255), exit_rect.inflate(20, 10), 15)
        draw_rounded_rect(screen, (255, 255, 255), settings_rect.inflate(20, 10), 15)
        screen.blit(play_text, play_rect)
        screen.blit(exit_text, exit_rect)
        screen.blit(settings_text, settings_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_rect.collidepoint(mouse_pos):
                    return
                if exit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    return
                if settings_rect.collidepoint(mouse_pos):
                    show_settings_menu(screen)  # Переход к меню настроек
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return
                if event.key == pygame.K_q:
                    pygame.quit()
                    return

# Функция для отображения диалогового окна
def show_game_over_screen(screen, score):
    font = pygame.font.Font(None, 74)
    text = font.render("Game Over", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    font_small = pygame.font.Font(None, 36)
    score_text = font_small.render(f"Your Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    restart_text = font_small.render("Рестарт", True, (255, 186, 0))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    settings_text = font_small.render("Настройки", True, (70, 120, 50))
    settings_rect = settings_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))

    exit_text = font_small.render("В другой раз", True, (255, 0, 0))
    exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))  # Добавляем кнопку выхода

    while True:
        screen.fill(BLUE)
        screen.blit(text, text_rect)
        screen.blit(score_text, score_rect)

        # Рисуем скругленные прямоугольники вокруг текста
        draw_rounded_rect(screen, (255, 255, 255), restart_rect.inflate(20, 10), 15)
        draw_rounded_rect(screen, (255, 255, 255), settings_rect.inflate(20, 10), 15)
        draw_rounded_rect(screen, (255, 255, 255), exit_rect.inflate(20, 10), 15)

        screen.blit(restart_text, restart_rect)
        screen.blit(settings_text, settings_rect)
        screen.blit(exit_text, exit_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False  # Выход из игры
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if restart_rect.collidepoint(mouse_pos):  # Проверка, попадает ли мышь на кнопку "Рестарт"
                    return True  # Возвращаемся в основной игровой цикл для перезапуска
                if settings_rect.collidepoint(mouse_pos):  # Проверка, попадает ли мышь на кнопку "Настройки"
                    show_settings_menu(screen)
                if exit_rect.collidepoint(mouse_pos):  # Проверка, попадает ли мышь на кнопку "В другой раз"
                    pygame.quit()
                    return False  # Выход из игры
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Если нажата клавиша "R"
                    return True  # Возвращаемся в основной игровой цикл для перезапуска
                if event.key == pygame.K_q:  # Если нажата клавиша "Q"
                    pygame.quit()
                    return False  # Выход из игры


def show_settings_menu(screen):
    current_tab = 'audio'  # 'audio' или 'controls'
    settings = {
        'volume': load_settings()[0],
        'track': load_settings()[1]
    }
    tracks = {
        'track1': 'Музыка 1',
        'track2': 'Музыка 2'
    }

    font = pygame.font.Font(None, 36)
    while True:
        screen.fill((0, 0, 0))

        # Рисуем вкладки
        tab_audio_rect = pygame.Rect(50, 20, 150, 40)
        tab_controls_rect = pygame.Rect(220, 20, 150, 40)

        # Кнопки вкладок
        pygame.draw.rect(screen, (0, 150, 0) if current_tab == 'audio' else (50, 50, 50), tab_audio_rect,
                         border_radius=10)
        pygame.draw.rect(screen, (0, 150, 0) if current_tab == 'controls' else (50, 50, 50), tab_controls_rect,
                         border_radius=10)

        tab_audio_text = font.render("Аудио", True, (255, 255, 255))
        tab_controls_text = font.render("Управление", True, (255, 255, 255))
        screen.blit(tab_audio_text, tab_audio_text.get_rect(center=tab_audio_rect.center))
        screen.blit(tab_controls_text, tab_controls_text.get_rect(center=tab_controls_rect.center))

        if current_tab == 'audio':
            # Содержимое вкладки аудио
            volume_text = font.render(f"Громкость: {int(settings['volume'] * 100)}%", True, (255, 255, 255))
            screen.blit(volume_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 150))

            volume_slider_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100, 200, 10)
            pygame.draw.rect(screen, (255, 255, 255), volume_slider_rect)
            pygame.draw.rect(screen, (0, 255, 0), (volume_slider_rect.x + int(settings['volume'] * 200) - 5,
                                                   volume_slider_rect.y - 5, 10, 20))

            # Выбор треков
            y_offset = SCREEN_HEIGHT // 2 - 50
            for track_id, track_name in tracks.items():
                btn_color = (0, 255, 0) if settings['track'] == track_id else (100, 100, 100)
                btn_text = font.render(track_name, True, btn_color)
                btn_rect = btn_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                screen.blit(btn_text, btn_rect)
                y_offset += 40

        else:
            # Содержимое вкладки управления
            controls = [
                "UP - Прыжок",
                "DOWN - Присесть",
                "ESC - Меню паузы",
                "R - Рестарт"
            ]

            y_offset = SCREEN_HEIGHT // 2 - 150
            control_font = pygame.font.Font(None, 40)
            title_text = control_font.render("Управление", True, (255, 255, 255))
            screen.blit(title_text, (SCREEN_WIDTH // 2 - 80, y_offset))
            y_offset += 60

            for control in controls:
                text = font.render(control, True, (255, 255, 255))
                screen.blit(text, (SCREEN_WIDTH // 2 - 100, y_offset))
                y_offset += 40

        # Кнопки управления
        apply_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 200, 160, 40)
        pygame.draw.rect(screen, (0, 255, 0), apply_rect, border_radius=20)
        apply_text = font.render("Применить", True, (0, 0, 0))
        screen.blit(apply_text, apply_text.get_rect(center=apply_rect.center))

        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 250, 160, 40)
        pygame.draw.rect(screen, (255, 0, 0), back_rect, border_radius=20)
        back_text = font.render("Назад", True, (0, 0, 0))
        screen.blit(back_text, back_text.get_rect(center=back_rect.center))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Переключение вкладок
                if tab_audio_rect.collidepoint(mouse_pos):
                    current_tab = 'audio'
                elif tab_controls_rect.collidepoint(mouse_pos):
                    current_tab = 'controls'

                # Обработка для вкладки аудио
                if current_tab == 'audio':
                    # Выбор трека
                    y_offset = SCREEN_HEIGHT // 2 - 50
                    for track_id in tracks.keys():
                        btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 75, y_offset - 15, 150, 30)
                        if btn_rect.collidepoint(mouse_pos):
                            settings['track'] = track_id
                            pygame.mixer.music.load(f'data/{track_id}.mp3')
                            pygame.mixer.music.play(-1)
                            pygame.mixer.music.set_volume(settings['volume'])
                        y_offset += 40

                    # Ползунок громкости
                    if volume_slider_rect.collidepoint(mouse_pos):
                        settings['volume'] = (mouse_pos[0] - volume_slider_rect.x) / volume_slider_rect.width
                        settings['volume'] = max(0, min(1, settings['volume']))
                        pygame.mixer.music.set_volume(settings['volume'])

                # Кнопки управления
                if apply_rect.collidepoint(mouse_pos):
                    save_settings(settings['volume'], settings['track'])
                    return

                if back_rect.collidepoint(mouse_pos):
                    return

            if event.type == pygame.MOUSEMOTION and current_tab == 'audio':
                if event.buttons[0]:  # Перетаскивание ползунка
                    if volume_slider_rect.collidepoint(event.pos):
                        settings['volume'] = (event.pos[0] - volume_slider_rect.x) / volume_slider_rect.width
                        settings['volume'] = max(0, min(1, settings['volume']))
                        pygame.mixer.music.set_volume(settings['volume'])

def show_exit_confirmation(screen):
    font = pygame.font.Font(None, 36)
    confirmation_text = font.render("Вы точно хотите выйти?", True, WHITE)
    confirmation_rect = confirmation_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

    yes_text = font.render("Да", True, (0, 255, 0))
    yes_rect = yes_text.get_rect(center=(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 50))

    no_text = font.render("Нет", True, (255, 0, 0))
    no_rect = no_text.get_rect(center=(SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2 + 50))

    while True:
        screen.fill(BLACK)  # Заливка фона черным цветом
        screen.blit(confirmation_text, confirmation_rect)
        screen.blit(yes_text, yes_rect)
        screen.blit(no_text, no_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True  # Выход из игры
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if yes_rect.collidepoint(mouse_pos):
                    pygame.quit()  # Закрываем игру
                    return  # Выход из игры
                if no_rect.collidepoint(mouse_pos):
                    return False  # Отмена выхода, закрываем окно
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False  # Отмена выхода


def show_start_countdown(screen):
    font = pygame.font.Font(None, 300)
    countdown_numbers = ['SEAL!']

    for number in countdown_numbers:
        start_time = pygame.time.get_ticks()
        alpha = 255  # Начальная непрозрачность
        while pygame.time.get_ticks() - start_time < COUNTDOWN_DURATION:
            # Прозрачность уменьшается от 255 до 0
            alpha = max(0, 255 - int(255 * (pygame.time.get_ticks() - start_time) / COUNTDOWN_DURATION))
            # Очищаем экран
            screen.fill(BLUE)
            # Создаем текст с текущей прозрачностью
            text_surface = font.render(number, True, WHITE)
            text_surface.set_alpha(alpha)
            # Центрируем текст
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_surface, text_rect)
            pygame.display.flip()
            pygame.time.delay(30)

def create_particles(position, penguin):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(2, 10)
    for _ in range(particle_count):
        Particle_Water(position, random.choice(numbers), random.choice(numbers), penguin)

# Основная функция игры
def main():
    init_db()  # Инициализация базы данных
    volume, track = load_settings()  # Загружаем настройки
    pygame.mixer.music.set_volume(volume)  # Установка громкости музыки
    high_score = get_high_score()  # Получаем текущий наивысший балл
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Seal on a Board")
    clock = pygame.time.Clock()
    show_loading_screen(screen)
    show_start_countdown(screen)
    try:
        pygame.mixer.music.load(f'data/{track}.mp3')
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Ошибка загрузки музыки: {e}")

    # Инициализация шрифта
    font = pygame.font.Font(None, 36)  # Создаем объект шрифта

    # Создаем пингвина и добавляем его в группу
    penguin = Penguin(player_sprites)
    water = Water()
    sky = Sky()
    obstacles = []
    score = 0
    lives = 3  # Количество жизней
    move_speed_obstacle = 12  # Скорость движения
    move_speed_penguin = 8
    running = True
    id_obstacle = 0
    old_id = []
    start_time = time.time()
    wave_time = time.time()
    last_obstacle = Wave(id_obstacle, big_wave_image, "big_wave", -SCREEN_HEIGHT, SCREEN_HEIGHT - 275, waves_sprites)
    obstacles.append(last_obstacle)
    add_wave = False
    on_wave = False
    last_seal_spawn_time = pygame.time.get_ticks()  # Время последнего спавна морского котика
    seal_spawn_interval = random.randint(7000, 23000)
    last_bird_spawn_time = pygame.time.get_ticks()  # Время последнего спавна птицы
    bird_spawn_interval = random.randint(10000, 20000)
    water_particle_coefficient = 0.5 + move_speed_penguin // 10  # Коэффициент брызгов зависит от скорости пингвина и от того что он на волне или нет
    distance_traveled = 0

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:  # Проверка на нажатие клавиши
                if event.key == pygame.K_ESCAPE:  # Если нажата клавиша "ESC"
                    action = show_pause_menu(screen)  # Показываем меню паузы
                    if action == "exit":
                        running = False  # Выход из игры
                    elif action == "restart":
                        # Сброс состояния игры
                        player_sprites.empty()
                        waves_sprites.empty()
                        cloud_sprites.empty()
                        bird_sprites.empty()
                        seals_sprites.empty()
                        all_sprites.empty()
                        # Сброс переменных состояния
                        penguin = Penguin(player_sprites)
                        obstacles.clear()
                        score = 0
                        lives = 3
                        move_speed_obstacle = 12
                        move_speed_penguin = 8
                        id_obstacle = 0
                        old_id = []
                        start_time = time.time()
                        wave_time = time.time()
                        # Пересоздание начальной волны
                        last_obstacle = Wave(id_obstacle, big_wave_image, "big_wave", -SCREEN_HEIGHT,
                                             SCREEN_HEIGHT - 275, waves_sprites)
                        obstacles.append(last_obstacle)
                        # Сброс таймеров спавна
                        last_seal_spawn_time = pygame.time.get_ticks()
                        last_bird_spawn_time = pygame.time.get_ticks()
                        distance_traveled = 0
                        volume, track = load_settings()
                        try:
                            pygame.mixer.music.load(f'data/{track}.mp3')
                            pygame.mixer.music.play(-1)
                        except Exception as e:
                            print(f"Ошибка загрузки музыки: {e}")
                        continue

        keys = pygame.key.get_pressed()  # Получаем состояние всех клавиш
        if keys[pygame.K_UP] and not penguin.is_jumping and penguin.current_energy >= 33:  # Прыжок при нажатии пробела
            penguin.is_jumping = True
            penguin.velocity_y = -penguin.jump_height  # Устанавливаем начальную скорость прыжка
            penguin.current_energy -= 33  # Уменьшаем энергию на 33%
        if keys[pygame.K_DOWN]:
            penguin.animated_down()
        else:
            penguin.animated_up()

        # Ограничение движения пингвина, чтобы он не выходил за пределы экрана
        if penguin.rect.x < 0:
            penguin.rect.x = 0
        if penguin.rect.x > SCREEN_WIDTH - penguin.rect.width:
            penguin.rect.x = SCREEN_WIDTH - penguin.rect.width

        end_time = time.time()  # Время сейчас для всех
        wave_end_time = time.time()  # Время сейчас для волны
        elapsed_time = end_time - start_time  # Сколько времени прошло со времени засечки для всех
        wave_elapsed_time = wave_end_time - wave_time  # Сколько времени прошло со времени засечки для волны
        if elapsed_time > 3 and 10 < move_speed_penguin:
            move_speed_penguin -= 2
            move_speed_obstacle += 2
            start_time = time.time()
        elif elapsed_time > 7:
            move_speed_penguin -= 2
            move_speed_obstacle += 2
            start_time = time.time()

        if wave_elapsed_time > 5:
            add_wave = True
            wave_time = time.time()

        # Рассчитываем пройденное расстояние
        distance_traveled += move_speed_penguin / FPS  # Увеличиваем пройденное расстояние на скорость пингвина
        distance_traveled += move_speed_obstacle / FPS  # Увеличиваем пройденное расстояние на скорость волн

        # Отображение расстояния на экране
        distance_text = font.render(f'Distance: {distance_traveled:.1f}m', True, WHITE)
        screen.blit(distance_text, (10, 250))  # Отображаем расстояние ниже других текстов

        # Генерация препятствий с вероятностью 2%
        if random.randint(1, 100) < 2 and last_obstacle.rect.x > 150 and add_wave:
            add_wave = False
            type_wave_num = random.randint(0, 100)
            if type_wave_num <= 12:  # 10% Вероятность
                new_wave = Wave(id_obstacle, big_wave_image, "big_wave", -SCREEN_HEIGHT, SCREEN_HEIGHT - 275, waves_sprites)
                obstacles.append(new_wave)
            elif 11 <= type_wave_num < 100:  # 90% Вероятность
                new_wave = Wave(id_obstacle, small_wave_image, "small_wave", -SCREEN_HEIGHT, SCREEN_HEIGHT - 280, waves_sprites)
                obstacles.append(new_wave)
            last_obstacle = obstacles[-1]
            id_obstacle += 1

        # Генерация птиц с интервалом 20-30 секунд
        current_time = pygame.time.get_ticks()
        if current_time - last_bird_spawn_time > bird_spawn_interval:
            Bird(bird_sprites)  # Спавн новой птицы и добавление в группу
            last_bird_spawn_time = current_time  # Обновляем время последнего спавна
            bird_spawn_interval = random.randint(10000, 20000)

        # Проверка времени для спавна морского котика
        current_time = pygame.time.get_ticks()
        if current_time - last_seal_spawn_time > seal_spawn_interval:
            Seal(seals_sprites)  # Создаем нового морского котика
            last_seal_spawn_time = current_time  # Обновляем время последнего спавна
            seal_spawn_interval = random.randint(7000, 23000)  # Устанавливаем новый интервал

        sky.draw_sky(screen)  # Прорисовываем небо
        sky.draw_cloud(screen)  # Прорисовываем облака
        player_sprites.draw(screen)
        penguin.update() # Обновление состояния пингвина
        waves_sprites.update(move_speed_obstacle)
        waves_sprites.draw(screen)
        bird_sprites.update()  # Обновляем птиц
        seals_sprites.update(move_speed_penguin)  # Обновляем морских котиков, чтобы они плыли за пингвином
        seals_sprites.draw(screen)  # Отрисовываем морских котиков
        bird_sprites.draw(screen)

        draw_energy_bar(screen, penguin)

        # Спавн брызгов вероятность от 5% до 10%
        if random.randint(1, 100) < 10 * water_particle_coefficient:
            create_particles((penguin.rect.x - 10, penguin.rect.y + penguin.rect.width + 10), penguin)

        all_sprites.update()
        all_sprites.draw(screen)

        # Отрисовка препятствий
        for obstacle in waves_sprites:
            if obstacle.rect.x > SCREEN_WIDTH:  # Удаление препятствий, вышедших за экран
                if obstacle in obstacles:
                    obstacles.remove(obstacle)
                waves_sprites.remove(obstacle)
                score += 1

        water.draw(screen)  # Прорисовываем воду

        # Проверка на столкновение с морскими котиками
        for seal in seals_sprites:
            if penguin.rect.colliderect(seal.rect) and not seal.is_damaged:  # Проверяем только неповрежденных котиков
                lives -= 1
                seal.is_damaged = True
                seal.damage_time = pygame.time.get_ticks()  # Запоминаем время получения урона

                # Обновляем отображение жизней
                lives_text = font.render(f'Lives: {lives}', True, WHITE)
                screen.blit(lives_text, (10, 50))
                pygame.display.update()
                if lives <= 0:
                    if show_game_over_screen(screen, score):  # Показываем экран окончания игры
                        # Полный сброс игры
                        player_sprites.empty()
                        waves_sprites.empty()
                        cloud_sprites.empty()
                        bird_sprites.empty()
                        seals_sprites.empty()
                        all_sprites.empty()

                        penguin = Penguin(player_sprites)
                        obstacles.clear()
                        score = 0
                        lives = 3
                        move_speed_obstacle = 12
                        move_speed_penguin = 8
                        id_obstacle = 0
                        old_id = []
                        start_time = time.time()
                        wave_time = time.time()
                        last_obstacle = Wave(id_obstacle, big_wave_image, "big_wave", -SCREEN_HEIGHT,
                                             SCREEN_HEIGHT - 275, waves_sprites)
                        obstacles.append(last_obstacle)
                        last_seal_spawn_time = pygame.time.get_ticks()
                        last_bird_spawn_time = pygame.time.get_ticks()
                        distance_traveled = 0
                        continue
                    else:
                        running = False
                break

        # Проверка на столкновение с птицей
        for bird in bird_sprites:
            if (penguin.rect.x + 50 > bird.rect.x > penguin.rect.x - 50 and  # Проверка по X
                    penguin.rect.y - 50 <= bird.rect.y <= penguin.rect.y + 50):  # Проверка по Y
                if not bird.caught:  # Если птица еще не поймана
                    bird.caught = True  # Устанавливаем состояние пойманной птицы
                    bird.catch_time = pygame.time.get_ticks()  # Запоминаем время захвата
                    penguin.hanging = True  # Устанавливаем состояние зависания пингвина
                    penguin.hang_start_time = pygame.time.get_ticks()  # Запоминаем время начала зависания
                    score += 5  # Увеличиваем счет за схваченную птицу

                # Обновление high_score, если score больше
                if score > high_score:
                    high_score = score  # Обновляем переменную high_score
                    update_high_score(high_score)  # Обновляем наивысший балл в базе данных
                break  # Выходим из цикла, чтобы не обрабатывать другие птицы

        # Проверка на столкновение с волной
        for obstacle in waves_sprites:
            if penguin.rect.colliderect(obstacle.rect):  # Проверка на столкновение
                on_wave = True
                water_particle_coefficient = 1 + move_speed_penguin // 10
                if obstacle.type == "big_wave":
                    if penguin.sit_down and obstacle.id not in old_id:
                        old_id.append(obstacle.id)
                        move_speed_penguin -= 2
                        move_speed_obstacle += 2
                    elif penguin.sit_down:
                        pass
                    else:
                        lives -= 1  # Уменьшаем количество жизней
                        if obstacle in obstacles:
                            obstacles.remove(obstacle)
                        waves_sprites.remove(obstacle)  # Удаляем столкнувшееся препятствие
                        if lives <= 0:  # Если жизни закончились, показываем экран окончания игры
                            if score > high_score:  # Если текущий счет больше наивысшего
                                update_high_score(score)  # Обновляем наивысший балл
                                high_score = score  # Обновляем переменную high_score

                            if show_game_over_screen(screen, score):
                                player_sprites.empty()  # Удаляем старую модельку пингвина
                                penguin = Penguin(player_sprites)  # Создаем новую модельку
                                obstacles.clear()
                                score = 0
                                lives = 3  # Количество жизней
                                move_speed_obstacle = 12  # Скорость движения
                                move_speed_penguin = 8
                                running = True
                                id_obstacle = 0
                                old_id = []
                                start_time = time.time()
                                last_obstacle = Wave(id_obstacle, big_wave_image, "big_wave", -SCREEN_HEIGHT,
                                                     SCREEN_HEIGHT - 300, waves_sprites)
                                obstacles.append(last_obstacle)

                elif obstacle.type == "small_wave":
                    if obstacle.id not in old_id:
                        penguin.animated_kant()
                        old_id.append(obstacle.id)
                        move_speed_penguin += 2
                        move_speed_obstacle -= 2
                        if move_speed_penguin > 10:
                            start_time = time.time()

            else:
                on_wave = False
                water_particle_coefficient = 0.5 + move_speed_penguin // 10

        # Отображение других текстов
        score_text = font.render(f'Score: {score}', True, WHITE)
        lives_text = font.render(f'Lives: {lives}', True, WHITE)
        speed_text = font.render(f'Speed: {move_speed_penguin}', True, WHITE)
        speed_wave_text = font.render(f'Speed wave:{move_speed_obstacle}', True, WHITE)
        time_wave_text = font.render(f'Time:{wave_elapsed_time}', True, WHITE)
        high_score_text = font.render(f'High Score: {high_score}', True, WHITE)  # Отображение наивысшего балла
        help_text = font.render(f'Пока только вниз', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(distance_text, (1050, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(speed_text, (10, 90))
        screen.blit(speed_wave_text, (10, 130))
        screen.blit(time_wave_text, (10, 170))
        screen.blit(high_score_text, (10, 210))  # Отображаем наивысший балл ниже других текстов
        screen.blit(help_text, (950, 50))
        pygame.display.flip()  # Обновляем экран

    pygame.quit()  # Выход из игры


if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    show_start_screen(screen)  # Показать заставку перед началом игры
    main()