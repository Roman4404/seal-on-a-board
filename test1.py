import pygame
import random

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Загрузка изображений
penguin_image = pygame.image.load('data/Pingein_player.png')
obstacle_image = pygame.image.load('data/cloud1.png')

# Класс для пингвина
class Penguin:
    def __init__(self):
        self.image = penguin_image
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT // 2
        self.jump_height = 10
        self.is_jumping = False
        self.jump_count = 10
        self.old_pos = 0

    # def jump(self):
    #
    #     if not self.is_jumping:
    #         self.is_jumping = True
    #     a = self.rect.y
    #     self.rect.y += 1
    #     while a != self.rect.y:
    #         print(self.rect.y)
    #         if self.is_jumping:
    #             if self.jump_count >= -10:
    #                 neg = 1
    #                 if self.jump_count < 0:
    #                     neg = -1
    #                 self.rect.y -= (self.jump_count ** 2) * 0.5 * neg
    #                 self.jump_count -= 1
    #             else:
    #                 self.is_jumping = False
    #                 self.jump_count = 10

    def jump(self):
        if not self.is_jumping:
            self.old_pos = self.rect.y
            self.rect.y -= 200
            self.is_jumping = True
        else:
            self.rect.y += 5
        if self.rect.y == self.old_pos:
            self.is_jumping = False
            return True


    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Класс для препятствий
class Obstacle:
    def __init__(self):
        self.image = obstacle_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - 100  # Положение препятствия

    def move(self):
        self.rect.x -= 5  # Движение препятствия влево

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Основная функция игры
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Seal on a Board")
    clock = pygame.time.Clock()

    penguin = Penguin()
    obstacles = []
    score = 0
    is_jumping = False

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(BLUE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  # Прыжок по нажатию стрелки вверх
                    is_jumping = True

        if is_jumping:
            if penguin.jump():
                is_jumping = False

        # Генерация препятствий с вероятностью 2%
        if random.randint(1, 100) < 2:
            obstacles.append(Obstacle())

        # Движение и отрисовка препятствий
        for obstacle in obstacles:
            obstacle.move()
            obstacle.draw(screen)
            if obstacle.rect.x < 0:  # Удаление препятствий, вышедших за экран
                obstacles.remove(obstacle)
                score += 1

        # Обработка изображения пингвина
        penguin.draw(screen)

        # Проверка на столкновение
        for obstacle in obstacles:
            if penguin.rect.colliderect(obstacle.rect):
                running = False  # Конец игры при столкновении

        # Отображение счета
        font = pygame.font.Font(None, 36)
        text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(text, (10, 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()