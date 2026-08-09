import pygame
import settings
import random
import math


class Enemy:
    def __init__(self, x, y, image=None):
        self.base_size = settings.ENEMY_SIZE
        self.base_speed = settings.ENEMY_SPEED
        self.color = settings.ENEMY_COLOR
        self.rect = pygame.Rect(0, 0, self.base_size, self.base_size)
        self.rect.center = (x, y)
        self.image = image
        self.direction = pygame.Vector2(1, 0)
        self.reset_stats()

    @classmethod
    def spawn_at_distance_from(cls, player_pos, distance, image=None):
        angle = random.random() * 2 * math.pi
        x = player_pos.x + math.cos(angle) * distance
        y = player_pos.y + math.sin(angle) * distance
        x = max(0 + cls._half_size(), min(x, settings.WIDTH - cls._half_size()))
        y = max(0 + cls._half_size(), min(y, settings.HEIGHT - cls._half_size()))
        return cls(x, y, image=image)

    @classmethod
    def _half_size(cls):
        return settings.ENEMY_SIZE / 2

    def pos(self):
        return pygame.Vector2(self.rect.center)

    def reset_stats(self):
        self.boost_count = 0
        self.boost_time_remaining = 0.0
        self.boost_total_time = 0.0
        self.trap_time_remaining = 0.0
        self.trap_animation_offset = pygame.Vector2(0, 0)
        self.speed = self.base_speed
        self.size = self.base_size
        # Health system (cycles when depleted)
        self.max_health = settings.ENEMY_HEALTH_MAX
        self.health = self.max_health
        # Attack and AI state
        self.attack_state = None
        self.attack_timer = 0.0
        self.attack_last_score = {
            'roar': -settings.ATTACK1_COOLDOWN,
            'ripple': -settings.ATTACK2_COOLDOWN,
            'grab': -settings.ATTACK3_COOLDOWN,
            'square': -settings.ATTACK4_COOLDOWN,
        }
        self.attack_data = {}
        self.death_state = None
        self.death_height = 0.0
        self.respawn_pos = pygame.Vector2(self.rect.center)
        self.stun_time_remaining = 0.0
        self.enraged = False
        self.enraged_until_score = 0
        # Main color and right-segment color
        import random as _rnd
        self.main_color = (_rnd.randint(60, 220), _rnd.randint(60, 220), _rnd.randint(60, 220))
        g = _rnd.randint(0, 255)
        self.right_segment_color = (g, g, g)
        center = self.rect.center
        self.rect.size = (int(self.size), int(self.size))
        self.rect.center = center
        self.rect.clamp_ip(pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT))

    def apply_boost(self):
        self.boost_count += 1
        self.boost_time_remaining += settings.BOOST_DURATION_SECONDS
        self.boost_total_time += settings.BOOST_DURATION_SECONDS
        self.speed = self.base_speed * (settings.BOOST_SPEED_MULT ** self.boost_count)
        self.size = self.base_size + settings.BOOST_SIZE_ADD * self.boost_count
        center = self.rect.center
        self.rect.size = (int(self.size), int(self.size))
        self.rect.center = center
        self.rect.clamp_ip(pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT))

    def apply_trap(self, duration):
        self.trap_time_remaining = duration

    def take_damage(self, amount: float):
        """Decrease enemy health by amount. Not used yet externally."""
        try:
            self.health -= float(amount)
        except Exception:
            self.health -= amount
        return self.health

    def tick(self, dt, score=None):
        if self.boost_time_remaining > 0:
            self.boost_time_remaining -= dt
            if self.boost_time_remaining <= 0:
                self.clear_boost()
        if self.trap_time_remaining > 0:
            self.trap_time_remaining -= dt
            if self.trap_time_remaining <= 0:
                self.trap_time_remaining = 0.0
                self.trap_animation_offset = pygame.Vector2(0, 0)
            else:
                self.update_trap_animation()
        if self.stun_time_remaining > 0:
            self.stun_time_remaining -= dt
            if self.stun_time_remaining <= 0:
                self.stun_time_remaining = 0.0
            return
        if self.enraged and score is not None and score >= self.enraged_until_score:
            self.enraged = False
        # Teleport enemy to center if it goes fully off-screen to avoid it getting lost
        if (self.rect.right < 0 or self.rect.left > settings.WIDTH or self.rect.bottom < 0 or self.rect.top > settings.HEIGHT):
            # set to top-left (0, 0) rather than calling it as a function
            self.rect.topleft = (0, 0)
        if self.death_state == 'dying':
            self.death_height -= settings.BOSS_DEATH_SPEED * dt
            if self.death_height <= 0:
                self.death_height = 0.0
                self.death_state = 'reviving'
                self.rect.center = self._random_spawn_pos(self.respawn_pos, settings.SPAWN_DISTANCE)
                self.health = self.max_health
            return
        if self.death_state == 'reviving':
            self.death_height += settings.BOSS_DEATH_SPEED * dt
            if self.death_height >= settings.BOSS_DEATH_HEIGHT:
                self.death_height = settings.BOSS_DEATH_HEIGHT
                self.death_state = None
                if score is not None:
                    self.enraged = True
                    self.enraged_until_score = score + settings.ENEMY_ENRAGE_SCORE_DURATION
            return
        if self.attack_state is not None:
            self.attack_timer += dt

    def clear_boost(self):
        self.boost_count = 0
        self.boost_time_remaining = 0.0
        self.boost_total_time = 0.0
        self.speed = self.base_speed
        self.size = self.base_size
        center = self.rect.center
        self.rect.size = (int(self.size), int(self.size))
        self.rect.center = center
        self.rect.clamp_ip(pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT))

    def update_trap_animation(self):
        if self.trap_time_remaining > 3:
            self.trap_animation_offset = pygame.Vector2(0, 0)
            return

        t = self.trap_time_remaining
        if t > 2:
            phase = 3 - t
            ease = math.sin(math.pi * 0.5 * phase)
            x = -settings.TRAP_WARNING_PHASE_LEFT_DISTANCE * ease
            y = 0
        elif t > 1:
            phase = 2 - t
            ease = math.sin(math.pi * 0.5 * phase)
            x = -settings.TRAP_WARNING_PHASE_LEFT_DISTANCE + (
                settings.TRAP_WARNING_PHASE_LEFT_DISTANCE + settings.TRAP_WARNING_PHASE_RIGHT_DISTANCE
            ) * ease
            y = 0
        else:
            phase = 1 - t
            ease = math.sin(math.pi * 0.5 * phase)
            x = settings.TRAP_WARNING_PHASE_RIGHT_DISTANCE
            y = -settings.TRAP_WARNING_JUMP_HEIGHT * ease

        self.trap_animation_offset = pygame.Vector2(x, y)

    def is_trapped(self):
        return self.trap_time_remaining > 0

    def has_boost(self):
        return self.boost_time_remaining > 0

    def can_use_attack(self, name, score):
        if self.is_trapped() or self.death_state is not None or self.stun_time_remaining > 0:
            return False
        if self.enraged:
            if name == 'roar':
                return score >= settings.ATTACK1_SCORE_THRESHOLD
            if name == 'ripple':
                return score >= settings.ATTACK2_SCORE_THRESHOLD
            if name == 'grab':
                return True
            if name == 'square':
                return score >= settings.ATTACK4_SCORE_THRESHOLD
        if name == 'roar':
            return score >= settings.ATTACK1_SCORE_THRESHOLD and score - self.attack_last_score['roar'] >= settings.ATTACK1_COOLDOWN
        if name == 'ripple':
            return score >= settings.ATTACK2_SCORE_THRESHOLD and score - self.attack_last_score['ripple'] >= settings.ATTACK2_COOLDOWN
        if name == 'grab':
            return score - self.attack_last_score['grab'] >= settings.ATTACK3_COOLDOWN
        if name == 'square':
            return score >= settings.ATTACK4_SCORE_THRESHOLD and score - self.attack_last_score['square'] >= settings.ATTACK4_COOLDOWN
        return False

    def begin_attack(self, name, player, score):
        self.attack_state = name
        self.attack_timer = 0.0
        self.attack_data = {'player_pos': pygame.Vector2(player.pos())}
        self.attack_last_score[name] = score
        if name == 'roar':
            direction = (player.pos() - self.pos())
            if direction.length_squared() == 0:
                direction = pygame.Vector2(1, 0)
            else:
                direction = direction.normalize()
            target = player.pos() - direction * settings.ATTACK1_TARGET_DISTANCE
            target.x = max(0, min(settings.WIDTH, target.x))
            target.y = max(0, min(settings.HEIGHT, target.y))
            self.attack_data.update({
                'target_point': target,
                'shockwave_origin': target,
                'shockwave_dir': (player.pos() - target).normalize(),
                'max_angle': settings.ATTACK1_SPREAD_ANGLE,
                'phase': 'move',
                'particles': [],
                'hit': False,
                'lock_updated': False,
            })
        elif name == 'ripple':
            end_point = pygame.Vector2(player.pos())
            points = [pygame.Vector2(self.pos())]
            for _ in range(3):
                prev = points[-1]
                offset = pygame.Vector2(random.uniform(-140, 140), random.uniform(-100, 100))
                candidate = pygame.Vector2(
                    max(0, min(settings.WIDTH, prev.x + offset.x)),
                    max(0, min(settings.HEIGHT, prev.y + offset.y)),
                )
                points.append(candidate)
            points.append(end_point)
            final_dir = (end_point - points[-2])
            if final_dir.length_squared() == 0:
                final_dir = pygame.Vector2(1, 0)
            else:
                final_dir = final_dir.normalize()
            wall_target = self._point_to_edge(end_point, final_dir)
            points.append(wall_target)
            self.attack_data.update({
                'phase': 'lock',
                'path': points,
                'path_index': 0,
                'backoff_point': self.pos() - (end_point - self.pos()).normalize() * settings.ATTACK2_BACKOFF_DISTANCE,
                'show_path': points[:],
                'run_velocity': pygame.Vector2(0, 0),
                'hit_target': False,
            })
        elif name == 'grab':
            self.attack_data.update({
                'phase': 'grab',
                'hand_left': pygame.Rect(0, 0, 36, 36),
                'hand_right': pygame.Rect(0, 0, 36, 36),
                'hold_start': pygame.Vector2(player.pos()),
                'player_offset': pygame.Vector2(0, 0),
                'throw_target': self._nearest_wall_point(player.pos()),
                'thrown': False,
            })
            player.stun_time_remaining = settings.ATTACK3_KNOCKBACK_STUN + settings.ATTACK3_GRAB_DURATION + settings.ATTACK3_THROW_DURATION
            player.locked_to_attack = True
        elif name == 'square':
            self.rect.center = (settings.WIDTH // 2, settings.HEIGHT // 2)
            self.attack_data.update({
                'phase': 'setup',
                'glow_rect': pygame.Rect(0, 0, settings.ATTACK4_ZONE_SIZE[0], settings.ATTACK4_ZONE_SIZE[1]),
                'glow_rect_center': pygame.Vector2(settings.WIDTH // 2, settings.HEIGHT // 2),
                'drones': [],
                'marks': [],
                'next_spawn': settings.ATTACK4_SPAWN_INTERVAL,
            })
        if name not in self.attack_last_score:
            self.attack_last_score[name] = score

    def _nearest_wall_point(self, position):
        x, y = position.x, position.y
        distances = [x, settings.WIDTH - x, y, settings.HEIGHT - y]
        min_dist = min(distances)
        if min_dist == x:
            return pygame.Vector2(0 + self.rect.width // 2, y)
        if min_dist == settings.WIDTH - x:
            return pygame.Vector2(settings.WIDTH - self.rect.width // 2, y)
        if min_dist == y:
            return pygame.Vector2(x, 0 + self.rect.height // 2)
        return pygame.Vector2(x, settings.HEIGHT - self.rect.height // 2)

    def _random_spawn_pos(self, player_pos, distance):
        angle = random.random() * 2 * math.pi
        x = player_pos.x + math.cos(angle) * distance
        y = player_pos.y + math.sin(angle) * distance
        x = max(0 + self._half_size(), min(x, settings.WIDTH - self._half_size()))
        y = max(0 + self._half_size(), min(y, settings.HEIGHT - self._half_size()))
        return pygame.Vector2(x, y)

    def start_death(self, player_pos):
        self.death_state = 'dying'
        self.death_height = settings.BOSS_DEATH_HEIGHT
        self.respawn_pos = player_pos
        self.attack_state = None
        self.attack_timer = 0.0
        self.attack_data.clear()

    def _point_to_edge(self, position, direction):
        if direction.length_squared() == 0:
            return pygame.Vector2(position)
        direction = direction.normalize()
        if direction.x == 0:
            tx = float('inf')
        elif direction.x > 0:
            tx = (settings.WIDTH - position.x) / direction.x
        else:
            tx = -position.x / direction.x
        if direction.y == 0:
            ty = float('inf')
        elif direction.y > 0:
            ty = (settings.HEIGHT - position.y) / direction.y
        else:
            ty = -position.y / direction.y
        t = min(tx, ty)
        if t < 0:
            t = 0
        edge_point = position + direction * t
        edge_point.x = max(0, min(settings.WIDTH, edge_point.x))
        edge_point.y = max(0, min(settings.HEIGHT, edge_point.y))
        return edge_point

    def update(self, player, dt):
        if self.is_trapped() or self.death_state is not None:
            return
        if self.attack_state is not None:
            self.run_attack(player, dt)
            return
        dirv = pygame.Vector2(player.pos()) - self.pos()
        if dirv.length_squared() == 0:
            return
        dirv = dirv.normalize()
        self.direction = dirv
        movement = dirv * self.speed * dt
        self.rect.centerx += movement.x
        self.rect.centery += movement.y

    def run_attack(self, player, dt):
        if self.attack_state == 'roar':
            self._update_roar(player, dt)
        elif self.attack_state == 'ripple':
            self._update_ripple(player, dt)
        elif self.attack_state == 'grab':
            self._update_grab(player, dt)
        elif self.attack_state == 'square':
            self._update_square(player, dt)

    def _update_roar(self, player, dt):
        data = self.attack_data
        if data['phase'] == 'move':
            direction = data['target_point'] - self.pos()
            if direction.length_squared() > 1:
                direction = direction.normalize()
                self.direction = direction
                step = direction * self.speed * dt
                self.rect.centerx += step.x
                self.rect.centery += step.y
            else:
                data['phase'] = 'charge'
                self.attack_timer = 0.0
        elif data['phase'] == 'charge':
            if not data.get('lock_updated', False) and self.attack_timer >= max(0.0, settings.ATTACK1_CHARGE_TIME - settings.ATTACK1_LOCK_ON_DELAY):
                data['shockwave_dir'] = (player.pos() - data['shockwave_origin']).normalize()
                data['lock_updated'] = True
            if self.attack_timer >= settings.ATTACK1_CHARGE_TIME:
                data['phase'] = 'shock'
                data['particles'] = []
                for i in range(settings.ATTACK1_PARTICLE_COUNT):
                    angle_offset = random.uniform(-data['max_angle'], data['max_angle'])
                    direction = data['shockwave_dir'].rotate(angle_offset)
                    data['particles'].append({
                        'pos': pygame.Vector2(data['shockwave_origin']),
                        'dir': direction,
                        'curved': random.choice([True, False]),
                    })
        elif data['phase'] == 'shock':
            alive = []
            for ppart in data['particles']:
                curve = pygame.Vector2(-ppart['dir'].y, ppart['dir'].x) * 0.12
                if ppart['curved']:
                    ppart['pos'] += (ppart['dir'] + curve) * settings.ATTACK1_SHOCKWAVE_SPEED * dt
                else:
                    ppart['pos'] += ppart['dir'] * settings.ATTACK1_SHOCKWAVE_SPEED * dt
                if 0 <= ppart['pos'].x <= settings.WIDTH and 0 <= ppart['pos'].y <= settings.HEIGHT:
                    alive.append(ppart)
                if not data['hit'] and player.rect.collidepoint(ppart['pos']):
                    player_dist = (player.pos() - self.pos()).length()
                    if player.shield_active and player_dist > settings.SHIELD_CLOSE_RANGE:
                        self.take_damage(settings.SHIELD_REFLECT_DAMAGE)
                        if self.health <= 0 and self.death_state is None:
                            self.start_death(player.pos())
                        self.attack_state = None
                        data.clear()
                        return
                    data['hit'] = True
                    player.hearts = max(0.0, player.hearts - settings.ATTACK_DAMAGE_HALF)
                    player.stun_time_remaining = settings.ATTACK3_KNOCKBACK_STUN
                    player.locked_to_attack = False
                    self._push_player_to_wall(player)
            data['particles'] = alive
            if not alive and self.attack_timer > settings.ATTACK1_CHARGE_TIME:
                self.attack_state = None
                data.clear()
        elif data['phase'] == 'done':
            self.attack_state = None
            data.clear()

    def _update_ripple(self, player, dt):
        data = self.attack_data
        if data['phase'] == 'lock':
            if self.attack_timer >= settings.ATTACK2_LOCK_TIME:
                data['phase'] = 'run'
                data['path_index'] = 1
                self.rect.center = (int(data['backoff_point'].x), int(data['backoff_point'].y))
                next_target = data['path'][1]
                velocity = next_target - self.pos()
                data['run_velocity'] = velocity.normalize() * settings.ATTACK2_RUN_SPEED if velocity.length_squared() > 0 else pygame.Vector2(settings.ATTACK2_RUN_SPEED, 0)
                self.direction = data['run_velocity'].normalize()
        elif data['phase'] == 'run':
            if data['path_index'] >= len(data['path']):
                if not data['hit_target']:
                    self.apply_trap(settings.ATTACK2_MISS_STUN)
                self.attack_state = None
                data.clear()
                return
            target = data['path'][data['path_index']]
            direction = target - self.pos()
            if direction.length_squared() <= (self.rect.width * 0.5) ** 2:
                data['path_index'] += 1
                if data['path_index'] < len(data['path']):
                    next_target = data['path'][data['path_index']]
                    direction = next_target - self.pos()
                    if direction.length_squared() > 0:
                        data['run_velocity'] = direction.normalize() * settings.ATTACK2_RUN_SPEED
                        self.direction = data['run_velocity'].normalize()
            self.rect.centerx += data['run_velocity'].x * dt
            self.rect.centery += data['run_velocity'].y * dt
            if player.rect.colliderect(self.rect) and not data['hit_target']:
                if player.shield_active and (player.pos() - self.pos()).length() > settings.SHIELD_CLOSE_RANGE:
                    self.take_damage(settings.SHIELD_REFLECT_DAMAGE)
                    if self.health <= 0 and self.death_state is None:
                        self.start_death(player.pos())
                    self.attack_state = None
                    data.clear()
                    return
                data['hit_target'] = True
                player.hearts = max(0.0, player.hearts - settings.ATTACK2_DAMAGE)
                player.locked_to_attack = False
                self._push_player_to_wall(player)
                self.attack_state = None
                data.clear()

    def _update_grab(self, player, dt):
        data = self.attack_data
        total = settings.ATTACK3_GRAB_DURATION + settings.ATTACK3_DRAG_DURATION + settings.ATTACK3_THROW_DURATION
        if self.attack_timer < settings.ATTACK3_GRAB_DURATION:
            ratio = self.attack_timer / max(0.001, settings.ATTACK3_GRAB_DURATION)
            target_y = data['hold_start'].y - settings.ATTACK3_HOLD_RAISE * ratio
            player.rect.center = (data['hold_start'].x, target_y)
        elif self.attack_timer < settings.ATTACK3_GRAB_DURATION + settings.ATTACK3_DRAG_DURATION:
            drag_time = self.attack_timer - settings.ATTACK3_GRAB_DURATION
            ratio = drag_time / max(0.001, settings.ATTACK3_DRAG_DURATION)
            behind = self.pos() - self.direction * (self.rect.width * 0.7 + player.rect.width * 0.5)
            player.rect.center = data['hold_start'] + (behind - data['hold_start']) * ratio
        else:
            if not data['thrown']:
                data['thrown'] = True
                player.hearts = max(0.0, player.hearts - 1.0)
                self._push_player_to_wall(player)
            if self.attack_timer >= total:
                self.attack_state = None
                data.clear()
                player.locked_to_attack = False

    def _update_square(self, player, dt):
        data = self.attack_data
        if self.attack_timer >= settings.ATTACK4_DURATION:
            self.attack_state = None
            data.clear()
            return
        data['next_spawn'] -= dt
        if data['next_spawn'] <= 0:
            data['next_spawn'] += settings.ATTACK4_SPAWN_INTERVAL
            data['drones'].append({
                'pos': pygame.Vector2(self.pos()),
                'target': pygame.Vector2(player.pos()),
                'alpha': 255,
                'arrived': False,
                'fade': 0.0,
            })
        for drone in data['drones'][:]:
            drone_rect = pygame.Rect(int(drone['pos'].x) - 10, int(drone['pos'].y) - 10, 20, 20)
            if player.rect.colliderect(drone_rect):
                player_dist = (player.pos() - self.pos()).length()
                if player.shield_active and player_dist > settings.SHIELD_CLOSE_RANGE:
                    self.stun_time_remaining = settings.ATTACK3_KNOCKBACK_STUN
                    self.attack_state = None
                    data.clear()
                    return
                damage = settings.ATTACK4_DAMAGE + (1 if self.enraged else 0)
                player.hearts = max(0.0, player.hearts - damage)
                player.stun_time_remaining = settings.ATTACK3_KNOCKBACK_STUN
                player.locked_to_attack = False
                data['drones'].remove(drone)
                self._push_player_to_wall(player)
                if player.hearts <= 0 and player.death_state is None:
                    player.death_state = 'dying'
                    player.death_height = settings.PLAYER_DEATH_HEIGHT
                    player.alive = True
                continue
            if not drone['arrived']:
                direction = drone['target'] - drone['pos']
                dist = direction.length()
                if dist <= settings.ATTACK4_DRONE_SPEED * dt:
                    drone['pos'] = pygame.Vector2(drone['target'])
                    drone['arrived'] = True
                else:
                    drone['pos'] += direction.normalize() * settings.ATTACK4_DRONE_SPEED * dt
            else:
                drone['fade'] += dt
                drone['alpha'] = max(0, 255 - int((drone['fade'] / settings.ATTACK4_FADE_TIME) * 255))
                if drone['fade'] >= settings.ATTACK4_FADE_TIME:
                    mark_rect = pygame.Rect(0, 0, 28, 28)
                    mark_rect.center = (int(drone['target'].x), int(drone['target'].y))
                    data['marks'].append({'rect': mark_rect, 'active': True})
                    data['drones'].remove(drone)
        for mark in data['marks']:
            if mark['active'] and player.rect.colliderect(mark['rect']):
                player_dist = (player.pos() - self.pos()).length()
                if player.shield_active and player_dist > settings.SHIELD_CLOSE_RANGE:
                    self.stun_time_remaining = settings.ATTACK3_KNOCKBACK_STUN
                    self.attack_state = None
                    data.clear()
                    return
                damage = settings.ATTACK_DAMAGE_HALF + (1 if self.enraged else 0)
                player.hearts = max(0.0, player.hearts - damage)
                player.stun_time_remaining = settings.ATTACK3_KNOCKBACK_STUN
                player.locked_to_attack = False
                self._push_player_to_wall(player)
                mark['active'] = False

    def _push_player_to_wall(self, player):
        px, py = player.rect.center
        left = px
        right = settings.WIDTH - px
        top = py
        bottom = settings.HEIGHT - py
        nearest = min(left, right, top, bottom)
        if nearest == left:
            player.rect.left = 0
        elif nearest == right:
            player.rect.right = settings.WIDTH
        elif nearest == top:
            player.rect.top = 0
        else:
            player.rect.bottom = settings.HEIGHT

    def draw_attack_effects(self, surface, player):
        if self.attack_state is None or self.death_state is not None:
            return
        data = self.attack_data
        if self.attack_state == 'roar' and data.get('phase') == 'charge':
            pygame.draw.circle(surface, (220, 220, 90), (int(self.rect.centerx), int(self.rect.centery)), 22, width=3)
        if self.attack_state == 'roar' and data.get('phase') == 'shock':
            for part in data.get('particles', []):
                rect = pygame.Rect(int(part['pos'].x) - settings.ATTACK1_PARTICLE_SIZE // 2, int(part['pos'].y) - settings.ATTACK1_PARTICLE_SIZE // 2, settings.ATTACK1_PARTICLE_SIZE, settings.ATTACK1_PARTICLE_SIZE)
                pygame.draw.rect(surface, (180, 180, 180), rect)
                pygame.draw.rect(surface, (100, 100, 100), rect, width=1)
        if self.attack_state == 'ripple':
            for index in range(len(data.get('show_path', [])) - 1):
                start = data['show_path'][index]
                end = data['show_path'][index + 1]
                direction = end - start
                length = max(1, direction.length())
                angle = math.degrees(math.atan2(direction.y, direction.x))
                rect = pygame.Rect(0, 0, int(length), settings.ATTACK2_SEGMENT_WIDTH)
                rect.center = (int((start.x + end.x) / 2), int((start.y + end.y) / 2))
                surface_rotated = pygame.Surface(rect.size, pygame.SRCALPHA)
                pygame.draw.rect(surface_rotated, (180, 180, 180, 180), pygame.Rect(0, 0, rect.width, rect.height), border_radius=6)
                surface_rotated = pygame.transform.rotate(surface_rotated, -angle)
                surface.blit(surface_rotated, surface_rotated.get_rect(center=rect.center))
            if data.get('phase') == 'lock':
                for point in data.get('show_path', []):
                    pygame.draw.circle(surface, (255, 180, 80), (int(point.x), int(point.y)), 8)
        if self.attack_state == 'grab':
            hand_left = data['hand_left']
            hand_right = data['hand_right']
            hand_left.center = (player.rect.centerx - 18, player.rect.top - 18)
            hand_right.center = (player.rect.centerx + 22, player.rect.centery)
            pygame.draw.rect(surface, (240, 240, 240), hand_left)
            pygame.draw.rect(surface, (240, 240, 240), hand_right)
            pygame.draw.rect(surface, (60, 60, 60), hand_left, width=3)
            pygame.draw.rect(surface, (60, 60, 60), hand_right, width=3)
        if self.attack_state == 'square':
            glow = data.get('glow_rect')
            if glow is not None:
                s = pygame.Surface(glow.size, pygame.SRCALPHA)
                pygame.draw.rect(s, (120, 220, 255, 90), s.get_rect(), border_radius=14)
                surface.blit(s, glow.topleft)
            for drone in data.get('drones', []):
                alpha = drone.get('alpha', 255)
                rect = pygame.Rect(int(drone['pos'].x) - 10, int(drone['pos'].y) - 10, 20, 20)
                dsurf = pygame.Surface(rect.size, pygame.SRCALPHA)
                dsurf.fill((200, 200, 255, alpha))
                surface.blit(dsurf, rect.topleft)
            for mark in data.get('marks', []):
                if mark['active']:
                    pygame.draw.rect(surface, (10, 10, 10), mark['rect'])

    def draw(self, surface):
        y_offset = 0.0
        if self.death_state in ('dying', 'reviving'):
            height_scale = max(0.0, min(1.0, self.death_height / settings.BOSS_DEATH_HEIGHT))
        else:
            height_scale = 1.0
        draw_center = (
            self.rect.centerx + self.trap_animation_offset.x,
            self.rect.centery + self.trap_animation_offset.y + y_offset,
        )
        if self.image is not None:
            angle = self.direction.angle_to(pygame.Vector2(1, 0))
            scale = (self.size * settings.SPRITE_OVERSIZE) / self.image.get_width()
            image = pygame.transform.rotozoom(self.image, -angle, scale)
            if height_scale < 1.0:
                new_height = max(1, int(image.get_height() * height_scale))
                image = pygame.transform.smoothscale(image, (image.get_width(), new_height))
            rect = image.get_rect(center=draw_center)
            surface.blit(image, rect)
        else:
            rect = self.rect.copy()
            rect.height = max(1, int(rect.height * height_scale))
            rect.center = draw_center
            pygame.draw.rect(surface, self.color, rect)
