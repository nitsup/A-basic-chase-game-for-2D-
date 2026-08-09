import pygame
import math
import settings


class Player:
    def __init__(self, x, y, image=None, shadow_image=None):
        self.base_size = settings.PLAYER_SIZE
        self.base_speed = settings.PLAYER_SPEED
        self.color = settings.PLAYER_COLOR
        self.rect = pygame.Rect(0, 0, self.base_size, self.base_size)
        self.rect.center = (x, y)
        self.image = image
        self.shadow_image = shadow_image
        self.direction = pygame.Vector2(1, 0)
        self.alive = True
        self.trap_animation_offset = pygame.Vector2(0, 0)
        self.mouse_angle = 0.0
        self.reset_stats()

    def pos(self):
        return pygame.Vector2(self.rect.center)

    def reset_stats(self):
        self.alive = True
        self.boost_count = 0
        self.boost_time_remaining = 0.0
        self.boost_total_time = 0.0
        self.trap_time_remaining = 0.0
        self.trap_animation_offset = pygame.Vector2(0, 0)
        self.stun_time_remaining = 0.0
        self.locked_to_attack = False
        self.attack_lock_target = None
        self.shield_active = False
        self.shield_time_remaining = 0.0
        self.shield_cooldown = 0.0
        self.block_active = False
        self.block_time_remaining = 0.0
        self.block_cooldown = 0.0
        self.death_state = None
        self.death_height = 0.0
        self.speed = self.base_speed
        self.size = self.base_size
        # Health in half-hearts: 10 = 5 full hearts
        self.hearts = settings.PLAYER_HEALTH_MAX
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

    def tick(self, dt):
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
                self.locked_to_attack = False
                self.attack_lock_target = None

        if self.shield_time_remaining > 0:
            self.shield_time_remaining -= dt
            if self.shield_time_remaining <= 0:
                self.shield_time_remaining = 0.0
                self.shield_active = False
                self.shield_cooldown = settings.SHIELD_COOLDOWN

        if self.shield_cooldown > 0:
            self.shield_cooldown -= dt
            if self.shield_cooldown <= 0:
                self.shield_cooldown = 0.0

        if self.block_time_remaining > 0:
            self.block_time_remaining -= dt
            if self.block_time_remaining <= 0:
                self.block_time_remaining = 0.0
                self.block_active = False
                self.block_cooldown = settings.BLOCK_COOLDOWN

        if self.block_cooldown > 0:
            self.block_cooldown -= dt
            if self.block_cooldown <= 0:
                self.block_cooldown = 0.0

        if self.death_state == 'dying':
            self.death_height -= settings.PLAYER_DEATH_SPEED * dt
            if self.death_height <= 0:
                self.death_height = 0.0
                self.death_state = 'dead'
                self.alive = False
            return

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

    def can_shield(self):
        return not self.shield_active and self.shield_cooldown <= 0 and self.death_state is None and self.alive and not self.is_trapped() and self.stun_time_remaining <= 0

    def activate_shield(self):
        if not self.can_shield():
            return
        self.shield_active = True
        self.shield_time_remaining = settings.SHIELD_DURATION

    def can_block(self):
        return not self.block_active and self.block_cooldown <= 0 and self.death_state is None and self.alive and not self.is_trapped() and self.stun_time_remaining <= 0

    def activate_block(self):
        if not self.can_block():
            return
        self.block_active = True
        self.block_time_remaining = settings.BLOCK_DURATION

    def update(self, keys, dt):
        if not self.alive or self.is_trapped() or self.stun_time_remaining > 0 or self.death_state is not None:
            return
        vel = pygame.Vector2(0, 0)
        if keys[pygame.K_w]:
            vel.y = -1
        if keys[pygame.K_s]:
            vel.y = 1
        if keys[pygame.K_a]:
            vel.x = -1
        if keys[pygame.K_d]:
            vel.x = 1
        if vel.length_squared() > 0:
            vel = vel.normalize()
            self.direction = vel
            movement = vel * self.speed * dt
            self.rect.centerx += movement.x
            self.rect.centery += movement.y

        self.rect.clamp_ip(pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT))

    def draw(self, surface):
        if not self.alive and self.death_state != 'dying':
            return
        if self.death_state == 'dying':
            height_scale = max(0.0, min(1.0, self.death_height / settings.PLAYER_DEATH_HEIGHT))
        else:
            height_scale = 1.0
        draw_center = (
            self.rect.centerx + self.trap_animation_offset.x,
            self.rect.centery + self.trap_animation_offset.y,
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

        if self.shield_active:
            shield_dir = pygame.Vector2(math.cos(math.radians(self.mouse_angle)), math.sin(math.radians(self.mouse_angle)))
            perp = pygame.Vector2(-shield_dir.y, shield_dir.x)
            center = pygame.Vector2(draw_center) + shield_dir * (settings.SHIELD_RECT_LENGTH * 0.5)
            shield_rect = pygame.Rect(0, 0, settings.SHIELD_RECT_LENGTH, settings.SHIELD_RECT_WIDTH)
            shield_rect.center = center
            surf = pygame.Surface((shield_rect.width, shield_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(surf, settings.SHIELD_COLOR, surf.get_rect(), border_radius=10)
            surf = pygame.transform.rotate(surf, -self.mouse_angle)
            surface.blit(surf, surf.get_rect(center=shield_rect.center))
            outline_rect = pygame.Rect(0, 0, settings.SHIELD_RECT_LENGTH + 8, settings.SHIELD_RECT_WIDTH + 8)
            outline_rect.center = center
            outline_surf = pygame.Surface(outline_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(outline_surf, settings.SHIELD_BORDER_COLOR, outline_surf.get_rect(), width=3, border_radius=12)
            outline_surf = pygame.transform.rotate(outline_surf, -self.mouse_angle)
            surface.blit(outline_surf, outline_surf.get_rect(center=outline_rect.center))
        elif self.block_active:
            border_rect = pygame.Rect(0, 0, int(self.size * 1.2), int(self.size * 1.2))
            border_rect.center = draw_center
            pygame.draw.rect(surface, (120, 220, 255), border_rect, width=3, border_radius=10)
