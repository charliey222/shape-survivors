import pygame
import random
import math
import re
import json

screen_width = 1920
screen_height = 1080
max_frame_rate = 144

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Shape Survivors")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont(None, 36)
font_medium = pygame.font.SysFont(None, 48)
font_large = pygame.font.SysFont(None, 72)

game_state = "START"

chars = [
    {
        "name": "Scout",
        "desc": "High mobility, lower health. Starts with Spheres.",
        "color": (0, 200, 255),
        "max_health": 100,
        "regen": 0.5,
        "speed": 2.5,
        "magnet": 75,
        "starting_weapons": [{"id": "sphere", "name": "Sphere", "damage": 10, "cooldown": 0, "interval": max_frame_rate / 2.5, "speed": 7, "radius": 6, "color": (255, 255, 0), "range": 500}]
    },
    {
        "name": "Ranger",
        "desc": "High damage and range, lower mobility. Starts with Line Segment.",
        "color": (80, 200, 120),
        "max_health": 85,
        "regen": 0.5,
        "speed": 1.8,
        "magnet": 80,
        "starting_weapons": [{"id": "line_segment", "name": "Line Segment", "damage": 20, "cooldown": 0, "interval": max_frame_rate * 2, "speed": 0, "radius": 3, "color": (80, 200, 120)}]
    },
    {
        "name": "Juggernaut",
        "desc": "High health and low mobility. Starts with Field",
        "color": (255, 100, 100),
        "max_health": 300,
        "regen": 0.5,
        "speed": 1.5,
        "magnet": 75,
        "starting_weapons": [{"id": "field", "name": "Field", "damage": 10, "cooldown": 0, "interval": max_frame_rate, "speed": 0, "radius": 30, "color": (144, 238, 144)}]
    }
]

selected_char_index = 0

enemy_types = [
    {"type": "triangle", "sides": 3, "speed": 1.4, "radius": 20, "health": 15, "xp": 10, "damage": 5, "color": (0, 255, 0), "boss": False}, 
    {"type": "square", "sides" : 4, "speed": 0.8, "radius": 35, "health": 60, "xp": 13, "damage": 8, "color": (30, 30, 120), "boss": False},
    {"type": "pentagon", "sides": 5, "speed": 3, "radius": 16, "health": 10, "xp": 12, "damage": 10, "color": (48, 25, 52), "boss": False},
    {"type": "hexagon", "sides": 6, "speed": 0.6, "radius": 60, "health": 200, "xp": 100, "damage": 20, "color": (255, 165, 0), "boss": True},
    {"type": "septagon", "sides": 7, "speed": 1.5, "radius": 20, "health": 45, "xp": 15, "damage": 7, "color": (255, 20, 147), "boss": False},
    {"type": "octagon", "sides": 8, "speed": 1.1, "radius": 40, "health": 80, "xp": 20, "damage": 14, "color": (128, 128, 128), "boss": False}
]

equipped_weapons = []

weapon_unlock_pool = [{"title": "Unlock Shrapnel", "target": "new_weapon", "id": "sharpnel", "name": "Shrapnel", "damage": 5, "cooldown": 0, "interval": max_frame_rate, "speed": 30,
        "radius": 5,
        "color": (128, 128, 128)
    },
    {
        "title": "Unlock Thunder",
        "target": "new_weapon",
        "id": "thunder",
        "name": "Thunder",
        "damage": 10,
        "cooldown": 0,
        "interval": max_frame_rate * 2,
        "speed": 0,
        "radius": 0,
        "color": (173, 216, 230)
    }
]

upgrade_pool = [
    # sphere
    {"title": "Sphere Damage +10%", "target": "sphere", "stat": "damage", "val": 0.1},
    {"title": "Sphere Cooldown -5%", "target": "sphere", "stat": "interval", "val": -0.05},
    {"title": "Sphere Radius +10%", "target": "sphere", "stat": "radius", "val": 0.1},
    {"title": "Sphere Range +20%", "target": "sphere", "stat": "range", "val": 0.2},

    # line segment
    {"title": "Line Segment Damage +10%", "target": "line_segment", "stat": "damage", "val": 0.1},
    {"title": "Line Segment Cooldown -5%", "target": "line_segment", "stat": "interval", "val": -0.05},
    {"title": "Line Segment Radius +10%", "target": "line_segment", "stat": "radius", "val": 0.1},
    {"title": "Line Segment Lifespan +30", "target": "line_segment", "stat": "lifespan", "val": 30},

    # field
    {"title": "Field Radius +10%", "target": "field", "stat": "radius", "val": 0.1},
    {"title": "Field Damage +10%", "target": "field", "stat": "damage", "val": 0.1},

    {"title": "Shrapnel Damage +20%", "target": "sharpnel", "stat": "damage", "val": 0.2},
    {"title": "Shrapnel Range +30%", "target": "shrapnel", "stat": "range", "val": 0.3},
    {"title": "Shrapnel Cooldown -10%", "target": "sharpnel", "stat": "interval", "val": -0.05},


    #player upgrades
    {"title": "Max Player Health +10%", "target": "player", "stat": "health", "val": 0.1},
    {"title": "Player Regen +5%", "target": "player", "stat": "regen", "val": 0.05},
    {"title": "Player Speed +10%", "target": "player", "stat": "speed", "val": 0.1},
]

