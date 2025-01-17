import pygame
import random
import os

pygame.init()
SCREEN_WIDTH = 860
SCREEN_HEIGHT = 620
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
all_sprites = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

# Загрузка изображений
penguin_image = pygame.image.load('data/Pingein_player2.png')
cloud_image = pygame.image.load('data/cloud1.png')
water_image = pygame.image.load('data/water_concept.png')
sky_image = pygame.image.load('data/sky_concept2.png')
wave_image = pygame.image.load('data/wave.png')
bird_image = pygame.image.load('data/bird_concept.png')

# Класс для пингвина
class Penguin:
    def __init__(self):
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

    def draw(self, screen, offset):
        # Отрисовываем пингвина с учетом смещения
        screen.blit(self.image, (self.rect.x + offset, self.rect.y))

# Класс для препятствий
class Obstacle:
    def __init__(self):
        self.image = wave_image
        self.rect = self.image.get_rect()
        self.rect.x = -SCREEN_WIDTH  # Начальная позиция волны (за левым краем экрана)
        self.rect.y = SCREEN_HEIGHT - 240  # Положение препятствия

    def move(self, speed):
        self.rect.x += speed  # Движение препятствия вправо

    def draw(self, screen, offset):
        # Отрисовываем препятствие с учетом смещения
        screen.blit(self.image, (self.rect.x + offset, self.rect.y))

class Water:
    def draw(self, screen):
        for x in range(0, 800, 96):
            screen.blit(water_image, (x, 540))

class Cloud:
    def __init__(self):
        self.image = cloud_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - 500  # Положение препятствия

    def move(self, speed):
        self.rect.x -= speed  # Движение препятствия влево

    def draw(self, screen, offset):
        # Отрисовываем препятствие с учетом смещения
        screen.blit(self.image, (self.rect.x + offset, self.rect.y))

class Bird(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(bird_group, all_sprites)
        self.image = bird_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = random.randint(50, 150)  # Положение птицы

    def update(self, speed):
        self.rect.x -= speed  # Движениептицы влево

# Занимается небом
class Sky:
    def __init__(self):
        self.clouds = []

    def draw_sky(self, screen):
        for x in range(0, 800, 512):
            screen.blit(sky_image, (x, 0))

    def draw_cloud(self, screen):
        if random.randint(1, 100) < 2 and len(self.clouds) < 4:
            self.clouds.append(Cloud())

        for cloud in self.clouds:
            cloud.move(5)  # Двигаем препятствия влево
            cloud.draw(screen, 0)  # Отрисовываем препятствия с учетом смещения
            if cloud.rect.x < 0:  # Удаление облака, вышедших за экран
                self.clouds.remove(cloud)

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
                if event.key == pygame.K_p:  return  # Запускаем основную игру
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

# Основная функция игры
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Seal on a Board")
    clock = pygame.time.Clock()

    penguin = Penguin()
    water = Water()
    sky = Sky()
    obstacles = []
    birds = []
    score = 0
    lives = 3  # Количество жизней
    move_speed = 5  # Скорость движения
    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()  # Получаем состояние всех клавиш
        if keys[pygame.K_RIGHT]:  # Движение пингвина вправо
            penguin.rect.x += move_speed
        if keys[pygame.K_LEFT]:  # Движение пингвина влево
            penguin.rect.x -= move_speed
        if keys[pygame.K_UP] and not penguin.is_jumping:  # Прыжок при нажатии пробела
            penguin.is_jumping = True

        # Ограничение движения пингвина, чтобы он не выходил за пределы экрана
        if penguin.rect.x < 0:
            penguin.rect.x = 0
        if penguin.rect.x > SCREEN_WIDTH - penguin.rect.width:
            penguin.rect.x = SCREEN_WIDTH - penguin.rect.width

        # Генерация препятствий с вероятностью 2%
        if random.randint(1, 100) < 2:
            obstacles.append(Obstacle())

        # Генерация птиц с вероятностью 1%
        if random.randint(1, 100) < 1:  # Измените вероятность по желанию
            birds.append(Bird())

        sky.draw_sky(screen)  # Прорисовываем небо
        sky.draw_cloud(screen)  # Прорисовываем облака

        # Отрисовка препятствий
        for obstacle in obstacles:
            obstacle.move(move_speed)  # Двигаем препятствия влево
            obstacle.draw(screen, 0)  # Отрисовываем препятствия без смещения

            if obstacle.rect.x > SCREEN_WIDTH:  # Удаление препятствий, вышедших за экран
                obstacles.remove(obstacle)
                score += 1

        # Отрисовка птиц
        for bird in birds:
            bird.move(move_speed)  # Двигаем птиц влево
            bird.draw(screen, 0)  # Отрисовываем птиц без смещения

            if bird.rect.x < 0:  # Удаление птиц, вышедших за экран
                birds.remove(bird)

        water.draw(screen)  # Прорисовываем воду
        penguin.jump()  # Обновляем состояние прыжка пингвина
        penguin.draw(screen, 0)  # Отрисовываем пингвина без смещения

        # Проверка на столкновение с волной
        for obstacle in obstacles:
            if obstacle.rect.colliderect(penguin.rect):  # Проверка на столкновение
                lives -= 1  # Уменьшаем количество жизней
                obstacles.remove(obstacle)  # Удаляем столкнувшееся препятствие
                if lives <= 0:  # Если жизни закончились, показываем экран окончания игры
                    if show_game_over_screen(screen, score):
                        penguin = Penguin()  # Перезапускаем игру
                        obstacles.clear()  # Очищаем препятствия
                        birds.clear()  # Очищаем птиц
                        score = 0  # Сбрасываем счет
                        lives = 3

        for bird in birds:
            if (penguin.rect.x + 50 > bird.rect.x > penguin.rect.x - 50 and  # Проверка по X
                    penguin.rect.y - 50 <= bird.rect.y <= penguin.rect.y + 50):  # Проверка по Y
                birds.remove(bird)  # Удаляем схваченную птицу
                score += 5  # Увеличиваем счет за схваченную птицу

        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        lives_text = font.render(f'Lives: {lives}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        pygame.display.flip()  # Обновляем экран

    pygame.quit()  # Выход из игры

if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    show_start_screen(screen)  # Показать заставку перед началом игры
    main()  # Запуск основной игры