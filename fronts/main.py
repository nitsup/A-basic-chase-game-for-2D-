import pygame
import random
import math
from pathlib import Path
import settings
import player
import enemy
import utility


class Pickup:
    def __init__(self, kind, position, image=None, glow=None):
        self.kind = kind
        self.rect = pygame.Rect(0, 0, settings.PICKUP_SIZE, settings.PICKUP_SIZE)
        self.rect.center = position
        self.image = image
        self.glow = glow
        self.color = settings.PICKUP_GREEN_COLOR if kind == "green" else settings.PICKUP_YELLOW_COLOR

    def draw(self, surface):
        if self.glow is not None:
            glow = pygame.transform.smoothscale(self.glow, (int(self.rect.width * 1.8), int(self.rect.height * 1.8)))
            glow_rect = glow.get_rect(center=self.rect.center)
            surface.blit(glow, glow_rect)

        if self.image is not None:
            draw_size = int(self.rect.width * settings.PICKUP_IMAGE_SCALE)
            image = pygame.transform.smoothscale(self.image, (draw_size, draw_size))
            surface.blit(image, image.get_rect(center=self.rect.center))


def random_pickup_position():
    half = settings.PICKUP_SIZE // 2
    x = random.randint(half, settings.WIDTH - half)
    y = random.randint(half, settings.HEIGHT - half)
    return x, y