current_choices = []

def reset_game():
    global game_time_frames, player_x, player_y, player_health, player_regen, i_frames, regen_timer, player_speed, magnet, max_health, player_xp, player_level, next_level, enemies_defeated, health_world_spawn_timer, equipped_weapons, next_health_orb
    global base_speed, base_max_health, base_magnet, base_regen, health_bonus, regen_bonus, speed_bonus, magnet_bonus
    game_time_frames = 0
    player_x = screen_width / 2
    player_y = screen_height / 2
    i_frames = 0
    regen_timer = 0
    player_xp = 0
    player_level = 1
    next_level = 50
    enemies_defeated = 0
    health_world_spawn_timer = 0
    next_health_orb = 0

    char = chars[selected_char_index]
    base_max_health = char["max_health"]
    base_regen = char["regen"]
    base_speed = char["speed"]
    base_magnet = char["magnet"]

    health_bonus = 0.0
    regen_bonus = 0.0
    speed_bonus = 0.0
    magnet_bonus = 0.0

    max_health = base_max_health
    player_health = max_health
    player_regen = base_regen
    player_speed = base_speed
    magnet = base_magnet

    equipped_weapons = []
    for w in char["starting_weapons"]:
        w_copy = dict(w)
        w_copy["base_damage"] = w_copy["damage"]
        w_copy["base_interval"] = w_copy["interval"]
        w_copy["base_radius"] = w_copy["radius"]
        w_copy["damage_bonus"] = 0.0
        w_copy["interval_bonus"] = 0.0
        w_copy["radius_bonus"] = 0.0
        if "lifespan" in w:
            w_copy["base_lifespan"] = w_copy["lifespan"]
            w_copy["lifespan_bonus"] = 0.0
        if "range" in w:
            w_copy["base_range"] = w_copy["range"]
            w_copy["range_bonus"] = 0.0
        equipped_weapons.append(w_copy)

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

def save_game():
    save_data = {
        "selected_char_index": selected_char_index,
        "player_level": player_level,
        "player_xp": player_xp,
        "next_level": next_level,
        "max_health": max_health,
        "player_health": player_health,
        "player_speed": player_speed,
        "player_regen": player_regen,
        "magnet": magnet,
        "enemies_defeated": enemies_defeated,
        "equipped_weapons": equipped_weapons,
        "game_time_frames": game_time_frames
    }

    with open("save.json", "w") as f:
        json.dump(save_data, f, indent=4)
def load_game():
    global selected_char_index, player_level, player_xp, next_level
    global max_health, player_health, player_speed, player_regen, magnet
    global enemies_defeated, equipped_weapons, game_state, game_time_frames

    try:
        with open("save.json", "r") as f:
            save_data = json.load(f)
            selected_char_index = save_data["selected_char_index"]
            player_level = save_data["player_level"]
            player_xp = save_data["player_xp"]
            next_level = save_data["next_level"]
            max_health = save_data["max_health"]
            player_health = save_data["player_health"]
            player_speed = save_data["player_speed"]
            player_regen = save_data["player_regen"]
            magnet = save_data["magnet"]
            enemies_defeated = save_data["enemies_defeated"]
            equipped_weapons = save_data["equipped_weapons"]
            game_time_frames = save_data["game_time_frames"]
            game_state = "PLAYING"
    except:
        print("No save file found")


