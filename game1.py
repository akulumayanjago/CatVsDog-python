import pygame
import random
import sys
import math

# Inisialisasi pygame dan mixer
pygame.init()
pygame.mixer.init()

# Ukuran layar
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("kucing vs anjing Maze")

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (10, 10, 80)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Font
font = pygame.font.SysFont('Arial', 24)

# Load suara
try:
    pygame.mixer.music.load("background.mp3")
    eat_sound = pygame.mixer.Sound("eat_sound.mp3")
    gameover_sound = pygame.mixer.Sound("gameover.mp3")
    pygame.mixer.music.play(-1)
except:
    print("Audio file not found. Lanjut tanpa suara.")
    eat_sound = None
    gameover_sound = None

# Fungsi untuk menggambar teks
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

# Load gambar
kucing = pygame.transform.scale(pygame.image.load("kucing.png"), (30, 30))
makanan_img = pygame.transform.scale(pygame.image.load("makanan.png"), (20, 20))
anjing_img = pygame.transform.scale(pygame.image.load("anjing.png"), (30, 30))

# Fungsi untuk membuat labirin
def generate_maze(width, height):
    maze = [[1] * width for _ in range(height)]
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def is_valid_move(x, y):
        return 0 <= x < width and 0 <= y < height and maze[y][x] == 1

    def dfs(x, y):
        maze[y][x] = 0
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if is_valid_move(nx, ny):
                maze[ny][nx] = 0
                maze[y + dy][x + dx] = 0
                dfs(nx, ny)

    start_x, start_y = random.randint(1, width // 2) * 2, random.randint(1, height // 2) * 2
    dfs(start_x, start_y)
    return maze

# Konfigurasi labirin
maze_width, maze_height = 26, 18
CELL_SIZE = 30
maze = generate_maze(maze_width, maze_height)
MAZE_WIDTH = maze_width * CELL_SIZE
MAZE_HEIGHT = maze_height * CELL_SIZE

# Posisi kucing
def get_valid_kucing_position():
    while True:
        x, y = random.randint(1, maze_width - 2), random.randint(1, maze_height - 2)
        if maze[y][x] == 0:
            return x * CELL_SIZE, y * CELL_SIZE

kucing_x, kucing_y = get_valid_kucing_position()
dx, dy = 0, 0

# Hantu
anjing_list = []
def spawn_anjing():
    anjing_list.clear()
    for _ in range(3):
        while True:
            x = random.randint(0, maze_width - 1)
            y = random.randint(0, maze_height - 1)
            if maze[y][x] == 0:
                anjing_list.append({'x': x * CELL_SIZE, 'y': y * CELL_SIZE, 'dx': random.choice([-2, 2]), 'dy': random.choice([-2, 2])})
                break

spawn_anjing()

# makanan dan Partikel
makanan = []
particles = []

for y in range(maze_height):
    for x in range(maze_width):
        if maze[y][x] == 0:
            makanan.append((x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))

score = 0
game_over = False
win = False

# Fungsi untuk menggambar labirin
def draw_maze():
    for y in range(maze_height):
        for x in range(maze_width):
            if maze[y][x] == 1:
                pygame.draw.rect(screen, DARK_BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Cek tabrakan dinding
def check_wall_collision(x, y):
    corners = [(x, y), (x + CELL_SIZE - 1, y), (x, y + CELL_SIZE - 1), (x + CELL_SIZE - 1, y + CELL_SIZE - 1)]
    for corner_x, corner_y in corners:
        cell_x, cell_y = corner_x // CELL_SIZE, corner_y // CELL_SIZE
        if corner_x < 0 or corner_x >= MAZE_WIDTH or corner_y < 0 or corner_y >= MAZE_HEIGHT:
            return True
        if maze[cell_y][cell_x] == 1:
            return True
    return False

# Gerak hantu
def gerak_anjing():
    for anjing in anjing_list:
        nx, ny = anjing['x'] + anjing['dx'], anjing['y'] + anjing['dy']
        if check_wall_collision(nx, ny):
            dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                if not check_wall_collision(anjing['x'] + dx, anjing['y'] + dy):
                    anjing['dx'], anjing['dy'] = dx, dy
                    break
        anjing['x'] += anjing['dx']
        anjing['y'] += anjing['dy']

# Partikel
def create_particles(x, y):
    for _ in range(10):
        particles.append({'x': x, 'y': y, 'dx': random.uniform(-2, 2), 'dy': random.uniform(-2, 2), 'life': 20})

def update_particles():
    for p in particles[:]:
        p['x'] += p['dx']
        p['y'] += p['dy']
        p['life'] -= 1
        if p['life'] <= 0:
            particles.remove(p)

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BLACK)
    wave = int(math.sin(pygame.time.get_ticks() * 5) * 10)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_over and not win:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: dx, dy = -2, 0
                if event.key == pygame.K_RIGHT: dx, dy = 2, 0
                if event.key == pygame.K_UP: dx, dy = 0, -2
                if event.key == pygame.K_DOWN: dx, dy = 0, 2
                if event.key == pygame.K_q: running = False
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                kucing_x, kucing_y = get_valid_kucing_position()
                dx = dy = score = 0
                game_over = win = False
                spawn_anjing()
                makanan = [(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2) for y in range(maze_height) for x in range(maze_width) if maze[y][x] == 0]

    if not game_over and not win:
        if not check_wall_collision(kucing_x + dx, kucing_y + dy):
            kucing_x += dx
            kucing_y += dy

        gerak_anjing()

        kucing_rect = pygame.Rect(kucing_x, kucing_y, CELL_SIZE, CELL_SIZE)
        for anjing in anjing_list:
            if kucing_rect.colliderect(pygame.Rect(anjing['x'], anjing['y'], CELL_SIZE, CELL_SIZE)):
                if gameover_sound:
                    gameover_sound.play()
                game_over = True

        for apple in makanan[:]:
            if math.hypot(apple[0] - (kucing_x + 15), apple[1] - (kucing_y + 15)) < 15:
                makanan.remove(apple)
                score += 10
                if eat_sound:
                    eat_sound.play()
                create_particles(*apple)

        if not makanan:
            win = True

    draw_maze()
    for apple in makanan:
        screen.blit(makanan_img, (apple[0] - 10, apple[1] - 10))
    screen.blit(kucing, (kucing_x, kucing_y))
    for anjing in anjing_list:
        screen.blit(anjing_img, (anjing['x'], anjing['y']))
    update_particles()
    for p in particles:
        pygame.draw.circle(screen, YELLOW, (int(p['x']), int(p['y'])), 3)

    pygame.draw.rect(screen, BLACK, (0, HEIGHT - 50, WIDTH, 50))  # Background bar for text at the bottom
    draw_text(f"Skor: {score}", font, WHITE, screen, 10, HEIGHT - 40)
    exit_button = pygame.draw.rect(screen, RED, (WIDTH - 220, HEIGHT - 40, 100, 30))  # Exit button
    restart_button = pygame.draw.rect(screen, GREEN, (WIDTH - 110, HEIGHT - 40, 100, 30))  # Restart button
    draw_text("Keluar", font, WHITE, screen, WIDTH - 200, HEIGHT - 35)
    draw_text("Restart", font, WHITE, screen, WIDTH - 90, HEIGHT - 35)

    # Check for button clicks
    if pygame.mouse.get_pressed()[0]:  # Left mouse button
        mouse_pos = pygame.mouse.get_pos()
        if exit_button.collidepoint(mouse_pos):
            running = False
        if restart_button.collidepoint(mouse_pos):
            kucing_x, kucing_y = get_valid_kucing_position()
            dx = dy = score = 0
            game_over = win = False
            spawn_anjing()
            makanan = [(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2) for y in range(maze_height) for x in range(maze_width) if maze[y][x] == 0]

    if game_over:
        draw_text("GAME OVER!", font, RED, screen, WIDTH // 2 - 100, HEIGHT // 2 - 20 + wave)
    if win:
        draw_text("YOU WIN!", font, GREEN, screen, WIDTH // 2 - 80, HEIGHT // 2 - 20 + wave)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
