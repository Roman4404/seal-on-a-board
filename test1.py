import pygame
import random
import os
import sys

pygame.init()
SCREEN_WIDTH = 860
SCREEN_HEIGHT = 620
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
all_sprites = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

# Загрузка изображений
def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        pygame.quit()
        sys.exit()
    return pygame.image.load(fullname)

penguin_image = load_image('Pingein_player2.png')
cloud_image = load_image('cloud1.png')
water_image = load_image('water_concept.png')
sky_image = load_image('sky_concept2.png')
wave_image = load_image('wave.png')
bird_image = load_image('bird_concept.png')
cloud_y = 200  # Высота облака

# Класс для пингвина
class Penguin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = penguin_image
        self.rect = self.image.get_rect()
        self.rect.x = 50  # Начальная позиция по оси X
        self.start_y = SCREEN_HEIGHT // 2 + 90  # Сохранение начальной позиции по оси Y
        self.rect.y = self.start_y  # Позиция по оси Y
        self.is_jumping = False  # Состояние прыжка
        self.jump_height = 10  # Высота прыжка
        self.jump_count = self.jump_height  # Счетчик прыжка
        self.is_hanging = False  # Состояние "зацепления"
        self.hang_time = 0  # Время, в течение которого пингвин висит
        self.is_moving_with_bird = False  # Состояние перемещения с птицей
        self.move_start_time = 0  # Время начала перемещения с птицей

    def jump(self):
        if self.is_hanging:
            return  # Если пингвин висит, не позволяет прыгать

        if self.is_jumping:
            if self.jump_count >= -self.jump_height:
                neg = 1
                if self.jump_count < 0:
                    neg = -1
                self.rect.y -= (self.jump_count ** 2) * 0.5 * neg  # Парабола прыжка
                self.jump_count -= 1
            else:
                self.is_jumping = False
                self.jump_count = self.jump_height
                self.rect.y = self.start_y  # Возвращаем на начальную высоту после прыжка

    def hang(self):
        self.is_hanging = True
        self.hang_time = pygame.time.get_ticks()  # Запоминаем текущее время

    def update(self):
        if self.is_hanging:
            # Проверяем, прошло ли 2 секунды (2000 мс)
            if pygame.time.get_ticks() - self.hang_time >= 2000:
                self.is_hanging = False  # Сбрасываем состояние "зацепления"
        self.jump()  # Обновляем состояние прыжка

        if self.is_moving_with_bird:
            current_time = pygame.time.get_ticks()
            if current_time - self.move_start_time < 2000:  # Проверка на 2 секунды
                self.rect.x -= 5  # Движение вместе с птицей влево
            else:
                self.is_moving_with_bird = False  # Сбрасываем состояние
                self.rect.y = self.start_y  # Приземление пингвина