def select_upgrade(index):
    global game_state, max_health, magnet, player_health, player_regen, player_speed, current_choices, level_queue
    global base_speed, base_max_health, base_magnet, base_regen
    global speed_bonus, health_bonus, magnet_bonus, regen_bonus
    if index < len(current_choices):
        choice = current_choices[index]

        if choice.get("target") == "new_weapon":
            equipped_weapons.append({"id": choice["id"], "name": choice["name"], "base_damage": choice["damage"], "base_interval": choice["interval"], "base_radius": choice["radius"], "damage": choice["damage"], "cooldown": 0, "interval": choice["interval"], "speed": choice["speed"], "radius": choice["radius"], "color": choice["color"], "damage_bonus": 0.0, "interval_bonus": 0.0, "radius_bonus": 0.0})
            if choice in weapon_unlock_pool:
                weapon_unlock_pool.remove(choice)

        elif choice["target"] == "player":
            if choice["stat"] == "health":
                health_bonus += choice["val"]
                max_health = round(base_max_health * (1 + health_bonus), 1)
                if max_health % 1 == 0:
                    max_health = int(max_health)
            elif choice["stat"] == "magnet":
                magnet_bonus = choice["val"]
                magnet = base_magnet * (1 + magnet_bonus)
            elif choice["stat"] == "speed":
                speed_bonus += choice["val"]
                player_speed = base_speed * (1 + speed_bonus)
            elif choice["stat"] == "regen":
                regen_bonus += choice["val"]
                player_regen = base_regen * (1 + player_regen)

        else:
            for w in equipped_weapons:
                if w["id"] == choice["target"]:
                    if choice["stat"] == "damage":
                        w["damage_bonus"] += choice["val"]
                        w["daamage"] = w["damage_bonus"] * (1 + w["damage_bonus"])
                    elif choice["stat"] == "interval":
                        w["interval_bonus"] += choice["val"]
                        w["interval"] = max(10, int(w["base_interval"] * (1 + w["interval_bonus"])))
                    elif choice["stat"] == "radius":
                        w["radius_bonus"] += choice["val"]
                        w["radius"] = w["base_radius"] * (1 + w["radius_bonus"])
                    elif choice["stat"] == "range":
                        w["range_bonus"] += choice["val"]
                        w["range"] = w["base_radius"] * (1 + w["range_bonus"])
                    elif choice["stat"] == "lifespan":
                        w["lifespan_bonus"] += choice["val"]
                        w["lifespan"] = w["base_lifespan"] * (1 + w["lifespan_bonus"])

        if len(level_queue) > 0:
            level_queue.pop(0)
        if len(level_queue) > 0:
            valid_upgrades = [
                up for up in upgrade_pool
                if up["target"] == "player" or up["target"] in [w["id"] for w in equipped_weapons]
            ]
            current_choices = random.sample(valid_upgrades, min (3, len(valid_upgrades)))
            game_state = "LEVEL_UP"
        else:
            game_state = "PLAYING"


