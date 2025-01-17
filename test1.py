import pygame
import random
import os

pygame.init()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Загрузка изображений
penguin_image = pygame.image.load('data/Pingein_player2.png')
penguin_down_image = pygame.image.load('data/Pingein_concept2_animated _down_player.png')
cloud_image = pygame.image.load('data/cloud1.png')
water_image = pygame.image.load('data/water_concept.png')
sky_image = pygame.image.load('data/sky_concept2.png')
wave_image = pygame.image.load('data/wave.png')


# Класс для пингвина
class Penguin:
    def __init__(self):
        self.image = penguin_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 - 100 # Начальная позиция по оси X
        self.rect.y = SCREEN_HEIGHT // 2 + 115  # Позиция по оси Y
        self.sit_down = False

    def draw(self, screen, offset):
        # Отрисовываем пингвина с учетом смещения
        screen.blit(self.image, (self.rect.x + offset, self.rect.y))

    def animated_down(self):
        self.image = penguin_down_image
        self.sit_down = True

    def animated_up(self):
        self.image = penguin_image
        self.sit_down = False


# Класс для препятствий
class Obstacle:
    def __init__(self, id_obstacle):
        self.image = wave_image
        self.rect = self.image.get_rect()
        self.rect.x = -SCREEN_WIDTH  # Начальная позиция волны (за левым краем экрана)
        self.rect.y = SCREEN_HEIGHT - 300  # Положение препятствия
        self.id = id_obstacle

    def move(self, speed):
        self.rect.x += speed  # Движение препятствия вправо

    def draw(self, screen, offset):
        # Отрисовываем препятствие с учетом смещения
        screen.blit(self.image, (self.rect.x + offset, self.rect.y))

class Water:
    def __init__(self):
        self.image = pygame.transform.scale(water_image, (96 * 1.5, 96 * 1.5))

    def draw(self, screen):
        for x in range(0, 1280, 96):
            screen.blit(self.image, (x, SCREEN_HEIGHT - 96))

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

# Основная функция игры
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Seal on a Board")
    clock = pygame.time.Clock()

    penguin = Penguin()
    water = Water()
    sky = Sky()
    obstacles = []
    score = 0
    lives = 3  # Количество жизней
    move_speed_obstacle = 10  # Скорость движения
    move_speed_penguin = 5
    running = True
    id_obstacle = 0
    old_id = []
    last_obstacle = Obstacle(id_obstacle)
    obstacles.append(last_obstacle)
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
            penguin.animated_down()
        if keys[pygame.K_UP]:
            penguin.animated_up()

        # Ограничение движения пингвина, чтобы он не выходил за пределы экрана
        if penguin.rect.x < 0:
            penguin.rect.x = 0
        if penguin.rect.x > SCREEN_WIDTH - penguin.rect.width:
            penguin.rect.x = SCREEN_WIDTH - penguin.rect.width

        # Генерация препятствий с вероятностью 2%
        if random.randint(1, 100) < 2 and last_obstacle.rect.x > 150:
            obstacles.append(Obstacle(id_obstacle))
            last_obstacle = obstacles[-1]
            id_obstacle += 1

        sky.draw_sky(screen)  # Прорисовываем небо
        sky.draw_cloud(screen)  # Прорисовываем облака
        penguin.draw(screen, 0)  # Отрисовываем пингвина без смещения

        # if not wave_on_penguin and add_speed:
        #     move_speed_penguin += 1
        #     move_speed_obstacle -= move_speed_penguin
        #     add_speed = False
        # elif wave_on_penguin:
        #     add_speed = True

        # Отрисовка препятствий
        for obstacle in obstacles:
            obstacle.move(move_speed_obstacle)  # Двигаем препятствия влево
            obstacle.draw(screen, 0)  # Отрисовываем препятствия без смещения

            if obstacle.rect.x > SCREEN_WIDTH:  # Удаление препятствий, вышедших за экран
                obstacles.remove(obstacle)
                score += 1

        water.draw(screen)  # Прорисовываем воду

        # Проверка на столкновение с волной
        for obstacle in obstacles:
            if penguin.rect.colliderect(obstacle.rect):# Проверка на столкновение
                if penguin.sit_down and obstacle.id not in old_id:
                    old_id.append(obstacle.id)
                    move_speed_penguin -= 1
                    move_speed_obstacle += 1
                elif penguin.sit_down:
                    pass
                else:
                    lives -= 1  # Уменьшаем количество жизней
                    obstacles.remove(obstacle)  # Удаляем столкнувшееся препятствие
                    if lives <= 0:  # Если жизни закончились, показываем экран окончания игры
                        if show_game_over_screen(screen, score):
                            penguin = Penguin()  # Перезапускаем игру
                            obstacles.clear()  # Очищаем препятствия
                            score = 0  # Сбрасываем счет
                            lives = 3

        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        lives_text = font.render(f'Lives: {lives}', True, WHITE)
        speed_text = font.render(f'Speed: {move_speed_penguin}', True, WHITE)
        help_text = font.render(f'Пока только вниз', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(speed_text, (10, 90))
        screen.blit(help_text, (950, 50))
        pygame.display.flip()  # Обновляем экран

    pygame.quit()  # Выход из игры

if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    show_start_screen(screen)  # Показать заставку перед началом игры
    main()  # Запуск основной игры