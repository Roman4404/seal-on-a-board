from tokenize import group

import pygame
import random
import os
import time

pygame.init()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
screen_rect = (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

# Загрузка изображений
penguin_image = pygame.image.load('data/Pingein_player2.png')
penguin_down_image = pygame.image.load('data/Pingein_concept2_animated _down_player.png')
cloud_image = pygame.image.load('data/cloud1.png')
water_image = pygame.image.load('data/water_concept.png')
water_animated_image = pygame.image.load('data/water_animated.png')
sky_image = pygame.image.load('data/sky_concept2.png')
big_wave_image = pygame.image.load('data/wave.png')
small_wave_image = pygame.image.load('data/small_wave.png')
down_kant_image = pygame.image.load('data/Pingein_concept_animated_down_kant_player.png')

# Группы спрайтов
all_sprites = pygame.sprite.Group()
player_sprites = pygame.sprite.Group()
waves_sprites = pygame.sprite.Group()
cloud_sprites = pygame.sprite.Group()

# Класс для пингвина
class Penguin(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group) # Вызываем конструктор родительского класса
        self.image = penguin_image # Изображение пингвина
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 - 100 # Начальная позиция по оси X
        self.rect.y = SCREEN_HEIGHT // 2 + 115  # Позиция по оси Y
        self.sit_down = False # В присади ли пингвин

    # Анимация приседа пингвина
    def animated_down(self):
        self.image = penguin_down_image # Обновления изображения "Анимация"
        self.sit_down = True # Пингвин в присади

    # Анимация поднятия пингвина
    def animated_up(self):
        self.image = penguin_image # Обновления изображения "Анимация"
        self.sit_down = False # Пингвин не в присади

    # Анимация канта пингвина
    def animated_kant(self):
        self.image = down_kant_image

    # Обновление местоположения пингвина
    def update(self):
        self.rect = self.rect.move(0, 0)

# Класс для препятствий
class Wave(pygame.sprite.Sprite):
    def __init__(self, id_obstacle, image, type_wave, x=-SCREEN_WIDTH, y=SCREEN_HEIGHT - 300, *group):
        super().__init__(*group)
        self.image = image # Изображение воды
        self.rect = self.image.get_rect()
        self.rect.x = x  # Начальная позиция волны (за левым краем экрана)
        self.rect.y = y  # Положение препятствия
        self.id = id_obstacle # Id волны нужно для ее отслеживания
        self.type = type_wave # Маленькая волна = "small_wave", Большая волна = "big_wave"

    # Обновление местоположения волны
    def update(self, speed):
        self.rect = self.rect.move(speed, 0)  # Движение препятствия вправо


# Класс для воды
class Water:
    def __init__(self):
        self.image = pygame.transform.scale(water_image, (96 * 1.5, 96 * 1.5)) # Изображение волны

    #Прорисовка ибо не спрайт
    def draw(self, screen):
        for x in range(0, 1280, 96):
            screen.blit(self.image, (x, SCREEN_HEIGHT - 96))

# Класс под облако
class Cloud(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = cloud_image # Изображение
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - 500  # Положение препятствия

    # Обновление местоположения
    def update(self, speed):
        self.rect = self.rect.move(-speed, 0)

# Занимается небом
class Sky:
    def __init__(self):
        self.image = pygame.transform.scale(sky_image, (540 * 1.5, 540 * 1.5)) # Изображение
        self.clouds = [] # Облака

    # Прорисовка неба
    def draw_sky(self, screen):
        for x in range(0, 1280, 512):
            screen.blit(self.image, (x, 0))

    # Прорисовка облаков
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
    # сгенерируем частицы разного размера
    fire = [pygame.image.load("data/water_particle.png")] # Исходное размер текстуры
    # Разные размер текстур
    for scale in (3, 6, 9):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy, penguin):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire) # Изображение
        self.rect = self.image.get_rect() # Размеры
        self.penguin = penguin # Пингвин (нужен для получения координат)

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = -0.4

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x -= self.velocity[0]
        self.rect.y += self.velocity[1]

        # убиваем, если частица ушла за экран
        if not self.rect.colliderect((self.penguin.rect.x - self.penguin.rect.width, self.penguin.rect.y + 110, self.penguin.rect.x, self.penguin.rect.y)):
            self.kill()