global selected_upgrade_index
selected_upgrade_index = 0
# load_game()
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
                save_game()
                running = False

            if event.key == pygame.K_e:
                spawn_angle = random.uniform(0, 2 * math.pi)
                spawn_distance = 500
                template = enemy_types[0]

                enemies.append({"x": player_x + math.cos(spawn_angle) * spawn_distance, "y": player_y + math.sin(spawn_angle) * spawn_distance, "speed": template["speed"], "radius": template["radius"], "health": template["health"], "xp": template["xp"], "color": template["color"], "sides": template["sides"], "damage": template["damage"], "boss": False, "hit_timers": {}})

            if game_state == "START":
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    selected_char_index = (selected_char_index - 1) % len(chars)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected_char_index = (selected_char_index + 1) % len (chars)
                elif event.key in (pygame.K_1, pygame.K_KP1):
                    selected_char_index = 0
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    selected_char_index = 1
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    selected_char_index = 2
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    reset_game()
                    game_state = "PLAYING"

            elif game_state == "LEVEL_UP":
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    selected_upgrade_index = (selected_upgrade_index - 1) % len(current_choices)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected_upgrade_index = (selected_upgrade_index + 1) % len(current_choices)
                elif event.key in (pygame.K_1, pygame.K_KP1):
                    select_upgrade(0)
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    select_upgrade(1)
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    select_upgrade(2)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    select_upgrade(selected_upgrade_index)

            elif game_state == "GAME_OVER":
                if event.key == pygame.K_r:
                    reset_game()
                    game_state = "PLAYING"

            elif game_state == "PLAYING":
                if event.key == pygame.K_TAB:
                    game_state = "PAUSED"

            elif game_state == "PAUSED":
                if event.key == pygame.K_TAB:
                    game_state = "PLAYING"



    if game_state == "START":
        #----------------------------------------NEW CODE
        screen.fill((30, 30, 30))

        title_surf = font_large.render("SHAPE SURVIVORS", True, (0, 255, 150))
        screen.blit(title_surf, ((screen_width - title_surf.get_width()) // 2, 80))

        sub_surf = font_small.render("Select Your Character", True, (200, 200, 200))
        screen.blit(sub_surf, ((screen_width - sub_surf.get_width()) // 2, 160))

        card_width, card_height = 360, 420
        total_width = len(chars) * card_width + (len(chars) - 1) * 40
        start_x = (screen_width - total_width) // 2
        card_y = 250

        for i, char in enumerate(chars):
            cx = start_x + i * (card_width + 40)
            is_selected = (i == selected_char_index)

            bg_color = (40, 45, 65) if not is_selected else (60, 70, 100)
            border_color = (0, 255, 200) if is_selected else (80, 80, 100)
            border_thick = 4 if is_selected else 2

            pygame.draw.rect(screen, bg_color, (cx, card_y, card_width, card_height), border_radius=12)
            pygame.draw.rect(screen, border_color, (cx, card_y, card_width, card_height), border_thick, border_radius=12)

            pygame.draw.circle(screen, char["color"], (cx + card_width // 2, card_y + 80), 35)

            name_surf = font_medium.render(char["name"], True, (255, 255 ,255)) if not is_selected else font_medium.render(char["name"], True, (240, 60, 60))
            screen.blit(name_surf, (cx + (card_width - name_surf.get_width()) // 2, card_y + 135))

            weapon_name = char["starting_weapons"][0]["name"]
            weapon_surf = font_small.render(f"Starting Weapon: {weapon_name}", True, (255, 215, 0))
            screen.blit(weapon_surf, (cx + (card_width - weapon_surf.get_width()) // 2, card_y + 185))

            hp_surf = font_small.render(f"HP: {char['max_health']}({char['regen']})", True, (255, 255, 255))
            speed_surf = font_small.render(f"Speed: {char["speed"]}", True, (100, 200, 255))
            magnet_surf = font_small.render(f"Magnet: {char["magnet"]}", True, (200, 150, 255))

            screen.blit(hp_surf, (cx + 40, card_y + 230))
            screen.blit(speed_surf, (cx + 40, card_y + 265))
            screen.blit(magnet_surf, (cx + 40, card_y + 300))

            desc_words = char["desc"].split(" ")
            line1 = " ".join(desc_words[:len(desc_words)//2])
            line2 = " ".join(desc_words[len(desc_words)//2:])
            d1_surf = font_small.render(line1, True, (170, 170, 170))
            d2_surf = font_small.render(line2, True, (170, 170, 170))
            screen.blit(d1_surf, (cx + (card_width - d1_surf.get_width()) // 2, card_y + 345))
            screen.blit(d2_surf, (cx + (card_width - d2_surf.get_width()) // 2, card_y + 375))

        prompt_surf = font_medium.render("Press [SPACE] or [ENTER] to Start", True, (255, 255 ,255))
        screen.blit(prompt_surf, ((screen_width - prompt_surf.get_width()) // 2, screen_height - 180))

        
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
                player_health = round(min(max_health, player_health + player_regen), 1)
                regen_timer = 0
        else:
            regen_timer = 0
        #----------------------------------------

        #----------------------------------------WEAPONS
        for w in equipped_weapons:
            if w["cooldown"] > 0:
                w["cooldown"] -= 1
            else:
                if w["id"] == "line_segment":
                    closest_enemy = None
                    min_dist = float('inf')
                    for enemy in enemies:
                        dist = math.hypot(enemy["x"] - player_x, enemy["y"] - player_y)
                        if dist < min_dist:
                            min_dist = dist
                            closest_enemy = enemy
                    if closest_enemy:
                        edx = closest_enemy["x"] - player_x
                        edy = closest_enemy["y"] - player_y
                        edist = math.hypot(edx, edy)
                        aim_x = edx / edist if edist > 0 else facing_x
                        aim_y = edy / edist if edist > 0 else facing_y
                    else:
                        aim_x, aim_y = facing_x, facing_y

                    projectiles.append({
                        "x": player_x,
                        "y": player_y,
                        "dx": aim_x,
                        "dy": aim_y,
                        "damage": w["damage"],
                        "speed": 0,
                        "radius": w["radius"],
                        "color": w["color"],
                        "weapon_id": w["id"],
                        "life": max_frame_rate / 10,
                        "length": 1600
                    })
                elif w["id"] == "thunder":
                    random_enemy = None
                    min_val = float('inf')
                    for enemy in enemies:
                        if math.hypot(enemy["x"] - player_x, enemy["y"] - player_y) <= 800:
                            val = random.uniform(0,1)
                            if val < min_val:
                                min_val = val
                                random_enemy = enemy
                    if random_enemy:
                        enx = random_enemy["x"] - player_x
                        eny = random_enemy["y"] - player_y
                    else:
                        enx = player_x
                        eny = player_y
                    projectiles.append({
                        "x": enx,
                        "y": eny,
                        "damage": w["damage"],
                        "speed": 0,
                        "color": w["color"],
                        "weapon_id": w["id"],
                        "life": max_frame_rate / 2
                    })
                elif w["id"] == "field":
                    projectiles.append({
                        "x": player_x,
                        "y": player_y,
                        "dx": player_x,
                        "dy": player_y,
                        "damage": w["damage"],
                        "speed": 0,
                        "radius": w["radius"],
                        "color": w["color"],
                        "weapon_id": w["id"],
                        "life": max_frame_rate + 30
                    })
                elif w["id"] == "shrapnel":
                    projectiles.append({
                        "x": player_x + 15 * facing_x,
                        "y": player_y + 15 * facing_y,
                        "x2": player_x + 15 * facing_x,
                        "y2": player_y + 15 * facing_y,
                        "x3": player_x + 15 * facing_x,
                        "y3": player_y + 15 * facing_y,
                        "dx": facing_x,
                        "dy": facing_y,
                        "damage": w["damage"],
                        "speed": w["speed"],
                        "radius": w["radius"],
                        "color": w["color"],
                        "weapon_id": w["id"],
                        "range": w["range"]
                    })
                elif w["id"] == "sphere":
                    projectiles.append({
                        "x": player_x + 15 * facing_x,
                        "y": player_y + 15 * facing_y,
                        "dx": facing_x,
                        "dy": facing_y,
                        "damage": w["damage"],
                        "speed": w["speed"],
                        "radius": w["radius"],
                        "color": w["color"],
                        "weapon_id": w["id"],
                        "range": w["range"]
                    })
                w["cooldown"] = w["interval"]


        for p in projectiles[:]:
            if p.get("weapon_id") == "line_segment":
                p["life"] -= 1
                if p["life"] <= 0:
                    projectiles.remove(p)
                    continue

                start_x, start_y = player_x, player_y
                end_x = player_x + p["dx"] * p["length"]
                end_y = player_y + p["dy"] * p["length"]

                for enemy in enemies[:]:
                    weapon_id = p["weapon_id"]
                    if enemy["hit_timers"].get(weapon_id, 0) == 0:
                        px, py = enemy["x"], enemy["y"]
                        line_len_sq = (end_x - start_x)**2 + (end_y - start_y)**2
                        if line_len_sq == 0:
                            continue
                        t = max(0, min(1, ((px - start_x) * (end_x - start_x) + (py - start_y) * (end_y - start_y)) / line_len_sq))
                        proj_x = start_x + t * (end_x - start_x)
                        proj_y = start_y + t * (end_y - start_y)
                        dist_to_line = math.hypot(px - proj_x, py - proj_y)

                        if dist_to_line <= (enemy["radius"] + p["radius"]):
                            enemy["health"] -= p["damage"]
                            enemy["hit_timers"][weapon_id] = 10
                            enemy["hit_flash"] = 16

                            if enemy["health"] <= 0:
                                enemies_defeated += 1
                                xp_orbs.append({
                                "x": enemy["x"],
                                "y": enemy["y"],
                                "radius": math.sqrt(enemy["xp"]) + 5,
                                "xp": enemy["xp"], 
                                "collected": False
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
            elif p.get("weapon_id") == "thunder":
                p["life"] -= 1
                if p["life"] <= 0:
                    projectiles.remove(p)

                for enemy in enemies[:]:
                    weapon_id = p["weapon_id"]
                    if enemy["hit_timers"].get(weapon_id, 0) == 0:
                        enemy["health"] -= p["damage"]
                        enemy["hit_timers"][weapon_id] = 15
                        enemy["hit_flash"] = 16

                        if enemy["health"] <= 0:
                            enemies_defeated += 1
                            xp_orbs.append({
                                "x": enemy["x"],
                                "y": enemy["y"],
                                "radius": math.sqrt(enemy["xp"]) + 5,
                                "xp": enemy["xp"],
                                "collected": False
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
            elif p.get("weapon_id") == "field":
                p["x"] = player_x
                p["y"] = player_y
                p["life"] -= 1
                if p["life"] <= 0:
                    projectiles.remove(p)
                    continue

                for enemy in enemies[:]:
                    weapon_id = p["weapon_id"]
                    if enemy["hit_timers"].get(weapon_id, 0) == 0:
                        dist_to_field = math.hypot(p["x"] - enemy["x"], p["y"] - enemy["y"])
                        if dist_to_field <= (p["radius"] + enemy["radius"]):
                            if enemy["hit_timers"].get(weapon_id, 0) == 0:
                                enemy["health"] -= p["damage"]
                                enemy["hit_timers"][weapon_id] = 15
                                enemy["hit_flash"] = 16

                                if enemy["health"] <= 0:
                                    enemies_defeated += 1
                                    xp_orbs.append({
                                        "x": enemy["x"],
                                        "y": enemy["y"],
                                        "radius": math.sqrt(enemy["xp"]) + 5,
                                        "xp": enemy["xp"], 
                                        "collected": False
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
            elif p.get("weapon_id") == "shrapnel":
                p["x"] += p["dx"] * p["speed"]
                p["y"] += p["dy"] * p["speed"]
                if facing_x != 0:
                    p["x2"] += p["dx"] * p["speed"]
                    p["y2"] += (p["dy"] - 0.2) * p["speed"]
                    p["x3"] += p["dx"] * p["speed"]
                    p["y3"] += (p["dy"] + 0.2) * p["speed"]
                else:
                    p["x2"] += (p["dx"] - 0.2) * p["speed"]
                    p["y2"] += p["dy"] * p["speed"]
                    p["x3"] += (p["dx"] + 0.2) * p["speed"]
                    p["y3"] += p["dy"] * p["speed"]

                if math.hypot(p["x"] - player_x, p["y"] - player_y) >= p["range"]:
                    projectiles.remove(p)

                projectile_hit = False
                for enemy in enemies[:]:
                    distance_to_enemy = math.hypot(p["x"] - enemy["x"], p["y"] - enemy["y"])
                    distance_to_enemy2 = math.hypot(p["x2"] - enemy["x"], p["y2"] - enemy["y"])
                    distance_to_enemy3 = math.hypot(p["x3"] - enemy["x"], p["y3"] - enemy["y"])
                    if distance_to_enemy <= (p["radius"] + enemy["radius"]) or distance_to_enemy2 <= p["radius"] + enemy["radius"] or distance_to_enemy3 <= p["radius"] + enemy["radius"]:
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
                                        "xp": enemy["xp"], 
                                        "collected": False
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

                if projectile_hit == True and p in projectiles:
                    projectiles.remove(p)

            elif p.get("weapon_id") == "sphere":
                p["x"] += p["dx"] * p["speed"]
                p["y"] += p["dy"] * p["speed"]

                if math.hypot(p["x"] - player_x, p["y"] - player_y) >= p["range"]:
                    projectiles.remove(p)

                projectile_hit = False
                for enemy in enemies[:]:
                    distance_to_enemy = math.hypot(p["x"] - enemy["x"], p["y"] - enemy["y"])
                    if distance_to_enemy <= (p["radius"] + enemy["radius"]):
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
                                        "xp": enemy["xp"], 
                                        "collected": False
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

                if projectile_hit == True and p in projectiles:
                    projectiles.remove(p)

        #----------------------------------------
    
        #----------------------------------------XP
        for orb in xp_orbs[:]:
            distance_to_player = math.hypot(orb["x"] - player_x, orb["y"] - player_y)
            if distance_to_player <= magnet or orb["collected"] == True:
                angle_to_player = math.atan2(player_y - orb["y"], player_x - orb["x"])
                orb["x"] += math.cos(angle_to_player) * 2
                orb["y"] += math.sin(angle_to_player) * 2
                orb["collected"] = True
                if distance_to_player <= orb["radius"] + 15:
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

                        if player_level == 5:
                            current_choices = random.sample(weapon_unlock_pool, min(3, len(weapon_unlock_pool)))
                        else:
                            valid_upgrades = [
                                up for up in upgrade_pool
                                if up["target"] == "player" or up["target"] in [w["id"] for w in equipped_weapons]
                            ]                           
                            current_choices = random.sample(valid_upgrades, min (3, len(valid_upgrades)))
                        level_queue.append(True)
                    if len(level_queue) > 0 and game_state == "PLAYING":
                        game_state = "LEVEL_UP"
                    break

        #----------------------------------------HEALTH
        health_world_spawn_timer += 1
        if next_health_orb == 0:
            next_health_orb = max_frame_rate * random.uniform(10, 30)
        if health_world_spawn_timer >= next_health_orb:
            health_world_spawn_timer = 0
            next_health_orb = 0
            spawn_angle = random.uniform(0, 2 * math.pi)
            spawn_dist = random.randint(500, 900)

            health_orbs.append({
                "x": player_x + math.cos(spawn_angle) * spawn_dist,
                "y": player_y + math.sin(spawn_angle) * spawn_dist,
                "radius": 13,
                "heal_amount": 25,
                "collected": False
            })
        for orb in health_orbs[:]:
            distance_to_player = math.hypot(orb["x"] - player_x, orb["y"] - player_y)
            if distance_to_player <= magnet or orb["collected"] == True:
                angle_to_player = math.atan2(player_y - orb["y"], player_x - orb["x"])
                orb["x"] += math.cos(angle_to_player) * 2
                orb["y"] += math.sin(angle_to_player) * 2
                orb["collected"] = True
                if distance_to_player <= orb["radius"] + 15:
                    amount_healed = min(max_health - player_health, orb["heal_amount"])
                    player_health += amount_healed

                    floating_texts.append({
                        "x": player_x,
                        "y": player_y - 20,
                        "text": f"+{round(amount_healed, 1)}",
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
            hexagons_exist = any(
                enemy["sides"] == 6
                for enemy in enemies
            )
            if total_seconds < 180:
                template = random.choices(enemy_types, weights=[90, 10, 0, 0, 0 ,0])[0]
            elif total_seconds >= 180 and total_seconds <= 185:
                if hexagons_exist:
                    template = random.choices(enemy_types, weights=[90, 10, 0, 0, 0, 0])[0]
                else:
                    template = enemy_types[3]
            elif total_seconds > 185 and total_seconds < 360 and not hexagons_exist:
                template = random.choices(enemy_types, weights=[35, 65, 10, 0, 0, 0])[0]
            elif total_seconds >= 360 and not hexagons_exist:
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

        # PROJECTILES
        for p in projectiles:
            if p["weapon_id"] == "line_segment":
                start_x = player_x - camera_x
                start_y = player_y - camera_y
                end_x = player_x - camera_x + p["dx"] * p["length"]
                end_y = player_y - camera_y + p["dy"] * p["length"]
                pygame.draw.line(screen, p["color"], (start_x, start_y), (end_x, end_y), 6)
            elif p["weapon_id"] == "thunder":
                pygame.draw.circle(screen, p["color"], (enemy["x"] - camera_x, enemy["y"] - camera_y), 20)
            elif p["weapon_id"] == "field":
                cx = p["x"] - camera_x
                cy = p["y"] - camera_y
 
                surf = pygame.Surface((p["radius"] * 2, p["radius"] * 2), pygame.SRCALPHA)
                alpha_color = (p["color"][0], p["color"][1], p["color"][2], 50)
                pygame.draw.circle(surf, alpha_color, (p["radius"], p["radius"]), p["radius"])
                screen.blit(surf, (cx - p["radius"], cy - p["radius"]))
            elif p["weapon_id"] == "shrapnel":
                pygame.draw.circle(screen, p["color"], (p["x"] - camera_x, p["y"] - camera_y), p["radius"])
                pygame.draw.circle(screen, p["color"], (p["x2"] - camera_x, p["y2"] - camera_y), p["radius"])
                pygame.draw.circle(screen, p["color"], (p["x3"] - camera_x, p["y3"] - camera_y), p["radius"])
            elif p["weapon_id"] == "sphere":
                pygame.draw.circle(screen, p["color"], (p["x"] - camera_x, p["y"] - camera_y), p["radius"])

        # PLAYER
        if i_frames > 0:
            if (i_frames // (max_frame_rate / 7)) % 2 == 0:
                player_color = (150, 50, 50)
            else:
                player_color = (255, 0, 0)
        else:
            player_color = (144, 11, 11)

        pygame.draw.circle(screen, player_color, (player_x - camera_x, player_y - camera_y), 15)

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

        if player_health % 1 == 0 and player_health == max_health:
            current_health = pygame.font.SysFont(None, 30).render(f"{int(player_health)}/{max_health}", True, (255, 255 ,255))
        elif player_health % 1 == 0:
            current_health = pygame.font.SysFont(None, 30).render(f"{int(player_health)}/{max_health}", True, (200, 20, 20))
        else:
            current_health = pygame.font.SysFont(None, 30).render(f"{player_health}/{max_health}", True, (200, 20, 20))
        screen.blit(current_health, (bar_x + (bar_width - current_health.get_width()) // 2, bar_y))

        level_surface = font_small.render(f"Level: {player_level} XP: {player_xp}/{next_level}", True, (0, 200, 255))
        screen.blit(level_surface, (bar_x, bar_y + 30))

        # FPS COUNTER
        fps_surface = font_small.render(f"FPS: {round(clock.get_fps(), 1)}", True, (255, 255, 255))
        screen.blit(fps_surface, (screen_width - 150, 30))            

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

        # MINI MAP
        map_size = 100
        map_x = 50
        map_y = screen_height - map_size - 50
        map_radius = 800

        minimap_surf = pygame.Surface((map_size, map_size), pygame.SRCALPHA)
        minimap_surf.fill((20, 20, 30, 180))

        scale = map_size / (map_radius * 2)
        center_offset = map_size / 2

        for orb in health_orbs:
            rx = (orb["x"] - player_x) * scale + center_offset
            ry = (orb["y"] - player_y) * scale + center_offset
            if 0 <= rx <= map_size and 0<= ry <= map_size:
                pygame.draw.circle(minimap_surf, (50, 225, 100), (int(rx), int(ry)), 3)
        for enemy in enemies:
            rx = (enemy["x"] - player_x) * scale + center_offset
            ry = (enemy["y"] - player_y) * scale + center_offset
            if 0 <= rx <= map_size and 0 <= ry <= map_size:
                color = (255, 80, 80) if not enemy.get("boss") else (255, 165, 0)
                blip_size = 2 if not enemy.get("boss") else 4
                pygame.draw.circle(minimap_surf, color, (int(rx), int(ry)), blip_size)

        pygame.draw.circle(minimap_surf, (255, 255, 255), (int(center_offset), int(center_offset)), 3)
        pygame.draw.rect(minimap_surf, (100, 100, 120), (0, 0, map_size, map_size), 2, border_radius=8)
        
        screen.blit(minimap_surf, (map_x, map_y))

        coords_surf_x = pygame.font.SysFont(None, 20).render(f"X: {camera_x}", True, (255, 255, 255))
        coords_surf_y = pygame.font.SysFont(None, 20).render(f"Y: {-camera_y}", True, (255, 255 ,255))
        screen.blit(coords_surf_x, (50, screen_height - 50))
        screen.blit(coords_surf_y, (100, screen_height - 50))

        #----------------------------------------

    elif game_state == "LEVEL_UP":
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((20, 20, 30, 220))
        screen.blit(overlay, (0, 0))

        title_surf = font_large.render("Level Up!", True, (255, 215, 0))
        screen.blit(title_surf, (screen_width // 2 - title_surf.get_width() // 2, 100))


        card_width, card_height = 360, 420
        total_width = len(current_choices) * card_width + (len(current_choices) - 1)
        start_x = (screen_width - total_width) // 2
        card_y = 260

        selected_upgrade_index = min(selected_upgrade_index, len(current_choices) - 1)
        for i, choice in enumerate(current_choices):
            cx = start_x + i * (card_width + 40)
            is_selected = (i == selected_upgrade_index)

            bg_color = (40, 45, 65) if not is_selected else (60, 70, 100)
            border_color = (0, 255, 200) if is_selected else (80, 80, 100)
            border_thick = 4 if is_selected else 2

            pygame.draw.rect(screen, bg_color, (cx, card_y, card_width, card_height), border_radius=12)
            pygame.draw.rect(screen, border_color, (cx, card_y, card_width, card_height), border_thick, border_radius=12)

            num_surf = font_large.render(f"[{i + 1}]", True, (255, 215, 0))
            screen.blit(num_surf, (cx + (card_width - num_surf.get_width()) // 2, card_y + 35))

            upgrade_name_surf = font_medium.render(choice["title"], True, (255 ,255 ,255))
            screen.blit(upgrade_name_surf, (cx + (card_width - upgrade_name_surf.get_width()) // 2, card_y + 120))

            target_color = (100, 200, 255) if choice['target'] == "player" else (255, 180, 50)
            target_surf = font_small.render(re.sub(r'[^a-zA-Z ]', ' ', choice['target'].upper()), True, target_color)
            screen.blit(target_surf, (cx + (card_width - target_surf.get_width()) // 2, card_y + 180))

            if choice.get("target") == "new_weapon":
                detail_surf = font_small.render("WEAPON UNLOCK", True, (200, 200, 200))
                val_surf = font_medium.render("Equip Active", True, (255, 100, 255))
            else:
                stat_name = choice["stat"].upper()
                val_str = f"+{100 * choice['val']}%" if choice["val"] > 0 else f"{choice["val"]}"
                detail_surf = font_small.render(stat_name, True, (200, 200, 200))
                val_surf = font_medium.render(val_str, True, (50, 255, 100))

            screen.blit(detail_surf, (cx + (card_width - detail_surf.get_width()) // 2, card_y + 240))
            screen.blit(val_surf, (cx + (card_width - val_surf.get_width()) // 2, card_y + 280))


    elif game_state == "PAUSED":

        paused_surf = font_large.render("Paused", True, (255, 255, 255))
        screen.blit(paused_surf, ((screen_width - paused_surf.get_width()) // 2, screen_height // 2 - 100))

    elif game_state == "GAME_OVER":

        over_surf = font_large.render('GAME OVER', True, (255, 50, 50))
        restart_surf = font_small.render('Press [R] to restart or [ESC] to Quit', True, (200, 200, 200))
        screen.blit(over_surf, (screen_width // 2 - over_surf.get_width() // 2, screen_height // 2 - 100))
        screen.blit(restart_surf, (screen_width // 2 - restart_surf.get_width() // 2, screen_height // 2))
    

    pygame.display.flip()
    clock.tick(max_frame_rate)

pygame.quit()