import pygame
import random

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Загрузка изображений
penguin_image = pygame.image.load('data/Pingein_player2.png')
obstacle_image = pygame.image.load('data/cloud1.png')
water_image = pygame.image.load('data/water_concept.png')
sky_image = pygame.image.load('data/sky_concept2.png')
wave_image = pygame.image.load('data/wave.png')

# Класс для пингвина
class Penguin:
    def __init__(self):
        self.image = penguin_image
        self.rect = self.image.get_rect()
        self.rect.x = 50  # Начальная позиция по оси X
        self.rect.y = SCREEN_HEIGHT // 2 + 90  # Позиция по оси Y

    def draw(self, screen, offset):
        # Отрисовываем пингвина с учетом смещения
        screen.blit(self.image, (self.rect.x + offset, self.rect.y))

# Класс для препятствий
class Obstacle:
    def __init__(self):
        self.image = wave_image
        self.rect = self.image.get_rect()
        self.rect.x = -100
        self.rect.y = SCREEN_HEIGHT - 240  # Положение препятствия

    def move(self, speed):
        self.rect.x += speed  # Движение препятствия влево

    def draw(self, screen, offset):
        # Отрисовываем препятствие с учетом смещения
        screen.blit(self.image, (self.rect.x + offset, self.rect.y))


class Water:
    def draw(self, screen):
        for x in range(0, 800, 96):
            screen.blit(water_image, (x, 540))


class Cloud:
    def __init__(self):
        self.image = obstacle_image
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
    move_speed = 5  # Скорость движения
    offset = 0  # Смещение для движения игрового поля
    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()  # Получаем состояние всех клавиш
        if keys[pygame.K_RIGHT]:  # Движение игрового поля вперед
            offset += move_speed  # Уменьшаем смещение
        if keys[pygame.K_LEFT]:  # Движение игрового поля назад
            offset -= move_speed  # Увеличиваем смещение

        # Ограничение смещения, чтобы пингвин не выходил за пределы экрана
        if penguin.rect.x + offset < 0:
            offset = -penguin.rect.x  # Не даем пингвину выйти за левую границу
        if penguin.rect.x + offset > SCREEN_WIDTH - penguin.rect.width:
            offset = SCREEN_WIDTH - penguin.rect.width - penguin.rect.x  # Не даем пингвину выйти за правую границу

        # Генерация препятствий с вероятностью 2%
        if random.randint(1, 100) < 2:
            obstacles.append(Obstacle())

        sky.draw_sky(screen) #Прорисовываем небо
        sky.draw_cloud(screen) #Прорисовываем облака

        # Отрисовка препятствий
        for obstacle in obstacles:
            obstacle.move(5)  # Двигаем препятствия влево
            obstacle.draw(screen, 0)  # Отрисовываем препятствия с учетом смещения
            if obstacle.rect.x > SCREEN_WIDTH:  # Удаление препятствий, вышедших за экран
                obstacles.remove(obstacle)
                score += 1

        water.draw(screen) #Прорисовываем воду
        penguin.draw(screen, offset)  # Отрисовываем пингвина с учетом смещения
        # Проверка на столкновение
        for obstacle in obstacles:
            if penguin.rect.x == obstacle.rect.x:
                print(penguin.rect.x, obstacle.rect.x)
                lives -= 1  # Уменьшаем количество жизней
                obstacles.remove(obstacle)  # Удаляем столкнувшееся препятствие
                if lives <= 0:  # Если жизни закончились, показываем экран окончания игры
                    if show_game_over_screen(screen, score):
                        penguin = Penguin()  # Перезапускаем игру
                        obstacles.clear()  # Очищаем препятствия
                        score = 0  # Сбрасываем счет
                        lives = 3  # Восстанавливаем жизни
        # Отображение счета и жизней
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        lives_text = font.render(f'Lives: {lives}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        pygame.display.flip()  # Обновляем экран

    pygame.quit()  # Выход из игры

if __name__ == "__main__":
    main()