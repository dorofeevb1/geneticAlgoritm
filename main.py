import pygame
import sys
import random
import math

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CIRCLE_RADIUS = 20
POPULATION_SIZE = 10
MUTATION_RATE = 0.1
INITIAL_GREEN_CIRCLES = 20
INITIAL_HP = 100
EATEN_HP_BONUS = 100
HP_REDUCTION_PER_MOVE = 5
MOVEMENT_COST = 5  # HP, потерянные за каждое движение
TARGET_GREEN_CIRCLE_COUNT = 10
MAX_HP_VALUE = 10000
# Класс для представления кружков
class Circle:
    def __init__(self, x, y, color, hp):
        self.x = x
        self.y = y
        self.color = color
        self.hp = hp

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), CIRCLE_RADIUS)
        font = pygame.font.Font(None, 24)
        hp_text = font.render(str(self.hp), True, (0, 0, 0))
        screen.blit(hp_text, (self.x - CIRCLE_RADIUS, self.y + CIRCLE_RADIUS + 5))

    def distance(self, other_circle):
        return math.sqrt((self.x - other_circle.x)**2 + (self.y - other_circle.y)**2)

    def move(self, new_x, new_y):
        # Проверка на выход за пределы окна
        self.x = max(CIRCLE_RADIUS, min(new_x, WIDTH - CIRCLE_RADIUS))
        self.y = max(CIRCLE_RADIUS, min(new_y, HEIGHT - CIRCLE_RADIUS))
        self.hp -= MOVEMENT_COST
        if self.hp <= 0:
            self.hp = 0

    def move_towards(self, target_x, target_y):
        angle = math.atan2(target_y - self.y, target_x - self.x)
        new_x = self.x + math.cos(angle) * MOVEMENT_COST
        new_y = self.y + math.sin(angle) * MOVEMENT_COST
        self.move(new_x, new_y)

# Функция для создания начальной популяции красных кружков
def create_initial_population():
    population = []
    for _ in range(POPULATION_SIZE):
        x = random.randint(CIRCLE_RADIUS, WIDTH - CIRCLE_RADIUS)
        y = random.randint(CIRCLE_RADIUS, HEIGHT - CIRCLE_RADIUS)
        color = RED
        hp = INITIAL_HP
        population.append(Circle(x, y, color, hp))
    return population

# Функция для создания начальной популяции зеленых кружков
def create_initial_green_circles():
    green_circles = []
    for _ in range(INITIAL_GREEN_CIRCLES):
        x = random.randint(CIRCLE_RADIUS, WIDTH - CIRCLE_RADIUS)
        y = random.randint(CIRCLE_RADIUS, HEIGHT - CIRCLE_RADIUS)
        color = GREEN
        hp = INITIAL_HP
        green_circles.append(Circle(x, y, color, hp))
    return green_circles

# Функция для отображения популяции
def draw_population(population):
    for circle in population:
        circle.draw()

# Функция для мутации кружка
def mutate(circle):
    new_x = circle.x + random.randint(-5, 5)
    new_y = circle.y + random.randint(-5, 5)
    circle.move_towards(new_x, new_y)

# Функция для проверки столкновения кружков
def check_collision(circles):
    for i in range(len(circles)):
        for j in range(i + 1, len(circles)):
            if circles[i].distance(circles[j]) < 2 * CIRCLE_RADIUS:
                return True
    return False


# Функция для размножения с улучшением
def reproduce(population):
    new_population = []
    for circle in population:
        # Создание потомков с улучшениями
        for _ in range(2):
            new_x = circle.x + random.randint(-5, 5)
            new_y = circle.y + random.randint(-5, 5)

            # Улучшение показателей потомков
            new_hp = circle.hp + random.randint(1, 10)  # Увеличиваем здоровье случайным образом

            # Ограничиваем здоровье максимальным значением
            new_hp = min(new_hp, MAX_HP_VALUE)

            new_population.append(Circle(new_x, new_y, RED, new_hp))
    return new_population


# Функция для генерации новых зеленых кружков
def generate_new_green_circles(existing_green_circles, target_count):
    new_green_circles = []
    for _ in range(target_count - len(existing_green_circles)):
        x = random.randint(CIRCLE_RADIUS, WIDTH - CIRCLE_RADIUS)
        y = random.randint(CIRCLE_RADIUS, HEIGHT - CIRCLE_RADIUS)
        color = GREEN
        hp = INITIAL_HP
        new_green_circles.append(Circle(x, y, color, hp))
    return new_green_circles

# Основной код
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Genetic Algorithm")

population = create_initial_population()
green_circles = create_initial_green_circles()

font = pygame.font.Font(None, 36)

clock = pygame.time.Clock()

generation_count = 1  # Счетчик поколений

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Генерация новых зеленых кружков
    green_circles += generate_new_green_circles(green_circles, TARGET_GREEN_CIRCLE_COUNT)

    # Проверка столкновений между красными кружками
    if not population or check_collision(population):
        population = create_initial_population()
        generation_count += 1

    screen.fill((255, 255, 255))

    draw_population(population)
    draw_population(green_circles)

    # Логика поедания зеленых кружков и движения красных
    for red_circle in population:
        # Находим ближайший зеленый кружок
        closest_green_circle = min(green_circles, key=lambda green_circle: red_circle.distance(green_circle))
        # Двигаемся к зеленому кружку
        red_circle.move_towards(closest_green_circle.x, closest_green_circle.y)

        # Проверяем столкновение с другими красными кружками
        for other_red_circle in population:
            if red_circle != other_red_circle and red_circle.distance(other_red_circle) < 2 * CIRCLE_RADIUS:
                # Касание другого красного кружка
                if red_circle.hp > other_red_circle.hp:
                    # Уменьшаем HP у того, кто сильнее
                    red_circle.hp -= HP_REDUCTION_PER_MOVE
                else:
                    # Уменьшаем HP у того, кто слабее
                    other_red_circle.hp -= HP_REDUCTION_PER_MOVE

        # Проверяем съедание зеленых кружков
        if red_circle.distance(closest_green_circle) < 2 * CIRCLE_RADIUS:
            green_circles.remove(closest_green_circle)
            red_circle.hp += EATEN_HP_BONUS

    # Логика размножения
    if len(population) <= 3:
        population += reproduce(population)

    # Удаление кружков с HP <= 0
    population = [circle for circle in population if circle.hp > 0]

    # Отображение количества красных кружков, счетчика действий и счетчика поколений
    red_count_text = font.render("Red Circles: {}".format(len(population)), True, (0, 0, 0))
    action_count_text = font.render("Actions: {}".format(len(population) * 2), True, (0, 0, 0))
    generation_count_text = font.render("Generation: {}".format(generation_count), True, (0, 0, 0))

    screen.blit(red_count_text, (10, 10))
    screen.blit(action_count_text, (10, 40))
    screen.blit(generation_count_text, (10, 70))

    pygame.display.flip()
    clock.tick(60)  # Установите желаемую частоту обновлений
