import pygame
import random
import heapq
from map import generate_map

pygame.init()

def spawn_npc():
    while True:
        x = random.randint(1, len(MAP[0]) - 2)
        y = random.randint(1, len(MAP) - 2)

        if MAP[y][x] == 0:
            return x, y
        
        
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid, start, goal, avoid=None):
    
    rows = len(grid)
    cols = len(grid[0])

    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        x, y = current

        neighbors = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]

        for nx, ny in neighbors:
            if 0 <= nx < cols and 0 <= ny < rows:
                if not (0 < nx < len(MAP[0]) - 1 and 0 < ny < len(MAP) - 1):
                    continue

                if grid[ny][nx] != 0:
                    continue

                # 💥 custo de medo (FUGA)
                extra_cost = danger_map[ny][nx] * 10

                if avoid is not None:
                    dist_avoid = abs(nx - avoid[0]) + abs(ny - avoid[1])

                    if dist_avoid <= 8:
                        extra_cost += (9 - dist_avoid) ** 3 * 20

                neighbor = (nx, ny)

                tentative_g = g_score[current] + 1 + extra_cost

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)

                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None

def carregar_mapa():
    global MAP, danger_map
    global npc_x, npc_y
    global player_x, player_y
    global player2_x, player2_y
    global player1_path, player2_path
    global SCALE, WIDTH, HEIGHT, screen

    if SIZE < 9:
        tamanho = 9
    else:
        tamanho = SIZE

    MAP = generate_map(tamanho)

    danger_map = [
        [0 for _ in range(len(MAP[0]))]
        for _ in range(len(MAP))
    ]

    player1_path = []
    player2_path = []

    npc_x, npc_y = spawn_npc()

    SCALE = 600 / len(MAP)

    WIDTH = len(MAP[0]) * SCALE
    HEIGHT = len(MAP) * SCALE

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Mapa {len(MAP)}x{len(MAP)}")
    
SIZE = 2

player_x = 1
player_y = 1
player1_path = []
move_timer1 = 0

p1ia = False

if SIZE >= 9:
    MAP = generate_map(SIZE)
else:
    SIZE = 9
    MAP = generate_map(SIZE)

npc_x, npc_y = spawn_npc()

points = 0

player2_x = len(MAP[0]) - 2
player2_y = len(MAP) - 2
player2_path = []
move_timer = 0

devagar = 0.2
rapido = 0.15

danger_map = [[0 for _ in range(len(MAP[0]))] for _ in range(len(MAP))]

player2_points = 0
    
SCALE = 600 / len(MAP)

player_rect = pygame.Rect(
    player_x * SCALE,
    player_y * SCALE,
    SCALE,
    SCALE
)

WIDTH, HEIGHT = len(MAP[0])*SCALE, len(MAP)*SCALE
FPS = 240

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"Mapa {len(MAP)}x{len(MAP)}")

clock = pygame.time.Clock()
running = True

def events():
    global running, player_x, player_y

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if not p1ia:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_w:
                    player_y -= 1

                if event.key == pygame.K_s:
                    player_y += 1

                if event.key == pygame.K_a:
                    player_x -= 1

                if event.key == pygame.K_d:
                    player_x += 1
            
            player_x = max(1, min(player_x, len(MAP[0]) - 2))
            player_y = max(1, min(player_y, len(MAP) - 2))

speed_boost_timer = 0

