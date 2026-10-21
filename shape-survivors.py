import pygame
import random
import math

screen_width = 1920
screen_height = 1080
max_frame_rate = 144

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Shape Survivors")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont(None, 36)
font_large = pygame.font.SysFont(None, 72)

game_state = "START"

def reset_game():
    global player_x, player_y, player_health, i_frames, enemy_one_x, enemy_one_y, game_state, shoot_cooldown
    player_x = screen_width / 2
    player_y = screen_height / 2
    player_health = max_health
    i_frames = 0
    enemy_one_x = random.randint(20, screen_width - 20)
    enemy_one_y = random.randint(20, screen_height - 20)
    projectiles.clear()
    enemies.clear()
    shoot_cooldown = 0

player_speed = 2
max_health = 100

projectiles = []
projectile_speed = 6
projectile_radius = 6
shoot_cooldown = 0
shoot_interval = max_frame_rate
facing_x, facing_y = 1, 0

enemies = []
enemy_spawn_interval = max_frame_rate * 4
spawn_timer = 0


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if game_state == "START":
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    reset_game()
                    game_state = "PLAYING"

            elif game_state == "GAME_OVER":
                if event.key == pygame.K_r:
                    reset_game()
                    game_state = "PLAYING"

    if game_state == "START":
        title_surf = font_large.render("SHAPE SURVIVORS", True, (0, 255, 150))
        prompt_surf = font_small.render("Press [SPACE] or [ENTER] to Start", True, (200, 200, 200))
        screen.blit(title_surf, (screen_width // 2 - title_surf.get_width() // 2, screen_height // 2 - 100))
        screen.blit(prompt_surf, (screen_width // 2 - prompt_surf.get_width() // 2, screen_height // 2))
        
    if game_state == "PLAYING":
        #----------------------------------------PLAYER
        keys = pygame.key.get_pressed()
        move_x, move_y = 0, 0
        if keys[pygame.K_w]: move_y -= 1
        if keys[pygame.K_s]: move_y += 1
        if keys[pygame.K_a]: move_x -= 1
        if keys[pygame.K_d]: move_x += 1

        player_x += move_x * player_speed
        player_y += move_y * player_speed

        camera_x = player_x - screen_width / 2
        camera_y = player_y - screen_height / 2
        
        if move_x != 0 or move_y != 0:
            mag = math.hypot(move_x, move_y)
            facing_x = move_x / mag
            facing_y = move_y / mag
        #----------------------------------------

        #----------------------------------------PROJECTILES
        if shoot_cooldown > 0:
            shoot_cooldown -= 1
        else:
            projectiles.append({
                "x": player_x,
                "y": player_y,
                "dx": facing_x,
                "dy": facing_y
            })
            shoot_cooldown = shoot_interval

        for p in projectiles[:]:
            p["x"] += p["dx"] * projectile_speed
            p["y"] += p["dy"] * projectile_speed

            if math.hypot(p["x"] - player_x, p["y"] - player_y) > 1000:
                projectiles.remove(p)

            projectile_hit = False
            for enemy in enemies[:]:
                distance_to_enemy = math.hypot(p["x"] - enemy["x"], p["y"] - enemy["y"])
                if distance_to_enemy < (projectile_radius + enemy["radius"]):
                        enemies.remove(enemy)
                        projectile_hit = True
                        break

            if projectile_hit:
                if p in projectiles:
                    projectiles.remove(p)
        #----------------------------------------
    
        #----------------------------------------ENEMIES
        spawn_timer += 1
        if spawn_timer >= enemy_spawn_interval:
            spawn_timer = 0
            spawn_angle = random.uniform(0, 2 * math.pi)
            spawn_distance = random.randint(800, 1000)
            enemies.append({
                "x": player_x + math.cos(spawn_angle) * spawn_distance,
                "y": player_y + math.sin(spawn_angle) * spawn_distance,
                "speed": 1.3,
                "radius": 10
            })

        is_colliding = False
        for enemy in enemies[:]:
            dx = player_x - enemy["x"]
            dy = player_y - enemy["y"]
            distance = math.hypot(dx, dy)

            if distance > 1:
                dx /= distance
                dy /= distance
                enemy["x"] += dx * enemy["speed"]
                enemy["y"] += dy * enemy["speed"]

            if distance < (15 + enemy["radius"]):
                is_colliding = True

        if i_frames > 0:
            i_frames -= 1

        if player_health <= 0:
            game_state = "GAME_OVER"

        if is_colliding and i_frames == 0:
            player_health -= 5
            i_frames = max_frame_rate / 3
        #----------------------------------------

        #----------------------------------------RENDERING 
        # BACKGROUND
        screen.fill((30, 30, 30))
        start_x = int(-camera_x) % 100
        start_y = int(-camera_y) % 100

        for x in range(start_x, screen_width, 100):
            pygame.draw.line(screen, (35, 35, 45), (x, 0), (x, screen_height), 1)
        for y in range(start_y, screen_height, 100):
            pygame.draw.line(screen, (35, 35, 45), (0, y), (screen_width, y), 1)

        # PLAYER
        if i_frames > 0:
            if (i_frames // (max_frame_rate / 7)) % 2 == 0:
                player_color = (150, 50, 50)
            else:
                player_color = (255, 0, 0)
        else:
            player_color = (144, 11, 11)

        pygame.draw.circle(screen, player_color, (player_x - camera_x, player_y - camera_y), 15)

        # PROJECTILES
        for p in projectiles:
            proj_screen_x = p["x"] - camera_x
            proj_screen_y = p["y"] - camera_y
            pygame.draw.circle(screen, (255, 255, 0), (proj_screen_x, proj_screen_y), projectile_radius)

        # ENEMIES
        for enemy in enemies:
            ex = enemy["x"] - camera_x
            ey = enemy["y"] - camera_y
            r = enemy["radius"]
            pygame.draw.polygon(screen, (0, 255, 0), (
                (ex, ey - r),
                (ex - r * math.sqrt(3) / 2, ey + r / 2),
                (ex + r * math.sqrt(3) / 2, ey + r / 2)
            ))

        # HEALTH BAR
        bar_width = 300
        bar_height = 20
        bar_x = 50
        bar_y = 50
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        current_health_width = int(bar_width * (player_health / max_health))
        pygame.draw.rect(screen, (50, 200, 50), (bar_x, bar_y, current_health_width, bar_height))
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)

        # FPS COUNTER
        fps_surface = font_small.render(f"FPS: {round(clock.get_fps(), 1)}", True, (255, 255, 255))
        screen.blit(fps_surface, (screen_width - 150, 30))
        #----------------------------------------

    elif game_state == "GAME_OVER":

        over_surf = font_large.render('GAME OVER', True, (255, 50, 50))
        restart_surf = font_small.render('Press [R] to restart or [ESC] to Quit', True, (200, 200, 200))
        screen.blit(over_surf, (screen_width // 2 - over_surf.get_width() // 2, screen_height // 2 - 100))
        screen.blit(restart_surf, (screen_width // 2 - restart_surf.get_width() // 2, screen_height // 2))
    

    pygame.display.flip()
    clock.tick(max_frame_rate)

pygame.quit()

