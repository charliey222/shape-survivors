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

enemy_types = [
    {"type": "triangle", "sides": 3, "speed": 1.4, "radius": 20, "health": 15, "xp": 100, "damage": 5, "color": (0, 255, 0), "boss": False}, 
    {"type": "square", "sides" : 4, "speed": 0.8, "radius": 35, "health": 60, "xp": 13, "damage": 8, "color": (30, 30, 120), "boss": False},
    {"type": "pentagon", "sides": 5, "speed": 3, "radius": 16, "health": 10, "xp": 12, "damage": 10, "color": (48, 25, 52), "boss": False},
    {"type": "hexagon", "sides": 6, "speed": 0.6, "radius": 60, "health": 200, "xp": 100, "damage": 20, "color": (255, 165, 0), "boss": True},
    {"type": "septagon", "sides": 7, "speed": 1.5, "radius": 20, "health": 45, "xp": 15, "damage": 7, "color": (255, 20, 147), "boss": False},
    {"type": "octagon", "sides": 8, "speed": 1.1, "radius": 40, "health": 80, "xp": 20, "damage": 14, "color": (128, 128, 128), "boss": False}
]

equipped_weapons = [
    {"id": "sphere", "name": "Sphere", "damage": 10, "cooldown": 0, "interval": max_frame_rate / 2, "speed": 7, "radius": 6, "color": (255, 255, 0)}
]

upgrade_pool = [
    {"title": "Sphere Damage +5", "target": "sphere", "stat": "damage", "val": 5},
    {"title": "Sphere Cooldown -5", "target": "sphere", "stat": "interval", "val": -5},
    {"title": "Sphere Radius + 1", "target": "sphere", "stat": "radius", "val": 1}
]

current_choices = []

def reset_game():
    global game_time_frames, player_x, player_y, player_health, i_frames, regen_timer, player_xp, player_level, next_level, enemies_defeated, health_world_spawn_timer
    game_time_frames = 0
    player_x = screen_width / 2
    player_y = screen_height / 2
    player_health = max_health
    i_frames = 0
    regen_timer = 0
    player_xp = 0
    player_level = 1
    next_level = 50
    enemies_defeated = 0
    health_world_spawn_timer = 0
    health_orbs.clear()
    current_choices.clear()
    projectiles.clear()
    enemies.clear()
    xp_orbs.clear()
    dying_enemies.clear()
    floating_texts.clear()
    level_queue.clear()
    for w in equipped_weapons:
        w["cooldown"] = 0

def select_upgrade(index):
    global game_state, max_health, magnet, player_health, current_choices, level_queue
    if index < len(current_choices):
        choice = current_choices[index]

        if choice["target"] == "player":
            if choice["stat"] == "health":
                max_health += choice["val"]
                player_health = min(max_health, player_health + choice["val"])
            elif choice["stat"] == "magnet":
                magnet += choice["val"]

        else:
            for w in equipped_weapons:
                if w["name"] == choice["target"]:
                    if choice ["stat"] == "interval":
                        w["interval"] == max(10, w["interval" + choice["val"]])
                else:
                    w[choice["stat"]] += choice["val"]

        if len(level_queue) > 0:
            level_queue.pop(0)
        if len(level_queue) > 0:
            current_choices = random.sample(upgrade_pool, min(3, len(upgrade_pool)))
            game_state = "LEVEL_UP"
        else:
            game_state = "PLAYING"


player_speed = 2
max_health = 1000
player_regen = 0.5
magnet = 75

projectiles = []
facing_x, facing_y = 1, 0

enemies = []
enemy_spawn_interval = max_frame_rate * 2
spawn_timer = 0

health_orbs = []

dying_enemies = []

xp_orbs = []

floating_texts = []