def update(dt):
    
    global SIZE, MAP, WIDTH, HEIGHT, danger_map, speed_boost_timer, npc_x, npc_y, player_x, player_y, player2_x, player2_y, points, player2_points, player1_path, move_timer1, player2_path, move_timer
    
    dist = abs(player_x - player2_x) + abs(player_y - player2_y)

    if dist <= 2:
        danger_map[player_x][player_y] += 0.5
    
    if player_x == player2_x and player_y == player2_y:
        
        danger_map[player_x][player_y] += 20
        
        SIZE -= 1
        carregar_mapa()
        player2_points += 1
        
        player_x = 1
        player_y = 1

        player2_x = len(MAP[0]) - 2
        player2_y = len(MAP) - 2

        while MAP[player_y][player_x] == 1:
            player2_x = len(MAP[0]) - 2
            player2_y = len(MAP) - 2

        while MAP[player2_y][player2_x] == 1:
            player2_x = len(MAP[0]) - 2
            player2_y = len(MAP) - 2
    
    dist = abs(player_x - player2_x) + abs(player_y - player2_y)

    if dist == 1:
        speed_boost_timer = 3.0
        
    if player_x == npc_x and player_y == npc_y and player2_x == npc_x and player2_y == npc_y:
        points += 1

        npc_x, npc_y = spawn_npc()
            
    if player_x == npc_x and player_y == npc_y:
        SIZE += 1
        carregar_mapa()
        points += 1

        # garante que não spawn em parede
        while MAP[npc_y][npc_x] == 1:
            npc_x, npc_y = spawn_npc()
    
    # PLAYER 2 coleta NPC azul
    if player2_x == npc_x and player2_y == npc_y:
        player2_points += 1

        npc_x, npc_y = spawn_npc()

        while MAP[npc_y][npc_x] == 1:
            npc_x, npc_y = spawn_npc()
    
    #####################################################
    
    if p1ia:
        start = (player_x, player_y)
        goal = (npc_x, npc_y)

        if not player1_path or player1_path[-1] != goal:
            path = astar(MAP, start, goal, avoid=(player2_x, player2_y))
            
            player1_path = path[1:]

        move_timer1 += dt

        speed = rapido if speed_boost_timer > 0 else devagar

        if move_timer1 > speed and player1_path:
            move_timer1 = 0

            nx, ny = player1_path.pop(0)

            if MAP[ny][nx] == 0:
                player_x, player_y = nx, ny
    
    #####################################################

    start = (player2_x, player2_y)
    goal = (player_x, player_y)

    if not player2_path or player2_path[-1] != goal:
        path = astar(MAP, start, goal, avoid=(player_x, player_y))
        
        player2_path = path[1:]
                
    if player1_path and player2_path:
        if player1_path[:5] == player2_path[:5]:
            npc_x, npc_y = spawn_npc()
            player1_path = []
            player2_path = []

    move_timer += dt

    if move_timer > devagar and player2_path:
        move_timer = 0

        nx, ny = player2_path.pop(0)

        if MAP[ny][nx] == 0:
            player2_x, player2_y = nx, ny
        
    if speed_boost_timer > 0:
        speed_boost_timer -= dt

    for y in range(len(MAP)):
        for x in range(len(MAP[0])):
            danger_map[y][x] *= 0.995

def draw():
    size = len(MAP)

    screen.fill("black")

    # grid
    for x in range(size + 1):
        pygame.draw.line(screen, (40, 40, 40),
                         (x * SCALE, 0),
                         (x * SCALE, size * SCALE))

    for y in range(size + 1):
        pygame.draw.line(screen, (40, 40, 40),
                         (0, y * SCALE),
                         (size * SCALE, y * SCALE))

    # paredes
    pygame.draw.rect(screen, "white", (0, 0, size*SCALE, SCALE))
    pygame.draw.rect(screen, "white", (0, (size-1)*SCALE, size*SCALE, SCALE))
    pygame.draw.rect(screen, "white", (0, 0, SCALE, size*SCALE))
    pygame.draw.rect(screen, "white", ((size-1)*SCALE, 0, SCALE, size*SCALE))

    # player
    pygame.draw.rect(
        screen,
        "red",
        (player_x * SCALE, player_y * SCALE, SCALE, SCALE)
    )
    
    pygame.draw.rect(
        screen,
        "green",
        (player2_x * SCALE, player2_y * SCALE, SCALE, SCALE)
    )
    
    pygame.draw.rect(
        screen,
        "blue",
        (npc_x * SCALE, npc_y * SCALE, SCALE, SCALE)
    )
    
    font = pygame.font.SysFont(None, 36)

    text1 = font.render(f"P1: {points}", True, "white")
    text2 = font.render(f"P2: {player2_points}", True, "white")

    screen.blit(text1, (50, 50))
    screen.blit(text2, (50, 80))

    pygame.display.flip()


def main():
    while running:
        dt = clock.tick(FPS) / 1000
        events()
        update(dt)
        draw()

    pygame.quit()


if __name__ == "__main__":
    main()