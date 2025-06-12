import pygame
import random
import math
import os

pygame.init()

# Música de fondo
pygame.mixer.init()
pygame.mixer.music.load("musica_fondo.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego de Supervivencia Zombi")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)

font = pygame.font.SysFont(None, 24)
font_big = pygame.font.SysFont(None, 48)

player_name = "Oli"

def show_menu():
    while True:
        screen.fill(WHITE)
        title_text = font_big.render("Supervivencia Zombi", True, BLACK)
        start_text = font.render("Presiona ENTER para jugar", True, BLACK)
        exit_text = font.render("Presiona ESC para salir", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 200))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 300))
        screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, 330))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

def show_game_over():
    while True:
        screen.fill(WHITE)
        game_over_text = font_big.render("Game Over", True, RED)
        restart_text = font.render("Presiona R para reiniciar o ESC para salir", True, BLACK)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 200))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 300))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

def draw_player(pos):
    pygame.draw.rect(screen, BLUE, (*pos, 40, 40))
    name_text = font.render(player_name, True, BLACK)
    screen.blit(name_text, (pos[0], pos[1] - 20))

def draw_bullet(pos):
    pygame.draw.circle(screen, BLACK, pos, 5)

def draw_zombie(z):
    colors = {
        'normal': RED,
        'tank': DARK_RED,
        'mutant': PURPLE,
        'fast': ORANGE,
        'brute': BROWN,
        'boss': GRAY
    }
    color = colors.get(z['type'], RED)
    pygame.draw.rect(screen, color, (*z['pos'], z['size'], z['size']))
    health_ratio = z['health'] / {
        'normal': 3,
        'tank': 6,
        'mutant': 10,
        'fast': 2,
        'brute': 5,
        'boss': 30 + 10 * round_number
    }[z['type']]
    pygame.draw.rect(screen, RED, (z['pos'][0], z['pos'][1] - 10, z['size'], 5))
    pygame.draw.rect(screen, GREEN, (z['pos'][0], z['pos'][1] - 10, z['size'] * health_ratio, 5))

def draw_powerups():
    for x, y, t in powerups:
        color = YELLOW if t == 'damage' else GREEN
        pygame.draw.rect(screen, color, (x, y, 20, 20))

def draw_health_bar():
    pygame.draw.rect(screen, RED, (10, 10, 200, 20))
    pygame.draw.rect(screen, GREEN, (10, 10, 200 * (player_health / player_max_health), 20))

def draw_score():
    score_text = font.render(f"Puntuación: {score}  Mejor: {high_score}", True, BLACK)
    screen.blit(score_text, (10, 40))

def draw_round():
    round_text = font.render(f"Ronda: {round_number}", True, BLACK)
    screen.blit(round_text, (WIDTH - 120, 10))