level_queue = []

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

            elif game_state == "LEVEL_UP":
                if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    select_upgrade(0)
                elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    select_upgrade(1)
                elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                    select_upgrade(2)

    if game_state == "START":
        title_surf = font_large.render("SHAPE SURVIVORS", True, (0, 255, 150))
        prompt_surf = font_small.render("Press [SPACE] or [ENTER] to Start", True, (200, 200, 200))
        screen.blit(title_surf, (screen_width // 2 - title_surf.get_width() // 2, screen_height // 2 - 100))
        screen.blit(prompt_surf, (screen_width // 2 - prompt_surf.get_width() // 2, screen_height // 2))
        
    if game_state == "PLAYING":
        game_time_frames += 1
        #----------------------------------------PLAYER
        keys = pygame.key.get_pressed()
        move_x, move_y = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_KP8]: move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN] or keys[pygame.K_KP2]: move_y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT] or keys[pygame.K_KP4]: move_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT] or keys [pygame.K_KP6]: move_x += 1

        player_x += move_x * player_speed
        player_y += move_y * player_speed

        camera_x = player_x - screen_width / 2
        camera_y = player_y - screen_height / 2
        
        if move_x != 0 or move_y != 0:
            mag = math.hypot(move_x, move_y)
            facing_x = move_x / mag
            facing_y = move_y / mag

        if player_health < max_health:
            regen_timer += 1
            if regen_timer >= max_frame_rate:
                player_health = min(max_health, player_health + player_regen)
                regen_timer = 0
        else:
            regen_timer = 0
        #----------------------------------------

        #----------------------------------------WEAPONS
        for w in equipped_weapons:
            if w["cooldown"] > 0:
                w["cooldown"] -= 1
            else:
                projectiles.append({
                    "x": player_x + 15 * facing_x,
                    "y": player_y + 15 * facing_y,
                    "dx": facing_x,
                    "dy": facing_y,
                    "damage": w["damage"],
                    "speed": w["speed"],
                    "radius": w["radius"],
                    "color": w["color"],
                    "weapon_id" : w["id"]
                })
                w["cooldown"] = w["interval"]


        for p in projectiles[:]:
            p["x"] += p["dx"] * p["speed"]
            p["y"] += p["dy"] * p["speed"]

            if math.hypot(p["x"] - player_x, p["y"] - player_y) > 1000:
                projectiles.remove(p)

            projectile_hit = False
            for enemy in enemies[:]:
                distance_to_enemy = math.hypot(p["x"] - enemy["x"], p["y"] - enemy["y"])
                if distance_to_enemy < (p["radius"] + enemy["radius"]):
                        weapon_id = p["weapon_id"]
                        if enemy["hit_timers"].get(weapon_id, 0) == 0:
                            enemy["health"] -= p["damage"]
                            projectile_hit = True
                            enemy["hit_timers"][weapon_id] = 15
                            enemy["hit_flash"] = 16

                            if enemy["health"] <= 0:
                                enemies_defeated += 1
                                xp_orbs.append({
                                    "x": enemy["x"],
                                    "y": enemy["y"],
                                    "radius": math.sqrt(enemy["xp"]) + 5,
                                    "xp": enemy["xp"]
                                })

                                dying_enemies.append({
                                    "x": enemy["x"],
                                    "y": enemy["y"],
                                    "radius": enemy["radius"],
                                    "sides": enemy["sides"],
                                    "color": enemy["color"],
                                    "fade_timer": 64,
                                    "max_fade": 64
                                })
                                enemies.remove(enemy)
                            break

            if projectile_hit and p in projectiles:
                projectiles.remove(p)

        #----------------------------------------
    
        #----------------------------------------XP
        for orb in xp_orbs[:]:
            distance_to_player = math.hypot(orb["x"] - player_x, orb["y"] - player_y)
            if distance_to_player < magnet:
                angle_to_player = math.atan2(player_y - orb["y"], player_x - orb["x"])
                orb["x"] += math.cos(angle_to_player) * 2
                orb["y"] += math.sin(angle_to_player) * 2
                if distance_to_player < orb["radius"] + 15:
                    floating_texts.append({
                        "x": player_x,
                        "y": player_y - 20,
                        "text": f"+{orb["xp"]}",
                        "color": (0, 150, 255),
                        "timer": 45
                    })                
                    xp_orbs.remove(orb)
                    player_xp += orb["xp"]
                    while player_xp >= next_level:
                        player_xp -= next_level
                        player_level += 1
                        next_level += 1
                        level_queue.append(True)

                    if len(level_queue) > 0 and game_state == "PLAYING":
                        current_choices = random.sample(upgrade_pool, min (3, len(upgrade_pool)))
                        game_state = "LEVEL_UP"
                    break

        #----------------------------------------HEALTH
        health_world_spawn_timer += 1
        if health_world_spawn_timer >= max_frame_rate * 15:
            health_world_spawn_timer = 0
            spawn_angle = random.uniform(0, 2 * math.pi)
            spawn_dist = random.randint(500, 900)

            health_orbs.append({
                "x": player_x + math.cos(spawn_angle) * spawn_dist,
                "y": player_y + math.sin(spawn_angle) * spawn_dist,
                "radius": 13,
                "heal_amount": 25
            })
        for orb in health_orbs[:]:
            distance_to_player = math.hypot(orb["x"] - player_x, orb["y"] - player_y)
            if distance_to_player < (orb["radius"] + magnet) and player_health < max_health:
                angle_to_player = math.atan2(player_y - orb["y"], player_x - orb["x"])
                orb["x"] += math.cos(angle_to_player) * 6
                orb["y"] += math.sin(angle_to_player) * 6
                amount_healed = min(max_health - player_health, orb["heal_amount"])
                player_health += amount_healed

                floating_texts.append({
                    "x": player_x,
                    "y": player_y - 20,
                    "text": f"+{amount_healed}",
                    "color": (50, 255, 100),
                    "timer": 45
                })

                health_orbs.remove(orb)

        #----------------------------------------
        #----------------------------------------ENEMIES
        spawn_timer += 1
        if spawn_timer >= enemy_spawn_interval:
            spawn_timer = 0
            spawn_angle = random.uniform(0, 2 * math.pi)
            spawn_distance = random.randint(800, 1000)

            if enemies_defeated < 2:
                template = random.choices(enemy_types, weights=[90, 10, 0, 0, 0 ,0])[0]
            elif enemies_defeated == 2:
                hexagons_exist = any(
                    enemy["sides"] == 6
                    for enemy in enemies
                )

                if hexagons_exist:
                    template = random.choices(enemy_types, weights=[90, 10, 0, 0, 0, 0])[0]
                else:
                    template = enemy_types[3]
            elif enemies_defeated > 2 and enemies_defeated <= 5:
                template = random.choices(enemy_types, weights=[35, 65, 10, 0, 0, 0])[0]
            else:
                template = random.choices(enemy_types, weights=[0, 0, 10, 0, 85, 5])[0]
                
            enemies.append({
                "x": player_x + math.cos(spawn_angle) * spawn_distance,
                "y": player_y + math.sin(spawn_angle) * spawn_distance,
                "speed": template["speed"],
                "radius": template["radius"],
                "health": template["health"],
                "xp": template["xp"],
                "color": template["color"],
                "sides": template["sides"],
                "damage": template["damage"],
                "boss": template["boss"], 
                "hit_timers": {}
            })

        for enemy in enemies[:]:
            for w_id in list(enemy["hit_timers"].keys()):
                if enemy["hit_timers"][w_id] > 0:
                    enemy["hit_timers"][w_id] -= 1

            if enemy.get("hit_flash", 0) > 0:
                enemy["hit_flash"] -= 1

        is_colliding = False
        for i, enemy in enumerate(enemies[:]):
            dx = player_x - enemy["x"]
            dy = player_y - enemy["y"]
            distance = math.hypot(dx, dy)

            if distance > 1:
                dx /= distance
                dy /= distance
                enemy["x"] += dx * enemy["speed"]
                enemy["y"] += dy * enemy["speed"]

            for j, other_enemy in enumerate(enemies):
                if i != j:
                    ex_diff = enemy["x"] - other_enemy["x"]
                    ey_diff = enemy["y"] - other_enemy["y"]
                    e_dist = math.hypot(ex_diff, ey_diff)
                    min_dist = enemy["radius"] + other_enemy["radius"]

                    if e_dist < min_dist and e_dist > 0:
                        push = (min_dist - e_dist) / 2
                        ex_diff /= e_dist
                        ey_diff /= e_dist
                        enemy["x"] += ex_diff * push
                        enemy["y"] += ey_diff * push

            if distance < (15 + enemy["radius"]):
                is_colliding = True

                knockback = 40
                if distance > 0:
                    enemy["x"] -= (dx / distance) * knockback
                    enemy["y"] -= (dx / distance) * knockback

        if i_frames > 0:
            i_frames -= 1

        if player_health <= 0:
            game_state = "GAME_OVER"

        if is_colliding and i_frames == 0:
            player_health -= enemy["damage"]
            i_frames = max_frame_rate / 3


        for enemy in enemies:
            if enemy["boss"] == True:
                screen_ex = enemy["x"] - camera_x
                screen_ey = enemy["y"] - camera_y

                if screen_ex < -20 - enemy["radius"]:
                    enemy["x"] = camera_x + screen_width + enemy["radius"] + 20
                elif screen_ex > screen_width + enemy["radius"] + 20:
                    enemy["x"] = camera_x - enemy["radius"] - 20 

                if screen_ey < -20 - enemy["radius"]:
                    enemy["y"] = camera_y + screen_height + enemy["radius"] + 20
                elif screen_ey > screen_height + enemy["radius"] + 20:
                    enemy["y"] = camera_y - enemy["radius"] - 20

        for d in dying_enemies[:]:
            d["fade_timer"] -= 1
            d["radius"] = max(1, d["radius"] - 0.3)
            if d["fade_timer"] <= 0:
                dying_enemies.remove(d)

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
            pygame.draw.circle(screen, p["color"], (p["x"] - camera_x, p["y"] - camera_y), p["radius"])

        # XP ORBS
        for orb in xp_orbs:
            orb_screen_x = orb["x"] - camera_x
            orb_screen_y = orb["y"] - camera_y
            pygame.draw.circle(screen, (0, 150, 255), (orb_screen_x, orb_screen_y), orb["radius"])
            pygame.draw.circle(screen, (255, 255 ,255), (orb_screen_x, orb_screen_y), math.sqrt(2) * orb["radius"] / 2)

        # HEALTH ORBS
        for orb in health_orbs:
            orb_screen_x = orb["x"] - camera_x
            orb_screen_y = orb["y"] - camera_y
            pygame.draw.circle(screen, (50, 255, 100), (orb_screen_x, orb_screen_y), orb["radius"])
            pygame.draw.circle(screen, (255, 255 ,255), (orb_screen_x, orb_screen_y), math.sqrt(2) * orb["radius"] / 2)

        # ENEMIES
        for enemy in enemies:
            ex = enemy["x"] - camera_x
            ey = enemy["y"] - camera_y
            r = enemy["radius"]
            num_sides = enemy["sides"]
            rotation_offset = math.radians(45) if num_sides == 4 else 0

            if enemy.get("hit_flash", 0) > 0:
                render_color = (255, 50, 50)
            else:
                render_color = enemy["color"]

            points = []
            points_two = []
            for k in range(num_sides):
                angle = (2 * math.pi * k / num_sides) - math.pi / 2 + rotation_offset
                px = ex + r * math.cos(angle)
                py = ey + r * math.sin(angle)
                points.append((px, py))
                px_two = px / 2
                py_two = py * math.sqrt(2) / 2
                points_two.append((px_two, py_two))

            pygame.draw.polygon(screen, render_color, points)
          #  pygame.draw.polygon(screen, (0, 0, 0), points_two)

        for d in dying_enemies:
            dx = int(d["x"] - camera_x)
            dy = int(d["y"] - camera_y)
            r = int(d["radius"])
            if r <= 0:
                continue

            surf_size = r * 4
            surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)

            alpha = int(255 * (d["fade_timer"] / d["max_fade"]))
            fade_color = (d["color"][0], d["color"][1], d["color"][2], alpha)

            points = []
            for k in range (d["sides"]):
                if d["sides"] == 4:
                        angle = (2 * math.pi * k / d["sides"]) - (math.pi / 2)
                else:
                    angle = (2 * math.pi * k / d["sides"]) - (math.pi / 2) + math.radians(45)
                px = (surf_size / 2) + r * math.cos(angle)
                py = (surf_size / 2) + r * math.sin(angle)
                points.append((px, py))

            pygame.draw.polygon(surf, fade_color, points)
            screen.blit(surf, (dx - surf_size // 2, dy - surf_size // 2))

        # HEALTH BAR AND XP LEVEL
        bar_width = 300
        bar_height = 20
        bar_x = 50
        bar_y = 50
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        current_health_width = int(bar_width * (player_health / max_health))
        pygame.draw.rect(screen, (50, 200, 50), (bar_x, bar_y, current_health_width, bar_height))
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)

        level_surface = font_small.render(f"Level: {player_level} XP: {player_xp}/{next_level}", True, (0, 200, 255))
        screen.blit(level_surface, (bar_x, bar_y + 30))

        # FPS COUNTER
        fps_surface = font_small.render(f"FPS: {round(clock.get_fps(), 1)}", True, (255, 255, 255))
        screen.blit(fps_surface, (screen_width - 150, 30))\

        # TIMER
        total_seconds = game_time_frames // max_frame_rate
        mins = total_seconds // 60
        seconds = total_seconds % 60

        time_surface = pygame.font.SysFont(None, 50).render(f"{mins:02}:{seconds:02}", True, (255, 255 ,255))
        screen.blit(time_surface, ((screen_width - time_surface.get_width()) // 2, 30))

        # KILLS
        kills_surf = font_small.render(f"Enemies Defeated: {enemies_defeated}", True, (255, 50, 50))
        kills_x = screen_width - kills_surf.get_width() - 30
        kills_y = screen_height - kills_surf.get_height() - 30
        screen.blit(kills_surf, (kills_x, kills_y))

        # FLOATING TEXT
        for ft in floating_texts[:]:
            ft["y"] -= 0.7
            ft["timer"] -= 1
            if ft["timer"] <= 0:
                floating_texts.remove(ft)
        for ft in floating_texts:
            fx = int(ft["x"] - camera_x)
            fy = int(ft["y"] - camera_y)

            text_surf = font_small.render(ft["text"], True, ft["color"])
            screen.blit(text_surf, (fx - text_surf.get_width() // 2, fy))
        #----------------------------------------

    elif game_state == "LEVEL_UP":
        # def select_upgrade(index):
        #     global game_state, max_health, magnet, player_health
        #     if index < len(current_choices):
        #         choice = current_choices[index]
        #         if choice["target"] == "player":
        #             if choice["state"] == "health":
        #                 max_health += choice["val"]
        #                 player_health = min(max_health, player_health + choice["val"])
        #             elif choice["staat"] == "magnet":
        #                 magnet += choice["val"]
        #         else:
        #             for w in equipped_weapons:
        #                 if w["name"] == choice["target"]:
        #                     w[choice["stat"]] = max(5, w[choice["stat"]] + choice ["val"])
        #                 else:
        #                     w[choice["stat"]] += choice["val"]
        #         # game_state = "PLAYING"

        #         if len(level_queue) > 0:
        #             level_queue.pop(0)

        #         if len(level_queue) > 0:
        #             current_choices = random.sample(upgrade_pool, min(3, len(upgrade_pool)))
        #             game_state = "LEVEL_UP"
        #         else:
        #             game_state = "PLAYING"




        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        title_surf = font_large.render("Level UP!", True, (0, 255, 200))
        screen.blit(title_surf, (screen_width // 2 - title_surf.get_width() // 2, 250))

        sub_surf = font_small.render("Choose an Upgrade:", True, (200, 200, 200))
        screen.blit(sub_surf, (screen_width // 2 - sub_surf.get_width(), 330))

        box_width, box_height = 500, 80
        start_y = 400
        for i, choice in enumerate(current_choices):
            box_y = start_y + i * 100
            box_x = (screen_width - box_width) // 2

            pygame.draw.rect(screen, (50, 50, 70), (box_x, box_y, box_width, box_height), border_radius = 8)
            pygame.draw.rect(screen, (0, 200, 255), (box_x, box_y, box_width, box_height), border_radius = 8)

            option_text = font_small.render(f"[{i + 1}] {choice["title"]}", True, (255, 255, 255))
            screen.blit(option_text, (box_x + 30, box_y + 25))

    elif game_state == "GAME_OVER":

        over_surf = font_large.render('GAME OVER', True, (255, 50, 50))
        restart_surf = font_small.render('Press [R] to restart or [ESC] to Quit', True, (200, 200, 200))
        screen.blit(over_surf, (screen_width // 2 - over_surf.get_width() // 2, screen_height // 2 - 100))
        screen.blit(restart_surf, (screen_width // 2 - restart_surf.get_width() // 2, screen_height // 2))
    

    pygame.display.flip()
    clock.tick(max_frame_rate)

pygame.quit()