# Функция для отображения заставки
def show_start_screen(screen):
    font = pygame.font.Font(None, 74)
    title_text = font.render("Seal on a Board", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

    font_small = pygame.font.Font(None, 36)
    play_text = font_small.render("Press P to Play", True, WHITE)
    play_rect = play_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    exit_text = font_small.render("Press Q to Quit", True, WHITE)
    exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    while True:
        screen.fill(BLUE)
        screen.blit(title_text, title_rect)
        screen.blit(play_text, play_rect)
        screen.blit(exit_text, exit_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event .type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return  # Запускаем основную игру
                if event.key == pygame.K_q:  # Выход из игры
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

    restart_text = font_small.render("Press R to Restart or Q to Quit", True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    while True:
        screen.fill(BLUE)
        screen.blit(text, text_rect)
        screen.blit(score_text, score_rect)
        screen.blit(restart_text, restart_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Перезапуск игры
                    return True
                if event.key == pygame.K_q:  # Выход из игры
                    pygame.quit()
                    return

def create_particles(position, penguin):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(2, 10)
    for _ in range(particle_count):
        Particle_Water(position, random.choice(numbers), random.choice(numbers), penguin)

# Основная функция игры
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Экран
    pygame.display.set_caption("Seal on a Board")
    clock = pygame.time.Clock()

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
    start_time = time.time() # Начало отсчета
    wave_time = time.time() # Время для спавна волн
    last_obstacle = Wave(id_obstacle, big_wave_image, "big_wave", -SCREEN_HEIGHT, SCREEN_HEIGHT - 300, waves_sprites) # Первая начинающая волна
    obstacles.append(last_obstacle) # Список волн
    add_wave = False # Можно ли создавать новую волну
    on_wave = False # На волне ли пингвин
    water_particle_coefficient = 0.5 + move_speed_penguin // 10
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()  # Получаем состояние всех клавиш
        # if keys[pygame.K_RIGHT]:  # Движение пингвина вправо
        #     penguin.rect.x += move_speed_penguin
        # if keys[pygame.K_LEFT]:  # Движение пингвина влево
        #     penguin.rect.x -= move_speed_penguin
        if keys[pygame.K_DOWN]:
            penguin.animated_down() # Пингвин присаживается
        elif not on_wave:
            penguin.animated_up() # Пингвин поднимается

        # Ограничение движения пингвина, чтобы он не выходил за пределы экрана
        if penguin.rect.x < 0:
            penguin.rect.x = 0
        if penguin.rect.x > SCREEN_WIDTH - penguin.rect.width:
            penguin.rect.x = SCREEN_WIDTH - penguin.rect.width

        end_time = time.time() # Время сейчас для всех
        wave_end_time = time.time() # Время сейчас для волны
        elapsed_time = end_time - start_time # Сколько времени прошло со времени засечки для всех
        wave_elapsed_time = wave_end_time - wave_time # Сколько времени прошло со времени засечки для волны
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


        # Генерация препятствий с вероятностью 2%
        if add_wave and random.randint(1, 100) < 2 and last_obstacle.rect.x > 150:
            add_wave = False
            type_wave_num = random.randint(0, 100)
            print(type_wave_num)
            if type_wave_num <= 10: #10% Вероятность
                obstacles.append(Wave(id_obstacle, big_wave_image, "big_wave", -SCREEN_HEIGHT, SCREEN_HEIGHT - 300, waves_sprites))
            elif 11 <= type_wave_num < 100: #90% Вероятность
                obstacles.append(Wave(id_obstacle, small_wave_image, "small_wave", -SCREEN_HEIGHT, SCREEN_HEIGHT - 280, waves_sprites))
            last_obstacle = obstacles[-1]
            id_obstacle += 1

        sky.draw_sky(screen)  # Прорисовываем небо
        sky.draw_cloud(screen)  # Прорисовываем облака
        player_sprites.draw(screen) # Прорисовываем игрока
        waves_sprites.update(move_speed_obstacle) # Волны местоположения
        waves_sprites.draw(screen) # Прорисовываем волны
        all_sprites.update() # Местоположение всех спрайтов
        all_sprites.draw(screen) # Прорисовываем все спрайты

        # Спавн брызгов вероятность от 5% до 10%
        if random.randint(1, 100) < 10 * water_particle_coefficient:
            create_particles((penguin.rect.x - 10, penguin.rect.y + penguin.rect.width + 10), penguin)

        # Отрисовка препятствий
        for obstacle in waves_sprites:
            if obstacle.rect.x > SCREEN_WIDTH:  # Удаление препятствий, вышедших за экран
                obstacles.remove(obstacle)
                waves_sprites.remove(obstacle)
                score += 1

        water.draw(screen)  # Прорисовываем воду

        # Проверка на столкновение с волной
        for obstacle in waves_sprites:
            if penguin.rect.colliderect(obstacle.rect):# Проверка на столкновение
                on_wave = True
                water_particle_coefficient = 1 + move_speed_penguin // 10
                if obstacle.type == "big_wave":
                    if penguin.sit_down and obstacle.id not in old_id:
                        old_id.append(obstacle.id)
                        move_speed_penguin -= 2 # Вчитаем скорость из скорости пингвина
                        move_speed_obstacle += 2 # Прибавляем скорость из скорости волны
                    elif penguin.sit_down: # Вприсяди ли пингвин
                        pass
                    else:
                        lives -= 1  # Уменьшаем количество жизней
                        obstacles.remove(obstacle)
                        waves_sprites.remove(obstacle)# Удаляем столкнувшееся препятствие
                        if lives <= 0:  # Если жизни закончились, показываем экран окончания игры
                            if show_game_over_screen(screen, score):
                                player_sprites.remove(penguin)
                                penguin = Penguin(player_sprites)  # Перезапускаем игру
                                obstacles.clear()
                                score = 0
                                lives = 3  # Количество жизней
                                move_speed_obstacle = 12  # Скорость движения
                                move_speed_penguin = 8
                                running = True
                                id_obstacle = 0
                                old_id = []
                                start_time = time.time()
                                last_obstacle = Wave(id_obstacle, big_wave_image, "big_wave", -SCREEN_HEIGHT,SCREEN_HEIGHT - 300, waves_sprites)
                                obstacles.append(last_obstacle)

                elif obstacle.type == "small_wave":
                    if obstacle.id not in old_id:
                        penguin.animated_kant()
                        old_id.append(obstacle.id)
                        move_speed_penguin += 2 # Прибавляем скорость из скорости пингвина
                        move_speed_obstacle -= 2 # Вчитаем скорость из скорости волны
                        if move_speed_penguin > 10:
                            start_time = time.time()

            else:
                on_wave = False # Не на волне
                water_particle_coefficient = 0.5


        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        lives_text = font.render(f'Lives: {lives}', True, WHITE)
        speed_text = font.render(f'Speed: {move_speed_penguin}', True, WHITE)
        speed_wave_text = font.render(f'Speed wave:{move_speed_obstacle}', True, WHITE)
        time_text = font.render(f'Time:{str(elapsed_time)}', True, WHITE)
        help_text = font.render(f'Пока только вниз', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(speed_text, (10, 90))
        screen.blit(speed_wave_text, (10, 130))
        screen.blit(time_text, (10, 170))
        screen.blit(help_text, (950, 50))
        pygame.display.flip()  # Обновляем экран

    pygame.quit()  # Выход из игры

if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    show_start_screen(screen)  # Показать заставку перед началом игры
    main()  # Запуск основной игры