# Класс для волн
class Wave(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(obstacle_group, all_sprites)
        self.image = wave_image
        self.rect = self.image.get_rect()
        self.rect.x = -self.rect.width  # Начальная позиция волны (за левым краем экрана)
        self.rect.y = SCREEN_HEIGHT - 240  # Положение волны

    def update(self):
        self.rect.x += 5  # Движение волны вправо
        if self.rect.x > SCREEN_WIDTH:  # Удаление волны, вышедшей за экран
            self.kill()

class Water:
    def draw(self, screen):
        for x in range(0, SCREEN_WIDTH, 96):
            screen.blit(water_image, (x, SCREEN_HEIGHT - 80))

class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = cloud_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = cloud_y - 100  # Положение облака

    def update(self):
        self.rect.x -= 2  # Движение облака влево
        if self.rect.x < -self.rect.width:  # Удаление облака, вышедшего за экран
            self.kill()

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(bird_group, all_sprites)
        self.image = bird_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH  # Начальная позиция по оси X
        self.rect.y = cloud_y

    def update(self):
        self.rect.x -= 5  # Движение птицы влево
        if self.rect.x < -self.rect.width:  # Удаление птицы, вышедшей за экран
            self.kill()

# Занимается небом
class Sky:
    def draw_sky(self, screen):
        for x in range(0, SCREEN_WIDTH, 512):
            screen.blit(sky_image, (x, 0))

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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return  # Запускаем основную игру
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
                    all_sprites.empty()  # Очищаем все спрайты
                    obstacle_group.empty()  # Очищаем препятствия
                    bird_group.empty()  # Очищаем птиц
                    return True
                if event.key == pygame.K_q:  # Выход из игры
                    pygame.quit()
                    return

# Основная функция игры
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Seal on a Board")
    clock = pygame.time.Clock()

    penguin = Penguin()
    water = Water()
    sky = Sky()
    score = 0
    lives = 3  # Количество жизней
    running = True
    last_bird_spawn_time = pygame.time.get_ticks()  # Время последнего спавна птицы
    bird_spawn_interval = random.randint(10000, 20000)
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()  # Получаем состояние всех клавиш
        if keys[pygame.K_RIGHT]:  # Движение пингвина вправо
            penguin.rect.x += 5
        if keys[pygame.K_LEFT]:  # Движение пингвина влево
            penguin.rect.x -= 5
        if keys[pygame.K_UP] and not penguin.is_jumping:  # Прыжок при нажатии пробела
            penguin.is_jumping = True

        # Ограничение движения пингвина, чтобы он не выходил за пределы экрана
        if penguin.rect.x < 0:
            penguin.rect.x = 0
        if penguin.rect.x > SCREEN_WIDTH - penguin.rect.width:
            penguin.rect.x = SCREEN_WIDTH - penguin.rect.width

        # Генерация птиц с интервалом 20-30 секунд
        current_time = pygame.time.get_ticks()
        if current_time - last_bird_spawn_time > bird_spawn_interval:
            Bird()  # Спавн новой птицы
            last_bird_spawn_time = current_time  # Обновляем время последнего спавна
            bird_spawn_interval = random.randint(10000, 20000)

        # Генерация волн с вероятностью 2%
        if random.randint(1, 100) < 2:
            Wave()

        # Генерация облаков с вероятностью 1%
        if random.randint(1, 100) < 2:
            Cloud()

        sky.draw_sky(screen)  # Прорисовываем небо
        water.draw (screen)  # Прорисовываем воду

        # Обновление и отрисовка всех спрайтов
        all_sprites.update()
        all_sprites.draw(screen)

        # Проверка на столкновение с волной
        for obstacle in obstacle_group:
            if obstacle.rect.colliderect(penguin.rect):  # Проверка на столкновение
                lives -= 1  # Уменьшаем количество жизней
                obstacle.kill()  # Удаляем столкнувшееся препятствие
                if lives <= 0:  # Если жизни закончились, показываем экран окончания игры
                    if show_game_over_screen(screen, score):
                        penguin = Penguin()  # Перезапускаем игру
                        score = 0  # Сбрасываем счет
                        lives = 3

        # Проверка на столкновение с птицей
        for bird in bird_group:
            if (penguin.rect.x + 50 > bird.rect.x > penguin.rect.x - 50 and  # Проверка по X
                    penguin.rect.y - 50 <= bird.rect.y <= penguin.rect.y + 50):  # Проверка по Y
                bird.kill()  # Удаляем схваченную птицу
                score += 5  # Увеличиваем счет за схваченную птицу
                penguin.is_moving_with_bird = True  # Устанавливаем состояние перемещения с птицей
                penguin.move_start_time = pygame.time.get_ticks()  # Запоминаем время начала перемещения
                break  # Выходим из цикла, чтобы не обрабатывать другие птицы

        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        lives_text = font.render(f'Lives: {lives}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        pygame.display.flip()  # Обновляем экран

    pygame.quit()  # Выход из игры

if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Создаем экран перед вызовом заставки
    show_start_screen(screen)  # Показать заставку перед началом игры
    main()  # Запуск основной игры