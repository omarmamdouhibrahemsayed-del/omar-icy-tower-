import math
import random
import pygame
from characters import render_character_sprite
from settings import (
    DRAG_AIR,
    FAST_FALL_GRAVITY_MULT,
    FRICTION_GROUND,
    GRAVITY_BASE,
    JUMP_MOMENTUM_BOOST,
    JUMP_VELOCITY_BASE,
    MAX_FALL_SPEED,
    MAX_MOMENTUM_SPEED,
    MAX_WALK_SPEED,
    MOMENTUM_BUILD_RATE,
    MOMENTUM_DECAY_RATE,
    PLATFORM_HEIGHT,
    PLAYER_HEIGHT,
    PLAYER_WIDTH,
    RUN_ACCEL_AIR,
    RUN_ACCEL_GROUND,
    SCREEN_WIDTH,
    SPRING_JUMP_VELOCITY,
)

# ==============================================================================
# Icy Tower 50: Legends & Styles - Player, Platforms, Coins & Particles
# ==============================================================================


class Particle:
    """Lightweight visual particle for jumps, combos, coins, and broken ice."""

    def __init__(self, x, y, vx, vy, color, radius=4, life=0.45, gravity=240.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.radius = float(radius)
        self.life = float(life)
        self.max_life = max(0.01, float(life))
        self.gravity = float(gravity)

    def update(self, dt):
        self.life -= dt
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    @property
    def alive(self):
        return self.life > 0.0

    def draw(self, surface, camera_y):
        if not self.alive:
            return
        ratio = max(0.0, self.life / self.max_life)
        r = max(1, int(self.radius * ratio))
        sx = int(self.x)
        sy = int(self.y - camera_y)
        pygame.draw.circle(surface, self.color, (sx, sy), r)


class CoinPickup:
    """Collectible coin floating above platforms."""

    def __init__(self, x, y, value=15):
        self.x = float(x)
        self.y = float(y)
        self.base_y = float(y)
        self.value = int(value)
        self.radius = 10
        self.collected = False
        self.phase = random.uniform(0.0, math.pi * 2.0)

    def update(self, dt):
        self.phase += dt * 4.5
        self.y = self.base_y + math.sin(self.phase) * 4.0

    def rect(self):
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def draw(self, surface, camera_y):
        if self.collected:
            return
        sx = int(self.x)
        sy = int(self.y - camera_y)
        # Outer gold coin + inner shine
        pygame.draw.circle(surface, (245, 185, 28), (sx, sy), self.radius)
        pygame.draw.circle(surface, (255, 232, 118), (sx, sy), max(3, self.radius - 3))
        shine_x = sx - 2
        shine_y = sy - 3
        pygame.draw.circle(surface, (255, 255, 245), (shine_x, shine_y), 2)


class Platform:
    """
    Tower floor platform.
    Kinds:
      - 'normal': steady platform
      - 'ice': low friction / slippery feel
      - 'fragile': cracks and crumbles shortly after landing
      - 'moving': patrols horizontally between tower walls
      - 'spring': launches the player extra high
    """

    def __init__(
        self,
        floor_index,
        x,
        y,
        width,
        kind="normal",
        move_speed=0.0,
        move_dir=1,
        wall_left=56,
        wall_right=SCREEN_WIDTH - 56,
    ):
        self.floor_index = int(floor_index)
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(PLATFORM_HEIGHT)
        self.kind = kind
        self.move_speed = float(move_speed)
        self.move_dir = 1 if move_dir >= 0 else -1
        self.wall_left = float(wall_left)
        self.wall_right = float(wall_right)

        self.broken = False
        self.crumble_timer = 0.0
        self.crumbling = False
        self.spring_anim = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    def trigger_land(self):
        if self.kind == "fragile" and not self.crumbling:
            self.crumbling = True
            self.crumble_timer = 0.42
        elif self.kind == "spring":
            self.spring_anim = 0.25

    def update(self, dt):
        if self.broken:
            return

        if self.spring_anim > 0.0:
            self.spring_anim = max(0.0, self.spring_anim - dt)

        if self.kind == "moving" and self.move_speed > 0.0:
            self.x += self.move_dir * self.move_speed * dt
            if self.x <= self.wall_left:
                self.x = self.wall_left
                self.move_dir = 1
            elif self.x + self.width >= self.wall_right:
                self.x = self.wall_right - self.width
                self.move_dir = -1

        if self.kind == "fragile" and self.crumbling:
            self.crumble_timer -= dt
            if self.crumble_timer <= 0.0:
                self.broken = True

    def draw(self, surface, theme, camera_y, font_lib):
        if self.broken:
            return

        sx = int(self.x)
        sy = int(self.y - camera_y)
        w = int(self.width)
        h = int(self.height)

        if sy < -40 or sy > surface.get_height() + 40:
            return

        # Choose colors by platform kind
        if self.kind == "ice":
            fill = theme.plat_ice
            border = theme.plat_border
        elif self.kind == "fragile":
            fill = theme.plat_fragile
            border = (140, 62, 54)
        elif self.kind == "moving":
            fill = theme.plat_moving
            border = theme.plat_border
        elif self.kind == "spring":
            fill = theme.plat_normal
            border = theme.plat_border
        else:
            fill = theme.plat_normal
            border = theme.plat_border

        shake_x = 0
        if self.kind == "fragile" and self.crumbling:
            shake_x = random.randint(-3, 3)

        rect = pygame.Rect(sx + shake_x, sy, w, h)
        pygame.draw.rect(surface, fill, rect, border_radius=5)
        pygame.draw.rect(surface, border, rect, width=2, border_radius=5)

        # Top highlight strip
        highlight_rect = pygame.Rect(sx + shake_x + 3, sy + 2, max(4, w - 6), 4)
        pygame.draw.rect(surface, (255, 255, 255), highlight_rect, border_radius=2)

        # Kind visual accents
        if self.kind == "fragile":
            # Crack lines
            mid_x = sx + shake_x + w // 2
            pygame.draw.line(surface, border, (mid_x - 10, sy + 2), (mid_x, sy + h - 2), 2)
            pygame.draw.line(surface, border, (mid_x, sy + h // 2), (mid_x + 12, sy + h - 2), 2)
        elif self.kind == "moving":
            # Left/right directional chevrons
            pygame.draw.polygon(
                surface,
                (25, 35, 50),
                [(sx + 8, sy + h // 2), (sx + 14, sy + 5), (sx + 14, sy + h - 5)],
            )
            pygame.draw.polygon(
                surface,
                (25, 35, 50),
                [(sx + w - 8, sy + h // 2), (sx + w - 14, sy + 5), (sx + w - 14, sy + h - 5)],
            )
        elif self.kind == "spring":
            pad_h = 10 if self.spring_anim > 0 else 6
            pad_y = sy - pad_h
            pad_x = sx + w // 2 - 14
            pygame.draw.rect(surface, theme.plat_spring, (pad_x, pad_y, 28, pad_h), border_radius=3)

        # Floor number badge every 5 floors or milestone floors
        if self.floor_index > 0 and (self.floor_index % 5 == 0 or self.floor_index == 1):
            label = font_lib.render_text(f"F{self.floor_index}", 12, (20, 28, 42), bold=True)
            surface.blit(label, (sx + 6, sy + 3))


class Player:
    """
    Icy Tower style player entity with horizontal acceleration, friction,
    momentum build-up, momentum-boosted jumps, flip/spin on high momentum,
    and fast-fall via Down arrow.
    """

    def __init__(self, x, y, character_spec, wall_left=56, wall_right=SCREEN_WIDTH - 56):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.char_spec = character_spec
        self.wall_left = float(wall_left)
        self.wall_right = float(wall_right)

        self.on_ground = False
        self.fast_falling = False
        self.facing_right = True
        self.momentum = 0.0  # 0.0 .. 1.0
        self.spin_angle = 0.0
        self.spinning = False
        self.anim_phase = 0.0
        self.current_floor = 0
        self.last_landed_floor = 0
        self.combo = 0
        self.max_combo = 0
        self.trail = []  # list of (x, y, alpha, spec)

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    @property
    def feet_y(self):
        return self.y + self.height

    def set_character(self, character_spec):
        self.char_spec = character_spec

    def update(self, dt, keys, current_platform_kind="normal", sound_engine=None, particles=None):
        move_left = bool(keys[pygame.K_LEFT])
        move_right = bool(keys[pygame.K_RIGHT])
        jump_pressed = bool(keys[pygame.K_UP])
        fast_fall_held = bool(keys[pygame.K_DOWN]) and not self.on_ground

        self.fast_falling = fast_fall_held and self.vy > -120.0

        # Slip factor when standing on an ice platform (mitigated by character slip_resist)
        slip_factor = 1.0
        if self.on_ground and current_platform_kind == "ice":
            slip_factor = max(0.22, 0.58 - self.char_spec.slip_resist * 0.65)

        accel = (RUN_ACCEL_GROUND if self.on_ground else RUN_ACCEL_AIR) * slip_factor
        friction = (FRICTION_GROUND if self.on_ground else DRAG_AIR) * slip_factor

        dir_input = 0
        if move_left and not move_right:
            dir_input = -1
            self.facing_right = False
        elif move_right and not move_left:
            dir_input = 1
            self.facing_right = True

        max_speed = MAX_WALK_SPEED + (MAX_MOMENTUM_SPEED - MAX_WALK_SPEED) * (
            self.momentum * (0.85 + 0.25 * self.char_spec.momentum_mult)
        )

        if dir_input != 0:
            self.vx += dir_input * accel * dt
            if abs(self.vx) > max_speed:
                self.vx = math.copysign(max_speed, self.vx)

            # Build momentum when running briskly in a consistent direction
            if abs(self.vx) > MAX_WALK_SPEED * 0.65:
                gain = MOMENTUM_BUILD_RATE * self.char_spec.momentum_mult * dt / 360.0
                self.momentum = min(1.0, self.momentum + gain)
            else:
                self.momentum = max(0.0, self.momentum - (MOMENTUM_DECAY_RATE * 0.4) * dt / 360.0)
        else:
            # Apply friction / drag
            if abs(self.vx) > 0.0:
                drop = friction * dt
                if abs(self.vx) <= drop:
                    self.vx = 0.0
                else:
                    self.vx -= math.copysign(drop, self.vx)
            self.momentum = max(0.0, self.momentum - MOMENTUM_DECAY_RATE * dt / 360.0)

        # Jump from ground
        if jump_pressed and self.on_ground:
            high_momentum = self.momentum >= 0.45
            jump_v = (
                JUMP_VELOCITY_BASE
                + JUMP_MOMENTUM_BOOST * self.momentum
            ) * self.char_spec.jump_mult
            self.vy = jump_v
            self.on_ground = False
            self.fast_falling = False

            if high_momentum:
                self.spinning = True
                self.spin_angle = 0.0
                if sound_engine:
                    sound_engine.play_sfx("momentum_jump")
                if particles is not None:
                    for _ in range(10):
                        particles.append(
                            Particle(
                                self.x + self.width * 0.5,
                                self.y + self.height,
                                random.uniform(-140, 140),
                                random.uniform(-180, -40),
                                self.char_spec.trail_color,
                                radius=4,
                                life=0.38,
                            )
                        )
            else:
                self.spinning = False
                if sound_engine:
                    sound_engine.play_sfx("jump")

        # Gravity & fast-fall
        grav = GRAVITY_BASE * (FAST_FALL_GRAVITY_MULT if self.fast_falling else 1.0)
        self.vy = min(MAX_FALL_SPEED * (1.25 if self.fast_falling else 1.0), self.vy + grav * dt)

        # Integrate position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Tower left/right wall collision with subtle bounce if hitting at high speed
        if self.x < self.wall_left:
            self.x = self.wall_left
            if self.vx < -260.0:
                self.vx = -self.vx * 0.45
            else:
                self.vx = 0.0
        elif self.x + self.width > self.wall_right:
            self.x = self.wall_right - self.width
            if self.vx > 260.0:
                self.vx = -self.vx * 0.45
            else:
                self.vx = 0.0

        # Spin animation while airborne with momentum
        if not self.on_ground and self.spinning:
            spin_dir = -1.0 if self.facing_right else 1.0
            self.spin_angle += spin_dir * (520.0 + self.momentum * 360.0) * dt
        else:
            self.spinning = False
            self.spin_angle = 0.0

        # Running stride phase
        if self.on_ground and abs(self.vx) > 15.0:
            self.anim_phase += dt * (0.6 + abs(self.vx) / 140.0)
        else:
            self.anim_phase += dt * 0.2

        # Motion afterimage trail when moving fast or spinning
        if abs(self.vx) > 420.0 or self.spinning or self.fast_falling:
            self.trail.append((self.x, self.y, 110, self.facing_right, self.spin_angle))
            if len(self.trail) > 6:
                self.trail.pop(0)

        new_trail = []
        for tx, ty, alpha, t_face, t_spin in self.trail:
            n_alpha = alpha - int(360 * dt)
            if n_alpha > 10:
                new_trail.append((tx, ty, n_alpha, t_face, t_spin))
        self.trail = new_trail

    def draw(self, surface, camera_y):
        # Draw faint trail ghosts
        for tx, ty, alpha, t_face, t_spin in self.trail:
            ghost = render_character_sprite(
                self.char_spec,
                width=self.width,
                height=self.height,
                facing_right=t_face,
                anim_phase=self.anim_phase,
                airborne=not self.on_ground,
                momentum_ratio=self.momentum,
            )
            if abs(t_spin) > 1.0:
                ghost = pygame.transform.rotate(ghost, t_spin)
            ghost.set_alpha(max(0, min(140, alpha)))
            rect = ghost.get_rect(
                center=(int(tx + self.width * 0.5), int(ty - camera_y + self.height * 0.5))
            )
            surface.blit(ghost, rect)

        sprite = render_character_sprite(
            self.char_spec,
            width=self.width,
            height=self.height,
            facing_right=self.facing_right,
            anim_phase=self.anim_phase,
            airborne=not self.on_ground,
            momentum_ratio=self.momentum,
        )
        if self.spinning and abs(self.spin_angle) > 1.0:
            sprite = pygame.transform.rotate(sprite, self.spin_angle)

        draw_rect = sprite.get_rect(
            center=(int(self.x + self.width * 0.5), int(self.y - camera_y + self.height * 0.5))
        )
        surface.blit(sprite, draw_rect)