def main():
    global player_pos, player_speed, player_size, player_health, player_max_health
    global bullets, bullet_speed, bullet_damage
    global zombies, zombie_size, SPAWN_ZOMBIE, boss_exists
    global powerups, powerup_size, powerup_duration
    global powerup_active, powerup_timer, health_boost_active, health_boost_timer, SPAWN_POWERUP
    global score, high_score_file, high_score
    global round_number, zombies_killed_this_round, zombies_to_kill

    player_pos = [WIDTH // 2, HEIGHT // 2]
    player_speed = 5
    player_size = 40
    player_health = 100
    player_max_health = 100

    bullets = []
    bullet_speed = 10
    bullet_damage = 1

    zombies = []
    zombie_size = 40
    SPAWN_ZOMBIE = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_ZOMBIE, 2000)
    boss_exists = False

    powerups = []
    powerup_size = 20
    powerup_duration = 5000
    powerup_active = False
    powerup_timer = 0
    health_boost_active = False
    health_boost_timer = 0
    SPAWN_POWERUP = pygame.USEREVENT + 2
    pygame.time.set_timer(SPAWN_POWERUP, 10000)

    score = 0
    high_score_file = "highscore.txt"
    if os.path.exists(high_score_file):
        with open(high_score_file, "r") as f:
            high_score = int(f.read())
    else:
        high_score = 0

    round_number = 1
    zombies_killed_this_round = 0
    zombies_to_kill = 10

    show_menu()

    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(60)
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == SPAWN_ZOMBIE:
                x = random.randint(0, WIDTH - zombie_size)
                y = random.choice([0, HEIGHT - zombie_size])
                z_type = random.choice(['normal', 'tank', 'mutant', 'fast', 'brute'])
                health_map = {'normal': 3, 'tank': 6, 'mutant': 10, 'fast': 2, 'brute': 5}
                speed_map = {'normal': 1, 'tank': 1, 'mutant': 1, 'fast': 3, 'brute': 1}
                damage_map = {'normal': 1, 'tank': 1, 'mutant': 1, 'fast': 1, 'brute': 3}
                size_map = {'normal': zombie_size, 'tank': zombie_size, 'mutant': zombie_size, 'fast': zombie_size, 'brute': zombie_size}
                zombies.append({
                    'pos': [x, y],
                    'health': health_map[z_type],
                    'type': z_type,
                    'speed': speed_map[z_type],
                    'damage': damage_map[z_type],
                    'size': size_map[z_type]
                })
            elif event.type == SPAWN_POWERUP:
                x = random.randint(0, WIDTH - powerup_size)
                y = random.randint(0, HEIGHT - powerup_size)
                p_type = random.choice(['damage', 'health'])
                powerups.append((x, y, p_type))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                dx, dy = mx - (player_pos[0] + player_size // 2), my - (player_pos[1] + player_size // 2)
                distance = math.hypot(dx, dy)
                dx, dy = dx / distance, dy / distance
                bullets.append([[player_pos[0] + player_size // 2, player_pos[1] + player_size // 2], [dx, dy]])

        if powerup_active and pygame.time.get_ticks() > powerup_timer:
            bullet_damage = 1
            powerup_active = False

        if health_boost_active and pygame.time.get_ticks() > health_boost_timer:
            player_max_health //= 2
            if player_health > player_max_health:
                player_health = player_max_health
            health_boost_active = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: player_pos[1] -= player_speed
        if keys[pygame.K_s]: player_pos[1] += player_speed
        if keys[pygame.K_a]: player_pos[0] -= player_speed
        if keys[pygame.K_d]: player_pos[0] += player_speed

        for bullet in bullets[:]:
            bullet[0][0] += bullet[1][0] * bullet_speed
            bullet[0][1] += bullet[1][1] * bullet_speed
            if bullet[0][0] < 0 or bullet[0][0] > WIDTH or bullet[0][1] < 0 or bullet[0][1] > HEIGHT:
                bullets.remove(bullet)

        for zombie in zombies[:]:
            dx = player_pos[0] - zombie['pos'][0]
            dy = player_pos[1] - zombie['pos'][1]
            dist = math.hypot(dx, dy)
            if dist != 0:
                zombie['pos'][0] += zombie['speed'] * dx / dist
                zombie['pos'][1] += zombie['speed'] * dy / dist

            if zombie['type'] == 'boss' and pygame.time.get_ticks() > zombie.get('spawn_timer', 0):
            # Solo invocar si no hay minions vivos
                zombie['minions'] = [m for m in zombie.get('minions', []) if m in zombies]
                if not zombie['minions']:
                    zombie['minions'] = []
                    for _ in range(3):
                        zx = zombie['pos'][0] + random.randint(-30, 30)
                        zy = zombie['pos'][1] + random.randint(-30, 30)
                        zx = max(0, min(WIDTH - zombie_size, zx))
                        zy = max(0, min(HEIGHT - zombie_size, zy))
                        minion = ({
                            'pos': [zx, zy],
                            'health': 2,
                            'type': 'normal',
                            'speed': 1,
                            'damage': 1,
                            'size': zombie_size
                        })
                        zombies.append(minion)
                        zombie['minions'].append(minion)
                    zombie['spawn_timer'] = pygame.time.get_ticks() + 3000

            if pygame.Rect(*player_pos, player_size, player_size).colliderect(pygame.Rect(*zombie['pos'], zombie['size'], zombie['size'])):
                player_health -= zombie['damage']
                if player_health <= 0:
                    running = False
                    break

            for bullet in bullets[:]:
                if pygame.Rect(*bullet[0], 5, 5).colliderect(pygame.Rect(*zombie['pos'], zombie['size'], zombie['size'])):
                    zombie['health'] -= bullet_damage
                    bullets.remove(bullet)
                    if zombie['health'] <= 0:
                        if zombie['type'] == 'boss':
                            boss_exists = False
                        zombies.remove(zombie)
                        score += 1
                        zombies_killed_this_round += 1

                        if score > high_score:
                            high_score = score
                            with open(high_score_file, "w") as f:
                                f.write(str(high_score))

                        if not any(z['type'] != 'boss' for z in zombies) and not boss_exists:
                            round_number += 1
                            zombies_killed_this_round = 0
                            zombies_to_kill += 5
                            x = random.randint(0, WIDTH - 80)
                            y = random.choice([0, HEIGHT - 80])
                            boss = {
                                'pos': [x, y],
                                'health': 30 + 10 * round_number,
                                'type': 'boss',
                                'speed': 0.5,
                                'damage': 4,
                                'size': 80,
                                'spawn_timer': pygame.time.get_ticks() + 3000,
                                'minions': []
                            }
                            zombies.append(boss)
                            boss_exists = True
                        break
                    # Solo avanzar ronda si no hay zombis ni jefe
                    if not zombies and not boss_exists:
                        round_number += 1
                        zombies_killed_this_round = 0
                        zombies_to_kill += 5
                        x = random.randint(0, WIDTH - 80)
                        y = random.choice([0, HEIGHT - 80])
                        boss = {
                            'pos': [x, y],
                            'health': 30 + 10 * round_number,
                            'type': 'boss',
                            'speed': 0.5,
                            'damage': 4,
                            'size': 80,
                            'spawn_timer': pygame.time.get_ticks() + 3000,
                            'minions': []
                        }
                        zombies.append(boss)
                        boss_exists = True


        for powerup in powerups[:]:
            if pygame.Rect(*player_pos, player_size, player_size).colliderect(pygame.Rect(powerup[0], powerup[1], powerup_size, powerup_size)):
                if powerup[2] == 'damage':
                    bullet_damage = 2
                    powerup_active = True
                    powerup_timer = pygame.time.get_ticks() + powerup_duration
                elif powerup[2] == 'health':
                    player_max_health *= 2
                    player_health = player_max_health
                    health_boost_active = True
                    health_boost_timer = pygame.time.get_ticks() + 10000
                powerups.remove(powerup)

        draw_player(player_pos)
        for bullet in bullets:
            draw_bullet([int(bullet[0][0]), int(bullet[0][1])])
        for zombie in zombies:
            draw_zombie(zombie)
        draw_powerups()
        draw_health_bar()
        draw_score()
        draw_round()
        pygame.display.flip()

    if not running:
        if show_game_over():
            main()

if __name__ == "__main__":
    main()
    pygame.quit()