def load_highscores(path):
    if not path.exists():
        return []
    scores = []
    try:
        with path.open('r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line.isdigit():
                    scores.append(int(line))
    except Exception:
        return []
    scores.sort(reverse=True)
    return scores[:settings.HIGHSCORES_COUNT]


def save_highscores(path, scores):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8') as file:
            for score in scores[:settings.HIGHSCORES_COUNT]:
                file.write(f"{score}\n")
                print(f"Saved score: {score}")
    except Exception:
        pass


def add_score(high_scores, score):
    if score <= 0:
        return high_scores
    new_scores = high_scores[:] + [score]
    new_scores.sort(reverse=True)
    return new_scores[:settings.HIGHSCORES_COUNT]


def create_menu_background(background_img, player_img, enemy_img):
    base = pygame.Surface((settings.WIDTH, settings.HEIGHT))
    if background_img is not None:
        base.blit(background_img, (0, 0))
    else:
        base.fill(settings.BG_COLOR)

    overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
    if player_img is not None:
        player_copy = pygame.transform.rotozoom(player_img, -20, 1.3)
        player_copy.set_alpha(90)
        overlay.blit(player_copy, (-60, settings.HEIGHT - player_copy.get_height() - 20))
    if enemy_img is not None:
        enemy_copy = pygame.transform.rotozoom(enemy_img, 30, 1.4)
        enemy_copy.set_alpha(90)
        overlay.blit(enemy_copy, (settings.WIDTH - enemy_copy.get_width() + 40, 40))
    base.blit(overlay, (0, 0))
    blurred = utility.blur_surface(base, scale=0.14, passes=2)
    dark = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
    dark.fill((0, 0, 0, 120))
    blurred.blit(dark, (0, 0))
    return blurred


def draw_menu_screen(screen, menu_bg, start_rect, highscores_rect, quit_rect):
    screen.blit(menu_bg, (0, 0))
    utility.draw_text(screen, "Base Halo", settings.MENU_TITLE_FONT_SIZE, (settings.WIDTH // 2, settings.HEIGHT // 5), settings.MENU_TITLE_COLOR, settings.FONT_NAME, center=True, bold=True, shadow=True)
    utility.draw_text(screen, "Collect boosts, avoid traps, survive the chase!", settings.MENU_SUBTITLE_FONT_SIZE, (settings.WIDTH // 2, settings.HEIGHT // 5 + 48), settings.MENU_SUBTITLE_COLOR, settings.FONT_NAME, center=True, shadow=True)
    utility.draw_button(screen, start_rect, "Start Game", settings.FONT_NAME, settings.MENU_BUTTON_TEXT_COLOR, settings.MENU_BUTTON_COLOR, settings.MENU_BUTTON_BORDER)
    utility.draw_button(screen, highscores_rect, "Highscores", settings.FONT_NAME, settings.MENU_BUTTON_TEXT_COLOR, settings.MENU_BUTTON_COLOR, settings.MENU_BUTTON_BORDER)
    utility.draw_button(screen, quit_rect, "Quit", settings.FONT_NAME, settings.MENU_BUTTON_TEXT_COLOR, settings.MENU_BUTTON_COLOR, settings.MENU_BUTTON_BORDER)

def draw_pause_screen(screen, resume_rect, highscores_rect, quit_rect):
    overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
    overlay.fill(settings.MENU_OVERLAY_COLOR)
    screen.blit(overlay, (0, 0))
    utility.draw_text(screen, "Paused", settings.MENU_TITLE_FONT_SIZE, (settings.WIDTH // 2, settings.HEIGHT // 5), settings.MENU_TITLE_COLOR, settings.FONT_NAME, center=True, bold=True, shadow=True)
    utility.draw_text(screen, "Press ESC to resume", settings.MENU_SUBTITLE_FONT_SIZE, (settings.WIDTH // 2, settings.HEIGHT // 5 + 48), settings.MENU_SUBTITLE_COLOR, settings.FONT_NAME, center=True, shadow=True)
    utility.draw_button(screen, resume_rect, "Resume", settings.FONT_NAME, settings.MENU_BUTTON_TEXT_COLOR, settings.MENU_BUTTON_COLOR, settings.MENU_BUTTON_BORDER)
    utility.draw_button(screen, highscores_rect, "Highscores", settings.FONT_NAME, settings.MENU_BUTTON_TEXT_COLOR, settings.MENU_BUTTON_COLOR, settings.MENU_BUTTON_BORDER)
    utility.draw_button(screen, quit_rect, "Quit", settings.FONT_NAME, settings.MENU_BUTTON_TEXT_COLOR, settings.MENU_BUTTON_COLOR, settings.MENU_BUTTON_BORDER)


def draw_highscore_screen(screen, high_scores, back_rect):
    screen.fill((12, 18, 28))
    utility.draw_text(screen, "Highscores", settings.MENU_TITLE_FONT_SIZE, (settings.WIDTH // 2, 82), settings.MENU_TITLE_COLOR, settings.FONT_NAME, center=True, bold=True, shadow=True)
    if high_scores:
        for index, value in enumerate(high_scores, start=1):
            utility.draw_text(screen, f"{index}. {value}", 28, (settings.WIDTH // 2, 150 + index * 42), settings.TEXT_COLOR, settings.FONT_NAME, center=True, shadow=True)
    else:
        utility.draw_text(screen, "No highscores yet. Play your first game!", 24, (settings.WIDTH // 2, 170), settings.TEXT_COLOR, settings.FONT_NAME, center=True, shadow=True)
    utility.draw_button(screen, back_rect, "Back", settings.FONT_NAME, settings.MENU_BUTTON_TEXT_COLOR, settings.MENU_BUTTON_COLOR, settings.MENU_BUTTON_BORDER)


def main():
    pygame.init()
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Simple Chase")
    clock = pygame.time.Clock()

    background_img = utility.load_image(settings.BACKGROUND_IMAGE)
    if background_img is not None and background_img.get_size() != (settings.WIDTH, settings.HEIGHT):
        background_img = pygame.transform.smoothscale(background_img, (settings.WIDTH, settings.HEIGHT))
    player_img = utility.load_image(settings.PLAYER_IMAGE)
    player_shadow = utility.load_image(settings.PLAYER_SHADOW_IMAGE)
    stone_background = None
    if background_img is None:
        stone_background = pygame.Surface((settings.WIDTH, settings.HEIGHT))
        stone_background.fill(settings.BG_COLOR)
        for _ in range(60):
            rx = random.randint(0, settings.WIDTH)
            ry = random.randint(0, settings.HEIGHT)
            rw = random.randint(4, 12)
            rh = random.randint(4, 10)
            rect = pygame.Rect(rx, ry, rw, rh)
            pygame.draw.rect(stone_background, (200, 200, 200), rect)
            pygame.draw.rect(stone_background, (140, 140, 140), rect, width=1)
            print("the Random backgroud is drawn with 60 random rectangles of varying sizes and colors to create a textured effect.")
        for _ in range(120):
            dot_x = random.randint(0, settings.WIDTH - 1)
            dot_y = random.randint(0, settings.HEIGHT - 1)
            stone_background.set_at((dot_x, dot_y), (60, 60, 60))
            print("random dots are drawn on the stone background to add more texture and variation to the background.")
    enemy_img = utility.load_image(settings.ENEMY_IMAGE)
    boost_img = utility.load_image(settings.BOOST_IMAGE)
    trap_img = utility.load_image(settings.TRAP_IMAGE)
    glow_img = utility.load_image(settings.PICKUP_GLOW_IMAGE)

    p = player.Player(settings.WIDTH // 2, settings.HEIGHT // 2, image=player_img, shadow_image=player_shadow)
    e = enemy.Enemy.spawn_at_distance_from(p.pos(), settings.SPAWN_DISTANCE, image=enemy_img)
    p.reset_stats()
    e.reset_stats()

    score = 0
    score_timer = 0.0
    score_acc = 0.0
    score_color = settings.TEXT_COLOR
    next_color_change_score = random.randint(60, 250)
    popups = []
    last_nearmiss_time = 0
    last_hit_time = 0
    pickups = []
    next_pickup_score = settings.PICKUP_SPAWN_SCORE_FIRST

    menu_state = "start"
    menu_return_state = "start"
    high_scores = load_highscores(Path(settings.HIGHSCORE_FILE))
    menu_bg = create_menu_background(background_img, player_img, enemy_img)
    center_x = settings.WIDTH // 2
    button_w = settings.MENU_BUTTON_WIDTH
    button_h = settings.MENU_BUTTON_HEIGHT
    total_height = button_h * 3 + settings.MENU_BUTTON_SPACING * 2
    start_y = settings.HEIGHT // 2 - total_height // 2 + 24
    start_rect = pygame.Rect(center_x - button_w // 2, start_y, button_w, button_h)
    highscores_rect = pygame.Rect(center_x - button_w // 2, start_y + button_h + settings.MENU_BUTTON_SPACING, button_w, button_h)
    quit_rect = pygame.Rect(center_x - button_w // 2, start_y + (button_h + settings.MENU_BUTTON_SPACING) * 2, button_w, button_h)
    back_rect = pygame.Rect(center_x - button_w // 2, settings.HEIGHT - 90, button_w, button_h)
    resume_rect = start_rect.copy()

    running = True
    game_over = False
    collision_time = None
    last_click_pos = None
    last_click_button = 0
    score_recorded = False
    death_slide_start = None

    while running:
        dt = clock.tick(settings.FPS) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.MOUSEBUTTONDOWN:
                last_click_pos = ev.pos
                last_click_button = ev.button
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE and menu_state == "play" and not game_over:
                    menu_state = "pause"
                    last_click_pos = None
                    last_click_button = 0
                    
                elif ev.key == pygame.K_ESCAPE and menu_state == "pause":
                    menu_state = "play"
                    last_click_pos = None
                    last_click_button = 0
                    
                elif ev.key == pygame.K_e and score >= settings.SHIELD_UNLOCK_SCORE:
                    p.activate_shield()

        if menu_state != "play":
            if last_click_button == 1 and last_click_pos is not None:
                if menu_state == "start":
                    if start_rect.collidepoint(last_click_pos):
                        p = player.Player(settings.WIDTH // 2, settings.HEIGHT // 2, image=player_img, shadow_image=player_shadow)
                        e = enemy.Enemy.spawn_at_distance_from(p.pos(), settings.SPAWN_DISTANCE, image=enemy_img)
                        p.reset_stats()
                        e.reset_stats()
                        score = 0
                        score_timer = 0.0
                        pickups = []
                        next_pickup_score = settings.PICKUP_SPAWN_SCORE_FIRST
                        game_over = False
                        collision_time = None
                        score_recorded = False
                        menu_state = "play"
                        last_click_pos = None
                        last_click_button = 0
                    elif highscores_rect.collidepoint(last_click_pos):
                        menu_state = "highscores"
                        last_click_pos = None
                        last_click_button = 0
                    elif quit_rect.collidepoint(last_click_pos):
                        running = False
                elif menu_state == "pause":
                    if resume_rect.collidepoint(last_click_pos):
                        menu_state = "play"
                        last_click_pos = None
                        last_click_button = 0
                    elif highscores_rect.collidepoint(last_click_pos):
                        menu_state = "highscores"
                        menu_return_state = "pause"
                        last_click_pos = None
                        last_click_button = 0
                    elif quit_rect.collidepoint(last_click_pos):
                        running = False
                elif menu_state == "highscores":
                    if back_rect.collidepoint(last_click_pos):
                        menu_state = menu_return_state
                        if menu_state == "highscores":
                            menu_state = "pause"
                        menu_return_state = "start"
                        last_click_pos = None
                        last_click_button = 0
                
        if menu_state != "play":
            if menu_state == "start":
                draw_menu_screen(screen, menu_bg, start_rect, highscores_rect, quit_rect)
            elif menu_state == "pause":
                draw_pause_screen(screen, resume_rect, highscores_rect, quit_rect)
            elif menu_state == "highscores":
                draw_highscore_screen(screen, high_scores, back_rect)
            pygame.display.update()
            if last_click_button == 1:
                last_click_pos = None
                last_click_button = 0
            continue
        if last_click_button == 1:
            settings.Py_running += 1

        keys = pygame.key.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        p.mouse_angle = math.degrees(math.atan2(mouse_y - p.rect.centery, mouse_x - p.rect.centerx))

        if p.death_state == 'dying':
            p.tick(dt)
            if death_slide_start is None:
                death_slide_start = pygame.time.get_ticks()
        elif e.death_state in ('dying', 'reviving'):
            e.tick(dt, score)
        elif not game_over:
            if keys[pygame.K_e] and score >= settings.SHIELD_UNLOCK_SCORE:
                p.activate_shield()

            player_can_move = not p.is_trapped() and p.stun_time_remaining <= 0 and p.death_state is None
            enemy_can_move = not (p.is_trapped() or e.is_trapped() or e.death_state is not None)
            if player_can_move:
                p.update(keys, dt)
            if enemy_can_move:
                # choose attacks before normal movement
                dist = (p.pos() - e.pos()).length()
                grabbed = utility.check_collision_rect(p.rect, e.rect)
                if e.attack_state is None:
                    if e.can_use_attack('square', score):
                        e.begin_attack('square', p, score)
                    elif dist >= settings.ATTACK2_TRIGGER_DISTANCE and e.can_use_attack('ripple', score):
                        e.begin_attack('ripple', p, score)
                    elif score >= settings.ATTACK1_SCORE_THRESHOLD and e.can_use_attack('roar', score):
                        e.begin_attack('roar', p, score)
                    elif grabbed and e.can_use_attack('grab', score):
                        e.begin_attack('grab', p, score)
                e.update(p, dt)

            if utility.check_collision_rect(p.rect, e.rect):
                if e.attack_state is None:
                    if e.can_use_attack('grab', score):
                        e.begin_attack('grab', p, score)
                    else:
                        now = pygame.time.get_ticks()
                        if now - last_hit_time > 800:
                            last_hit_time = now
                            print(f"Player hit! Hearts: {p.hearts}")
                            p.hearts = max(0.0, p.hearts - settings.ATTACK_DAMAGE_HALF)
                            p.stun_time_remaining = settings.ATTACK3_KNOCKBACK_STUN
                            p.locked_to_attack = False
                            e._push_player_to_wall(p)
                            if p.hearts <= 0 and p.death_state is None:
                                p.death_state = 'dying'
                                p.death_height = settings.PLAYER_DEATH_HEIGHT
                                p.alive = True
                if p.death_state is None:
                    p.tick(dt)
                e.tick(dt, score)
            else:
                # scoring: points per second depend on distance (closer => more points: 5..2)
                dist = (p.pos() - e.pos()).length()
                max_d = float(settings.WIDTH)
                tnorm = max(0.0, min(1.0, dist / max_d))
                points_per_sec = 5.0 - 3.0 * tnorm
                score_acc += points_per_sec * dt
                if score_acc >= 1.0:
                    add_n = int(score_acc)
                    score += add_n
                    score_acc -= add_n
                    # check color change thresholds
                    if score >= next_color_change_score:
                        score_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                        next_color_change_score = score + random.randint(60, 250)
                p.tick(dt)
                e.tick(dt, score)
                if score >= next_pickup_score:
                    kind = 'green' if random.random() < settings.GREEN_PICKUP_CHANCE else 'yellow'
                    image = boost_img if kind == 'yellow' else trap_img
                    pickups.append(Pickup(kind, random_pickup_position(), image=image, glow=glow_img))
                    interval = settings.PICKUP_SPAWN_INTERVAL_POST150 if score >= 150 else settings.PICKUP_SPAWN_INTERVAL_PRE150
                    next_pickup_score = score + random.randint(interval[0], interval[1])
        else:
            p.tick(dt)
            e.tick(dt)

        if p.death_state == 'dead' and not game_over:
            game_over = True
            if collision_time is None:
                collision_time = pygame.time.get_ticks()
            # keep enemy frozen during player death
            e.attack_state = None
            e.attack_data.clear()
            e.death_state = None
            # stop enemy actions once death is registered
            e.attack_state = None
            e.attack_data.clear()
            e.death_state = None
            print("Game over! Player has died. Waiting for respawn or menu interaction.")

        if not game_over:
            for current in pickups[:]:
                if utility.check_collision_rect(p.rect, current.rect):
                    if current.kind == 'yellow':
                        p.apply_boost()
                    else:
                        p.apply_trap(settings.TRAP_DURATION_PLAYER)
                        e.apply_trap(settings.TRAP_DURATION_PLAYER)
                    pickups.remove(current)
                    continue
                if utility.check_collision_rect(e.rect, current.rect):
                    if current.kind == 'yellow':
                        e.apply_boost()
                    else:
                        e.apply_trap(settings.TRAP_DURATION_ENEMY)
                    pickups.remove(current)
                    continue

        # Near-miss detection (40..60px beyond touching distance)
        if not game_over:
            min_touch = (p.rect.width + e.rect.width) / 2
            dist = (p.pos() - e.pos()).length()
            now_ms = pygame.time.get_ticks()
            if (min_touch + 40) <= dist <= (min_touch + 60) and now_ms - last_nearmiss_time > 2000:
                # spawn +10 popup (start from right -> glide to score)
                popup = {
                    'text': '+10',
                    'value': 10,
                    'start_time': now_ms / 1000.0,
                    'duration': 0.9,
                    'start_pos': (settings.SCORE_POS[0] + 220, settings.SCORE_POS[1]),
                    'end_pos': (settings.SCORE_POS[0] + 40, settings.SCORE_POS[1]),
                    'color': (180, 255, 120),
                    'added': False,
                }
                popups.append(popup)
                last_nearmiss_time = now_ms

        # Draw background / world
        if background_img is not None:
            screen.blit(background_img, (0, 0))
        else:
            screen.blit(stone_background, (0, 0))
        for current in pickups:
            current.draw(screen)
        e.draw(screen)
        p.draw(screen)
        e.draw_attack_effects(screen, p)

        # Enemy health bar (top middle)
        center_x = settings.WIDTH // 2
        eh_w = settings.ENEMY_HEALTH_BAR_WIDTH
        eh_h = settings.ENEMY_HEALTH_BAR_HEIGHT
        eh_x = center_x - eh_w // 2
        eh_y = settings.ENEMY_HEALTH_BAR_OFFSET_Y

        # If enemy reached zero health, cycle colors/health and create popup to add points
        if e.health <= 0 and e.death_state is None:
            e.start_death(p.pos())
            print("Enemy defeated! Spawning score popup.")
            popup = {
                'text': '+100',
                'value': 100,
                'start_time': pygame.time.get_ticks() / 1000.0,
                'duration': 0.9,
                'start_pos': (settings.SCORE_POS[0] + 260, settings.SCORE_POS[1]),
                'end_pos': (settings.SCORE_POS[0] + 40, settings.SCORE_POS[1]),
                'color': e.right_segment_color,
                'added': False,
            }
            popups.append(popup)

        # Draw health bar background
        health_bg_rect = pygame.Rect(eh_x, eh_y, eh_w, eh_h)
        pygame.draw.rect(screen, (24, 28, 36), health_bg_rect, border_radius=6)

        # Filled portion based on current health
        fill_frac = max(0.0, min(1.0, e.health / e.max_health))
        fill_w = int(fill_frac * eh_w)
        if fill_w > 0:
            fill_rect = pygame.Rect(eh_x, eh_y, fill_w, eh_h)
            pygame.draw.rect(screen, e.main_color, fill_rect, border_radius=6)

        # Right special segment (always shown on right side)
        right_w = settings.ENEMY_HEALTH_BAR_RIGHT_WIDTH
        right_rect = pygame.Rect(eh_x + eh_w - right_w, eh_y, right_w, eh_h)
        pygame.draw.rect(screen, e.right_segment_color, right_rect, border_radius=6)

        if e.enraged:
            face_rect = pygame.Rect(right_rect.left + 6, right_rect.top + 4, right_rect.width - 12, right_rect.height - 8)
            pygame.draw.rect(screen, (180, 30, 30), face_rect, border_radius=6)
            eye_size = 4
            pygame.draw.rect(screen, (0, 0, 0), (face_rect.left + 4, face_rect.top + 6, eye_size, eye_size))
            pygame.draw.rect(screen, (0, 0, 0), (face_rect.right - 4 - eye_size, face_rect.top + 6, eye_size, eye_size))
            pygame.draw.rect(screen, (0, 0, 0), (face_rect.left + 5, face_rect.bottom - 7, face_rect.width - 10, 3))

        # If enemy has a boost, draw a red boost bar below the health bar
        if e.has_boost():
            red_bar_w = settings.BOOST_BAR_WIDTH
            red_bar_h = settings.BOOST_BAR_HEIGHT
            red_bar_x = center_x - red_bar_w // 2
            red_bar_y = eh_y + eh_h + 8
            red_rect = pygame.Rect(red_bar_x, red_bar_y, red_bar_w, red_bar_h)
            red_fill = e.boost_time_remaining / e.boost_total_time if e.boost_total_time > 0 else 0.0
            utility.draw_bar(screen, red_rect, red_fill, bg_color=(40, 20, 20), fill_color=(200, 40, 40))

        if p.is_trapped():
            utility.draw_rhombus(
                screen,
                (p.rect.centerx, p.rect.top - 10),
                settings.RHOMBUS_SIZE,
                (0, 0, 0),
                border_color=(255, 255, 255),
                border_width=4,
            )
        if e.is_trapped():
            utility.draw_rhombus(
                screen,
                (e.rect.centerx, e.rect.top - 10),
                settings.RHOMBUS_SIZE,
                (0, 0, 0),
                border_color=(255, 255, 255),
                border_width=4,
            )

        utility.draw_text(screen, f"Score: {int(score)}", settings.SCORE_FONT_SIZE, settings.SCORE_POS, score_color, settings.FONT_NAME, center=False, bold=True)
        if score >= settings.SHIELD_UNLOCK_SCORE:
            utility.draw_text(screen, "Press E to activate shield", 18, (settings.SCORE_POS[0] + 250, settings.SCORE_POS[1] + 2), settings.TEXT_COLOR, settings.FONT_NAME, center=False, bold=False)
            if p.shield_active:
                utility.draw_text(screen, "SHIELD ACTIVE", 18, (settings.SCORE_POS[0] + 470, settings.SCORE_POS[1] + 2), (160, 255, 160), settings.FONT_NAME, center=False, bold=True)
            cooldown_rect = pygame.Rect(settings.WIDTH - 200, settings.HEIGHT - 40, 180, 18)
            utility.draw_bar(screen, cooldown_rect, 1.0 - min(1.0, p.shield_cooldown / settings.SHIELD_COOLDOWN), bg_color=(50, 50, 60), fill_color=(100, 180, 255))
            if p.shield_cooldown == 0.0:
                pygame.draw.rect(screen, (255, 255, 255), cooldown_rect, width=2, border_radius=10)
            else:
                pygame.draw.rect(screen, (80, 80, 90), cooldown_rect, width=2, border_radius=10)

        # Player hearts (pixel-art) drawn top-left above boost bar
        heart_x = settings.SCORE_POS[0] + 8
        heart_y = settings.SCORE_POS[1] + settings.SCORE_FONT_SIZE + 8
        heart_pixel_size = 4
        utility.draw_hearts(screen, heart_x, heart_y, int(p.hearts), max_hearts=5, pixel_size=heart_pixel_size, spacing=6, filled_color=(220, 60, 60), empty_color=(8, 8, 8))

        # Player boost bar (shifted down to avoid overlapping with hearts)
        if p.has_boost():
            p_fill = p.boost_time_remaining / p.boost_total_time if p.boost_total_time > 0 else 0.0
            # heart height approximated from pattern: 4 rows * pixel_size
            p_bar_y = settings.SCORE_POS[1] + settings.SCORE_FONT_SIZE + 8 + (heart_pixel_size * 4) + 6
            p_bar_rect = pygame.Rect(settings.SCORE_POS[0], p_bar_y, settings.BOOST_BAR_WIDTH, settings.BOOST_BAR_HEIGHT)
            utility.draw_bar(screen, p_bar_rect, p_fill, settings.BOOST_BAR_BG, settings.BOOST_BAR_FILL)
            if p.boost_time_remaining <= 5.0:
                pulse_phase = (pygame.time.get_ticks() / 700) % 2
                if pulse_phase < 1:
                    pygame.draw.rect(screen, (255, 80, 80), p_bar_rect, width=3, border_radius=10)
            p_label_pos = (p_bar_rect.centerx, p_bar_rect.bottom + settings.BOOST_LABEL_OFFSET_Y)
            utility.draw_text(screen, settings.BOOST_LABEL_TEXT, settings.BOOST_LABEL_FONT_SIZE, p_label_pos, settings.TEXT_COLOR, settings.FONT_NAME, center=True, bold=True)

        # Draw and update popups (floating score additions)
        now_s = pygame.time.get_ticks() / 1000.0
        for popup in popups[:]:
            elapsed = now_s - popup['start_time']
            dur = popup.get('duration', 0.9)
            start = popup['start_pos']
            end = popup['end_pos']
            if elapsed >= dur:
                if not popup.get('added', False):
                    score += popup.get('value', 0)
                    popup['added'] = True
                popups.remove(popup)
                continue
            # split-phase movement: slow 0.6s then fast 0.3s
            phase1 = min(0.6, dur)
            if elapsed <= phase1:
                t = elapsed / phase1
                mid = (start[0] + 0.4 * (end[0] - start[0]), start[1] + 0.4 * (end[1] - start[1]))
                pos = (start[0] + (mid[0] - start[0]) * t, start[1] + (mid[1] - start[1]) * t)
            else:
                t2 = (elapsed - phase1) / max(0.001, (dur - phase1))
                mid = (start[0] + 0.4 * (end[0] - start[0]), start[1] + 0.4 * (end[1] - start[1]))
                pos = (mid[0] + (end[0] - mid[0]) * t2, mid[1] + (end[1] - mid[1]) * t2)
            alpha = int(max(0, 255 * (1.0 - elapsed / dur)))
            color = popup.get('color', (255, 255, 255))
            # draw with alpha by rendering to a surface
            font = pygame.font.SysFont(settings.FONT_NAME, 22, bold=True)
            surf = font.render(popup['text'], True, color)
            if alpha < 255:
                surf.set_alpha(alpha)
            rect = surf.get_rect(center=pos)
            screen.blit(surf, rect)

        if p.death_state == 'dying' or game_over:
            if death_slide_start is not None:
                elapsed = (pygame.time.get_ticks() - death_slide_start) / 1000.0
                blurred = utility.blur_surface(screen, scale=0.16, passes=1)
                screen.blit(blurred, (0, 0))
                dark_overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
                dark_overlay.fill((0, 0, 0, 120))
                screen.blit(dark_overlay, (0, 0))
                slide_width = min(settings.WIDTH, int(elapsed * 380))
                slide_rect = pygame.Rect(-settings.WIDTH + slide_width, 0, settings.WIDTH, settings.HEIGHT)
                pygame.draw.rect(screen, (0, 0, 0), slide_rect)
        if game_over:
            if pygame.time.get_ticks() - collision_time >= 500:
                center_pos = (settings.WIDTH // 2, settings.HEIGHT // 2)
                utility.draw_text(screen, "You died", 48, center_pos, settings.TEXT_COLOR, settings.FONT_NAME)

                btn_w, btn_h = 160, 40
                btn_center = (center_pos[0], center_pos[1] + 60)
                btn_rect = pygame.Rect(0, 0, btn_w, btn_h)
                btn_rect.center = btn_center
                pygame.draw.rect(screen, (200, 200, 200), btn_rect)
                utility.draw_text(screen, "Respawn", 28, btn_rect.center, (0, 0, 0), settings.FONT_NAME, center=True, bold=True)
                btn2_rect = pygame.Rect(0, 0, btn_w, btn_h)
                btn2_rect.center = (center_pos[0], center_pos[1] + 120)
                pygame.draw.rect(screen, (180, 180, 180), btn2_rect)
                utility.draw_text(screen, "Menu", 28, btn2_rect.center, (0, 0, 0), settings.FONT_NAME, center=True, bold=True)

                if last_click_button == 1 and last_click_pos is not None:
                    if btn_rect.collidepoint(last_click_pos):
                        if not score_recorded:
                            high_scores = add_score(high_scores, score)
                            save_highscores(Path(settings.HIGHSCORE_FILE), high_scores)
                            score_recorded = True
                        p = player.Player(settings.WIDTH // 2, settings.HEIGHT // 2, image=player_img, shadow_image=player_shadow)
                        e = enemy.Enemy.spawn_at_distance_from(p.pos(), settings.SPAWN_DISTANCE, image=enemy_img)
                        p.reset_stats()
                        e.reset_stats()
                        score = 20
                        score_timer = 0.0
                        pickups = []
                        next_pickup_score = settings.PICKUP_SPAWN_SCORE_FIRST
                        game_over = False
                        collision_time = None
                        death_slide_start = None
                        last_click_pos = None
                        last_click_button = 0
                    elif btn2_rect.collidepoint(last_click_pos):
                        menu_state = "start"
                        game_over = False
                        death_slide_start = None
                        last_click_pos = None
                        last_click_button = 0

                if last_click_button == 1:
                    last_click_pos = None
                    last_click_button = 0

        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
