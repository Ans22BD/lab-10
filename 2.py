import pygame
import psycopg2
import json
import sys
from random import randint

# === 1. Настройки подключения к PostgreSQL ===
DB_NAME = "snake_db"
DB_USER = "postgres"
DB_PASSWORD = "Batyr2007"
DB_HOST = "localhost"
DB_PORT = "5432"

# === 2. База данных ===

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "user" (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_score (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES "user"(id),
            score INTEGER,
            level INTEGER,
            saved_state TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Таблицы созданы")

def get_or_create_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM "user" WHERE username = %s', (username,))
    result = cursor.fetchone()

    if result:
        user_id = result[0]
    else:
        cursor.execute('INSERT INTO "user" (username) VALUES (%s) RETURNING id', (username,))
        user_id = cursor.fetchone()[0]
        conn.commit()

    conn.close()
    return user_id

def get_user_score(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT score, level FROM user_score WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (0, 1)

def save_game_state(user_id, score, level, snake, direction, food):
    state = {
        'snake': snake,
        'direction': direction,
        'food': food
    }
    state_json = json.dumps(state)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_score (user_id, score, level, saved_state)
        VALUES (%s, %s, %s, %s)
    """, (user_id, score, level, state_json))
    conn.commit()
    conn.close()
    print("💾 Игра сохранена")

# === 3. Игра ===

create_tables()

username = input("Введите имя пользователя: ")
user_id = get_or_create_user(username)
score, level = get_user_score(user_id)

print(f"Привет, {username}! Уровень: {level} | Очки: {score}")

pygame.init()
CELL_SIZE = 20
WIDTH, HEIGHT = 640, 480
FPS = 10 + level * 2

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка")
clock = pygame.time.Clock()

GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

snake = [(100, 100)]
direction = (CELL_SIZE, 0)
food = (randint(0, (WIDTH - CELL_SIZE)//CELL_SIZE) * CELL_SIZE,
        randint(0, (HEIGHT - CELL_SIZE)//CELL_SIZE) * CELL_SIZE)

paused = False
running = True

def draw_snake():
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (*segment, CELL_SIZE, CELL_SIZE))

def draw_food():
    pygame.draw.rect(screen, RED, (*food, CELL_SIZE, CELL_SIZE))

def move_snake():
    head = snake[0]
    new_head = (head[0] + direction[0], head[1] + direction[1])
    snake.insert(0, new_head)
    if new_head == food:
        return True
    else:
        snake.pop()
        return False

def check_collision():
    head = snake[0]
    return (
        head in snake[1:] or
        head[0] < 0 or head[0] >= WIDTH or
        head[1] < 0 or head[1] >= HEIGHT
    )

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game_state(user_id, score, level, snake, direction, food)
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != (0, CELL_SIZE):
                direction = (0, -CELL_SIZE)
            elif event.key == pygame.K_DOWN and direction != (0, -CELL_SIZE):
                direction = (0, CELL_SIZE)
            elif event.key == pygame.K_LEFT and direction != (CELL_SIZE, 0):
                direction = (-CELL_SIZE, 0)
            elif event.key == pygame.K_RIGHT and direction != (-CELL_SIZE, 0):
                direction = (CELL_SIZE, 0)
            elif event.key == pygame.K_p:
                paused = not paused
                print("⏸ Пауза" if paused else "▶ Продолжить")
            elif event.key == pygame.K_s:
                save_game_state(user_id, score, level, snake, direction, food)

    if not paused:
        if move_snake():
            score += 10
            food = (randint(0, (WIDTH - CELL_SIZE)//CELL_SIZE) * CELL_SIZE,
                    randint(0, (HEIGHT - CELL_SIZE)//CELL_SIZE) * CELL_SIZE)

        if check_collision():
            print("💀 Игра окончена! Счёт:", score)
            save_game_state(user_id, score, level, snake, direction, food)
            pygame.time.wait(2000)
            running = False

    draw_snake()
    draw_food()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
