import math
import random
import sys
import pygame
from characters import get_character
from entities import CoinPickup, Particle, Platform, Player
from hud import GameplayHUD
from levels import LevelBackgroundRenderer, get_level
from settings import (
    APP_TITLE,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_GOLD,
    COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED,
    COLOR_DARK_PANEL,
    COLOR_MUTED_TEXT,
    COLOR_PANEL_BORDER,
    COLOR_WHITE,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    FontLibrary,
    SaveManager,
)
from shop_ui import CharacterShopScreen
from sound_engine import SoundEngine

# ==============================================================================
# Icy Tower 50: Legends & Styles - Main Application & Game Loop
# ==============================================================================


class IcyTowerGame:
    """Main controller managing menus, 50-level tower generation, physics, audio, and UI."""

    STATE_MENU = "menu"
    STATE_LEVEL_SELECT = "level_select"
    STATE_AUDIO_SETTINGS = "audio_settings"
    STATE_SHOP = "shop"
    STATE_PLAYING = "playing"

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(APP_TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.save_manager = SaveManager()
        self.font_lib = FontLibrary()
        self.sound_engine = SoundEngine(self.save_manager.audio)
        self.hud = GameplayHUD(self.font_lib)
        self.shop_screen = CharacterShopScreen(self.save_manager, self.sound_engine, self.font_lib)
        self.bg_renderer = LevelBackgroundRenderer()

        self.state = self.STATE_MENU
        self.previous_state = self.STATE_MENU
        self.selected_level_num = min(50, max(1, self.save_manager.highest_unlocked_level))
        self.level_page = (self.selected_level_num - 1) // 10

        self.elapsed_time = 0.0
        self.running = True

        # Active gameplay state
        self.level_cfg = get_level(self.selected_level_num)
        self.player = None
        self.platforms = []
        self.coins = []
        self.particles = []
        self.camera_y = 0.0
        self.highest_floor_reached = 0
        self.score = 0.0
        self.session_coins = 0
        self.paused = False
        self.esc_menu_open = False
        self.round_ended = False
        self.round_won = False
        self.round_reason = ""
        self.banner_text = ""
        self.banner_timer = 0.0
        self.generated_up_to_floor = 0
        self.next_platform_y = 0.0

        # Menu & audio UI rects
        self.menu_play_btn = pygame.Rect(SCREEN_WIDTH // 2 - 180, 290, 360, 56)
        self.menu_levels_btn = pygame.Rect(SCREEN_WIDTH // 2 - 180, 362, 360, 54)
        self.menu_shop_btn = pygame.Rect(SCREEN_WIDTH // 2 - 180, 432, 360, 54)
        self.menu_audio_btn = pygame.Rect(SCREEN_WIDTH // 2 - 180, 502, 360, 54)
        self.menu_quit_btn = pygame.Rect(SCREEN_WIDTH // 2 - 180, 572, 360, 52)

        self.lvl_back_btn = pygame.Rect(32, 24, 175, 46)
        self.lvl_prev_page_btn = pygame.Rect(40, SCREEN_HEIGHT - 84, 155, 46)
        self.lvl_next_page_btn = pygame.Rect(212, SCREEN_HEIGHT - 84, 155, 46)
        self.lvl_start_btn = pygame.Rect(SCREEN_WIDTH - 340, SCREEN_HEIGHT - 86, 300, 52)
        self.lvl_card_rects = []

        self.audio_back_btn = pygame.Rect(32, 24, 175, 46)
        self.audio_music_toggle_btn = pygame.Rect(SCREEN_WIDTH // 2 - 190, 220, 380, 52)
        self.audio_sfx_toggle_btn = pygame.Rect(SCREEN_WIDTH // 2 - 190, 290, 380, 52)
        self.audio_vol_down_btn = pygame.Rect(SCREEN_WIDTH // 2 - 190, 375, 110, 48)
        self.audio_vol_up_btn = pygame.Rect(SCREEN_WIDTH // 2 + 80, 375, 110, 48)

        self.sound_engine.configure_for_level(self.selected_level_num, self.level_cfg.theme_key)

    def _set_banner(self, text, duration=1.8):
        self.banner_text = text
        self.banner_timer = duration

    def _open_shop(self, return_state):
        self.previous_state = return_state
        self.state = self.STATE_SHOP
        self.sound_engine.play_sfx("ui_click")

    def start_level(self, level_num):
        self.selected_level_num = max(1, min(50, int(level_num)))
        self.level_cfg = get_level(self.selected_level_num)
        self.sound_engine.configure_for_level(self.level_cfg.level_num, self.level_cfg.theme_key)

        char_spec = get_character(self.save_manager.selected_character)
        wall_left = 56
        wall_right = SCREEN_WIDTH - 56

        # Floor 0 spans almost full tower width as starting safe deck
        start_y = SCREEN_HEIGHT - 110
        self.platforms = [
            Platform(
                floor_index=0,
                x=wall_left + 12,
                y=start_y,
                width=(wall_right - wall_left) - 24,
                kind="normal",
                wall_left=wall_left,
                wall_right=wall_right,
            )
        ]
        self.coins = []
        self.particles = []

        player_x = SCREEN_WIDTH * 0.5 - 17
        player_y = start_y - 48
        self.player = Player(player_x, player_y, char_spec, wall_left=wall_left, wall_right=wall_right)

        self.camera_y = 0.0
        self.highest_floor_reached = 0
        self.score = 0.0
        self.session_coins = 0
        self.paused = False
        self.esc_menu_open = False
        self.round_ended = False
        self.round_won = False
        self.round_reason = ""
        self.generated_up_to_floor = 0
        self.next_platform_y = start_y - self.level_cfg.floor_spacing

        self._generate_floors_until(self.level_cfg.target_floor + 12)
        self._set_banner(
            f"المستوى {self.level_cfg.level_num}: {self.level_cfg.title_ar} — {self.level_cfg.objective_ar}",
            2.6,
        )
        self.state = self.STATE_PLAYING

    def _generate_floors_until(self, max_floor):
        rng = random.Random(self.level_cfg.level_num * 9973 + self.generated_up_to_floor * 131)
        wall_left = 56
        wall_right = SCREEN_WIDTH - 56
        playable_w = wall_right - wall_left

        while self.generated_up_to_floor < max_floor:
            floor_idx = self.generated_up_to_floor + 1
            width = rng.randint(self.level_cfg.plat_width_min, self.level_cfg.plat_width_max)
            width = min(width, playable_w - 20)
            x = rng.uniform(wall_left + 8, wall_right - width - 8)
            y = self.next_platform_y

            # Choose platform kind based on level ratios
            roll = rng.random()
            kind = "normal"
            move_speed = 0.0
            move_dir = rng.choice([-1, 1])

            if floor_idx == self.level_cfg.target_floor:
                # Target floor is wide and reliable
                width = max(width, 190)
                x = SCREEN_WIDTH * 0.5 - width * 0.5
                kind = "normal"
            elif roll < self.level_cfg.moving_ratio:
                kind = "moving"
                move_speed = 65.0 + (self.level_cfg.level_num / 50.0) * 125.0 + rng.uniform(-15, 25)
            elif roll < self.level_cfg.moving_ratio + self.level_cfg.fragile_ratio:
                kind = "fragile"
            elif roll < self.level_cfg.moving_ratio + self.level_cfg.fragile_ratio + self.level_cfg.spring_ratio:
                kind = "spring"
            elif roll < (
                self.level_cfg.moving_ratio
                + self.level_cfg.fragile_ratio
                + self.level_cfg.spring_ratio
                + self.level_cfg.ice_ratio
            ):
                kind = "ice"

            plat = Platform(
                floor_index=floor_idx,
                x=x,
                y=y,
                width=width,
                kind=kind,
                move_speed=move_speed,
                move_dir=move_dir,
                wall_left=wall_left,
                wall_right=wall_right,
            )
            self.platforms.append(plat)

            # Spawn coin above platform
            if rng.random() < self.level_cfg.coin_density:
                coin_val = int((12 + self.level_cfg.level_num // 3) * self.player.char_spec.coin_mult)
                self.coins.append(CoinPickup(x + width * 0.5, y - 22, value=max(10, coin_val)))

            self.generated_up_to_floor = floor_idx
            self.next_platform_y -= self.level_cfg.floor_spacing

    def _finish_round(self, won, reason_ar):
        if self.round_ended:
            return
        self.round_ended = True
        self.round_won = bool(won)
        self.round_reason = reason_ar
        self.esc_menu_open = False
        self.paused = False

        # Award coins earned during run (bonus if level cleared)
        bonus_coins = (45 + self.level_cfg.level_num * 5) if self.round_won else 0
        total_earned = self.session_coins + bonus_coins
        self.save_manager.coins += total_earned
        self.save_manager.data["total_score"] = int(self.save_manager.data.get("total_score", 0) + self.score)
        self.save_manager.record_level_result(
            level_num=self.level_cfg.level_num,
            score=int(self.score),
            max_combo=self.player.max_combo,
            completed=self.round_won,
        )
        self.session_coins = total_earned

        if self.round_won:
            self.sound_engine.play_sfx("level_up")
        else:
            self.sound_engine.play_sfx("game_over")

    def _evaluate_level_victory(self):
        floor_ok = self.highest_floor_reached >= self.level_cfg.target_floor
        combo_ok = self.player.max_combo >= self.level_cfg.min_combo_req
        score_ok = int(self.score) >= self.level_cfg.min_score_req
        if floor_ok and combo_ok and score_ok:
            self._finish_round(
                True,
                f"تم تحقيق هدف المستوى {self.level_cfg.level_num} بنجاح!",
            )
        elif floor_ok and not combo_ok:
            self._finish_round(
                False,
                f"وصلت للقمة لكن الـ Combo المطلوب {self.level_cfg.min_combo_req}x (أقصاه {self.player.max_combo}x)",
            )
        elif floor_ok and not score_ok:
            self._finish_round(
                False,
                f"وصلت للقمة لكن النقاط المطلوبة {self.level_cfg.min_score_req} (جمعت {int(self.score)})",
            )

    def _update_playing(self, dt):
        # Refresh selected character in case player switched inside Shop
        active_char = get_character(self.save_manager.selected_character)
        if self.player.char_spec.char_id != active_char.char_id:
            self.player.set_character(active_char)

        if self.banner_timer > 0.0:
            self.banner_timer = max(0.0, self.banner_timer - dt)
            if self.banner_timer == 0.0:
                self.banner_text = ""

        # Update particles even when round ends
        for pt in self.particles:
            pt.update(dt)
        self.particles = [pt for pt in self.particles if pt.alive]

        if self.paused or self.esc_menu_open or self.round_ended:
            return

        # Keep generating floors ahead of player
        if self.player.current_floor + 14 > self.generated_up_to_floor:
            self._generate_floors_until(self.player.current_floor + 20)

        # Update platforms
        for plat in self.platforms:
            plat.update(dt)

        # Update coins
        for c in self.coins:
            c.update(dt)

        keys = pygame.key.get_pressed()
        prev_feet = self.player.feet_y
        standing_kind = "normal"
        if self.player.on_ground:
            for plat in self.platforms:
                if not plat.broken and abs(self.player.feet_y - plat.y) <= 4.0:
                    if self.player.x + self.player.width > plat.x and self.player.x < plat.x + plat.width:
                        standing_kind = plat.kind
                        break

        self.player.update(
            dt,
            keys,
            current_platform_kind=standing_kind,
            sound_engine=self.sound_engine,
            particles=self.particles,
        )

        # Optional drop-through fragile/ice/normal? Keep classic Icy Tower solid platforms with fast-fall
        landed_plat = None
        if self.player.vy >= 0.0:
            for plat in self.platforms:
                if plat.broken:
                    continue
                horizontally_over = (self.player.x + self.player.width - 5) >= plat.x and (
                    self.player.x + 5
                ) <= (plat.x + plat.width)
                crossed_top = prev_feet <= plat.y + 10.0 and self.player.feet_y >= plat.y
                if horizontally_over and crossed_top:
                    landed_plat = plat
                    break

        if landed_plat is not None:
            was_airborne = not self.player.on_ground
            self.player.y = landed_plat.y - self.player.height
            self.player.vy = 0.0
            self.player.on_ground = True
            self.player.fast_falling = False
            self.player.spinning = False
            self.player.spin_angle = 0.0
            landed_plat.trigger_land()

            if was_airborne:
                self.sound_engine.play_sfx("land")
                for _ in range(5):
                    self.particles.append(
                        Particle(
                            self.player.x + self.player.width * 0.5,
                            self.player.feet_y,
                            random.uniform(-90, 90),
                            random.uniform(-70, -15),
                            self.level_cfg.theme.accent,
                            radius=3,
                            life=0.28,
                        )
                    )

                # Combo & floor progression logic
                if landed_plat.floor_index > self.player.current_floor:
                    floors_jumped = landed_plat.floor_index - self.player.current_floor
                    if floors_jumped >= 2:
                        self.player.combo += floors_jumped - 1
                        self.player.max_combo = max(self.player.max_combo, self.player.combo)
                        self.sound_engine.play_sfx("combo")
                        self._set_banner(f"Combo {self.player.combo}x! (+{floors_jumped} طوابق)", 1.1)
                    else:
                        self.player.combo = max(1, self.player.combo)
                        self.player.max_combo = max(self.player.max_combo, self.player.combo)

                    self.player.current_floor = landed_plat.floor_index
                    if self.player.current_floor > self.highest_floor_reached:
                        diff = self.player.current_floor - self.highest_floor_reached
                        self.highest_floor_reached = self.player.current_floor
                        gain = diff * 120 * max(1, self.player.combo) * self.player.char_spec.score_mult
                        self.score += gain

                    self._evaluate_level_victory()
                    if self.round_ended:
                        return

                # Spring launch
                if landed_plat.kind == "spring":
                    self.player.vy = -1140.0 * self.player.char_spec.jump_mult
                    self.player.on_ground = False
                    self.player.spinning = True
                    self.sound_engine.play_sfx("spring")
                    self._set_banner("قفزة نابضة مرتفعة!", 1.0)

                # Fragile platform crumble effect
                if landed_plat.kind == "fragile":
                    self.sound_engine.play_sfx("break_plat")
        else:
            # Check if still supported by a non-broken platform
            still_supported = False
            if abs(self.player.vy) < 1e-3:
                for plat in self.platforms:
                    if not plat.broken and abs(self.player.feet_y - plat.y) <= 2.0:
                        if (self.player.x + self.player.width - 5) >= plat.x and (
                            self.player.x + 5
                        ) <= (plat.x + plat.width):
                            still_supported = True
                            break
            if not still_supported:
                self.player.on_ground = False

        # Collect coins
        p_rect = self.player.rect
        for coin in self.coins:
            if not coin.collected and p_rect.colliderect(coin.rect()):
                coin.collected = True
                self.session_coins += coin.value
                self.score += coin.value * 8 * self.player.char_spec.score_mult
                self.sound_engine.play_sfx("coin")
                for _ in range(6):
                    self.particles.append(
                        Particle(
                            coin.x,
                            coin.y,
                            random.uniform(-80, 80),
                            random.uniform(-110, -20),
                            COLOR_ACCENT_GOLD,
                            radius=3,
                            life=0.35,
                        )
                    )
        self.coins = [c for c in self.coins if not c.collected]

        # Camera auto-scroll upward + catch-up if player climbs high
        scroll_spd = self.level_cfg.camera_speed
        if self.highest_floor_reached >= 2:
            scroll_spd *= 1.0 + min(0.65, self.highest_floor_reached * 0.025)
        self.camera_y -= scroll_spd * dt

        target_cam_if_high = self.player.y - SCREEN_HEIGHT * 0.36
        if target_cam_if_high < self.camera_y:
            self.camera_y += (target_cam_if_high - self.camera_y) * min(1.0, dt * 7.5)

        # Prune far-below platforms & coins
        bottom_world = self.camera_y + SCREEN_HEIGHT + 240
        self.platforms = [p for p in self.platforms if p.y < bottom_world]
        self.coins = [c for c in self.coins if c.y < bottom_world]

        # Check fall off bottom of screen
        if self.player.y - self.camera_y > SCREEN_HEIGHT + 45:
            self._finish_round(False, "سقطت أسفل حدود الكاميرا — حاول مجدداً!")

    def _draw_playing(self):
        self.bg_renderer.draw(self.screen, self.level_cfg, self.camera_y, self.elapsed_time)

        for plat in self.platforms:
            plat.draw(self.screen, self.level_cfg.theme, self.camera_y, self.font_lib)

        for coin in self.coins:
            coin.draw(self.screen, self.camera_y)

        for pt in self.particles:
            pt.draw(self.screen, self.camera_y)

        if self.player:
            self.player.draw(self.screen, self.camera_y)

        self.hud.draw_top_hud(
            surface=self.screen,
            level_cfg=self.level_cfg,
            player=self.player,
            score=self.score,
            session_coins=self.session_coins,
            total_coins=self.save_manager.coins,
            paused=self.paused,
            banner_text=self.banner_text,
        )

        if self.esc_menu_open:
            self.hud.draw_esc_menu(self.screen, self.paused)
        elif self.round_ended:
            self.hud.draw_end_overlay(
                surface=self.screen,
                level_cfg=self.level_cfg,
                won=self.round_won,
                score=self.score,
                max_combo=self.player.max_combo,
                coins_earned=self.session_coins,
                reason_ar=self.round_reason,
            )

    def _handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.sound_engine.play_sfx("ui_click")
                self.start_level(self.selected_level_num)
            elif event.key == pygame.K_ESCAPE:
                self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.menu_play_btn.collidepoint(pos):
                self.sound_engine.play_sfx("ui_click")
                self.start_level(self.selected_level_num)
            elif self.menu_levels_btn.collidepoint(pos):
                self.sound_engine.play_sfx("ui_click")
                self.level_page = (self.selected_level_num - 1) // 10
                self.state = self.STATE_LEVEL_SELECT
            elif self.menu_shop_btn.collidepoint(pos):
                self._open_shop(self.STATE_MENU)
            elif self.menu_audio_btn.collidepoint(pos):
                self.sound_engine.play_sfx("ui_click")
                self.state = self.STATE_AUDIO_SETTINGS
            elif self.menu_quit_btn.collidepoint(pos):
                self.running = False

    def _draw_menu(self):
        self.bg_renderer.draw(self.screen, self.level_cfg, self.camera_y, self.elapsed_time)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 14, 26, 155))
        self.screen.blit(overlay, (0, 0))

        title = self.font_lib.render_text("ICY TOWER 50: LEGENDS & STYLES", 42, COLOR_ACCENT_CYAN, bold=True)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 118)))

        sub = self.font_lib.render_text(
            "50 مستوى متنوع • 14 شخصية Pixel Art • فيزياء زخم وقفز كلاسيكية",
            18,
            COLOR_WHITE,
        )
        self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 168)))

        info = self.font_lib.render_text(
            f"العملات: {self.save_manager.coins}  |  أعلى مستوى مفتوح: {self.save_manager.highest_unlocked_level}/50  |  أعلى نقاط: {self.save_manager.best_score}",
            16,
            COLOR_ACCENT_GOLD,
            bold=True,
        )
        self.screen.blit(info, info.get_rect(center=(SCREEN_WIDTH // 2, 212)))

        buttons = [
            (self.menu_play_btn, f"ابدأ اللعب — المستوى {self.selected_level_num}", (32, 116, 76), COLOR_ACCENT_GREEN),
            (self.menu_levels_btn, "اختيار مستوى (1 إلى 50)", (36, 68, 118), COLOR_ACCENT_CYAN),
            (self.menu_shop_btn, "متجر الشخصيات (14 شخصية)", (148, 104, 24), COLOR_ACCENT_GOLD),
            (self.menu_audio_btn, "إعدادات الصوت والموسيقى", (48, 58, 96), COLOR_ACCENT_CYAN),
            (self.menu_quit_btn, "خروج من اللعبة", (86, 36, 46), COLOR_ACCENT_RED),
        ]
        for rect, label, fill, border in buttons:
            pygame.draw.rect(self.screen, fill, rect, border_radius=10)
            pygame.draw.rect(self.screen, border, rect, width=2, border_radius=10)
            lbl = self.font_lib.render_text(label, 19, COLOR_WHITE, bold=True)
            self.screen.blit(lbl, lbl.get_rect(center=rect.center))

        hint = self.font_lib.render_text(
            "التحكم: الأسهم (يمين/يسار للزخم، أعلى للقفز، أسفل للنزول السريع) • ESC للقائمة والمتجر",
            14,
            COLOR_MUTED_TEXT,
        )
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 36)))

    def _handle_level_select_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.sound_engine.play_sfx("ui_click")
                self.state = self.STATE_MENU
            elif event.key == pygame.K_LEFT:
                self.sound_engine.play_sfx("ui_click")
                self.level_page = (self.level_page - 1) % 5
                self.selected_level_num = self.level_page * 10 + 1
                cfg = get_level(self.selected_level_num)
                self.sound_engine.configure_for_level(cfg.level_num, cfg.theme_key)
            elif event.key == pygame.K_RIGHT:
                self.sound_engine.play_sfx("ui_click")
                self.level_page = (self.level_page + 1) % 5
                self.selected_level_num = self.level_page * 10 + 1
                cfg = get_level(self.selected_level_num)
                self.sound_engine.configure_for_level(cfg.level_num, cfg.theme_key)
            elif event.key == pygame.K_RETURN:
                self.start_level(self.selected_level_num)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.lvl_back_btn.collidepoint(pos):
                self.sound_engine.play_sfx("ui_click")
                self.state = self.STATE_MENU
                return
            if self.lvl_prev_page_btn.collidepoint(pos):
                self.sound_engine.play_sfx("ui_click")
                self.level_page = (self.level_page - 1) % 5
                return
            if self.lvl_next_page_btn.collidepoint(pos):
                self.sound_engine.play_sfx("ui_click")
                self.level_page = (self.level_page + 1) % 5
                return
            for lvl_num, rect in self.lvl_card_rects:
                if rect.collidepoint(pos):
                    if lvl_num <= self.save_manager.highest_unlocked_level:
                        self.sound_engine.play_sfx("ui_click")
                        self.selected_level_num = lvl_num
                        cfg = get_level(lvl_num)
                        self.sound_engine.configure_for_level(cfg.level_num, cfg.theme_key)
                    else:
                        self.sound_engine.play_sfx("ui_click")
            if self.lvl_start_btn.collidepoint(pos):
                if self.selected_level_num <= self.save_manager.highest_unlocked_level:
                    self.start_level(self.selected_level_num)

    def _draw_level_select(self):
        self.screen.fill((12, 19, 34))
        pygame.draw.rect(self.screen, (18, 28, 48), (0, 0, SCREEN_WIDTH, 88))
        pygame.draw.line(self.screen, COLOR_PANEL_BORDER, (0, 88), (SCREEN_WIDTH, 88), 2)

        pygame.draw.rect(self.screen, (34, 52, 84), self.lvl_back_btn, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_ACCENT_CYAN, self.lvl_back_btn, width=2, border_radius=8)
        b_lbl = self.font_lib.render_text("← القائمة", 18, COLOR_WHITE, bold=True)
        self.screen.blit(b_lbl, b_lbl.get_rect(center=self.lvl_back_btn.center))

        title = self.font_lib.render_text(
            f"منتقي المستويات (1 - 50) • المجموعة {self.level_page + 1} / 5",
            26,
            COLOR_ACCENT_CYAN,
            bold=True,
        )
        self.screen.blit(title, (235, 24))

        self.lvl_card_rects = []
        start_num = self.level_page * 10 + 1
        end_num = min(50, start_num + 9)

        cols = 5
        card_w = 196
        card_h = 112
        gap_x = 14
        gap_y = 16
        grid_x = 40
        grid_y = 112

        for idx, lvl_num in enumerate(range(start_num, end_num + 1)):
            r_idx = idx // cols
            c_idx = idx % cols
            rect = pygame.Rect(
                grid_x + c_idx * (card_w + gap_x),
                grid_y + r_idx * (card_h + gap_y),
                card_w,
                card_h,
            )
            self.lvl_card_rects.append((lvl_num, rect))

            cfg = get_level(lvl_num)
            unlocked = lvl_num <= self.save_manager.highest_unlocked_level
            selected = lvl_num == self.selected_level_num
            rec = self.save_manager.data["level_records"].get(str(lvl_num), {})
            completed = bool(rec.get("completed", False))

            fill = (34, 58, 96) if selected else ((22, 34, 56) if unlocked else (16, 22, 34))
            border = COLOR_ACCENT_GOLD if selected else (cfg.theme.accent if unlocked else (52, 64, 84))
            pygame.draw.rect(self.screen, fill, rect, border_radius=10)
            pygame.draw.rect(self.screen, border, rect, width=3 if selected else 1, border_radius=10)

            n_lbl = self.font_lib.render_text(
                f"المستوى {lvl_num}" + (" ✓" if completed else ""),
                17,
                COLOR_ACCENT_GREEN if completed else (COLOR_WHITE if unlocked else COLOR_MUTED_TEXT),
                bold=True,
            )
            self.screen.blit(n_lbl, (rect.left + 12, rect.top + 10))

            t_lbl = self.font_lib.render_text(cfg.title_ar, 14, cfg.theme.accent if unlocked else COLOR_MUTED_TEXT)
            self.screen.blit(t_lbl, (rect.left + 12, rect.top + 38))

            status_lbl = self.font_lib.render_text(
                f"طابق {cfg.target_floor} • {cfg.theme.name_ar}" if unlocked else "مغلق",
                12,
                COLOR_MUTED_TEXT,
            )
            self.screen.blit(status_lbl, (rect.left + 12, rect.top + 68))

        # Selected level summary panel
        sel_cfg = get_level(self.selected_level_num)
        info_rect = pygame.Rect(40, 368, SCREEN_WIDTH - 80, 278)
        pygame.draw.rect(self.screen, COLOR_DARK_PANEL, info_rect, border_radius=12)
        pygame.draw.rect(self.screen, sel_cfg.theme.accent, info_rect, width=2, border_radius=12)

        s_title = self.font_lib.render_text(
            f"تفاصيل المستوى {sel_cfg.level_num}: {sel_cfg.title_ar} ({sel_cfg.title_en})",
            22,
            COLOR_WHITE,
            bold=True,
        )
        self.screen.blit(s_title, (info_rect.left + 24, info_rect.top + 20))

        details = [
            f"الثيم والصوت: {sel_cfg.theme.name_ar} (نغمة وإيقاع خاص بالمستوى {sel_cfg.level_num})",
            f"الهدف: {sel_cfg.objective_ar}",
            f"سرعة الكاميرا: {sel_cfg.camera_speed:.1f} px/s  |  المسافة بين الطوابق: {sel_cfg.floor_spacing} px",
            f"نسب المنصات: متحركة {int(sel_cfg.moving_ratio*100)}% • هشة {int(sel_cfg.fragile_ratio*100)}% • جليدية {int(sel_cfg.ice_ratio*100)}% • نابضة {int(sel_cfg.spring_ratio*100)}%",
        ]
        for i, line in enumerate(details):
            d_surf = self.font_lib.render_text(line, 16, COLOR_ACCENT_CYAN if i == 1 else COLOR_WHITE)
            self.screen.blit(d_surf, (info_rect.left + 24, info_rect.top + 60 + i * 32))

        pygame.draw.rect(self.screen, (28, 44, 72), self.lvl_prev_page_btn, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, self.lvl_prev_page_btn, width=2, border_radius=8)
        p_lbl = self.font_lib.render_text("← مجموعة سابقة", 15, COLOR_WHITE, bold=True)
        self.screen.blit(p_lbl, p_lbl.get_rect(center=self.lvl_prev_page_btn.center))

        pygame.draw.rect(self.screen, (28, 44, 72), self.lvl_next_page_btn, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, self.lvl_next_page_btn, width=2, border_radius=8)
        n_lbl = self.font_lib.render_text("مجموعة تالية →", 15, COLOR_WHITE, bold=True)
        self.screen.blit(n_lbl, n_lbl.get_rect(center=self.lvl_next_page_btn.center))

        pygame.draw.rect(self.screen, (34, 118, 78), self.lvl_start_btn, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_ACCENT_GREEN, self.lvl_start_btn, width=2, border_radius=8)
        st_lbl = self.font_lib.render_text(f"دخول المستوى {sel_cfg.level_num}", 18, COLOR_WHITE, bold=True)
        self.screen.blit(st_lbl, st_lbl.get_rect(center=self.lvl_start_btn.center))

    def _handle_audio_settings_event(self, event):
        audio = self.save_manager.audio
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.sound_engine.play_sfx("ui_click")
            self.state = self.STATE_MENU
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.audio_back_btn.collidepoint(pos):
                self.sound_engine.play_sfx("ui_click")
                self.state = self.STATE_MENU
            elif self.audio_music_toggle_btn.collidepoint(pos):
                audio["music_enabled"] = not bool(audio.get("music_enabled", True))
                self.sound_engine.sync_settings(audio)
                self.save_manager.save()
                self.sound_engine.play_sfx("ui_click")
            elif self.audio_sfx_toggle_btn.collidepoint(pos):
                audio["sfx_enabled"] = not bool(audio.get("sfx_enabled", True))
                self.sound_engine.sync_settings(audio)
                self.save_manager.save()
                self.sound_engine.play_sfx("ui_click")
            elif self.audio_vol_down_btn.collidepoint(pos):
                cur = float(audio.get("master_volume", 0.75))
                audio["master_volume"] = max(0.0, round(cur - 0.1, 2))
                self.sound_engine.sync_settings(audio)
                self.save_manager.save()
                self.sound_engine.play_sfx("ui_click")
            elif self.audio_vol_up_btn.collidepoint(pos):
                cur = float(audio.get("master_volume", 0.75))
                audio["master_volume"] = min(1.0, round(cur + 0.1, 2))
                self.sound_engine.sync_settings(audio)
                self.save_manager.save()
                self.sound_engine.play_sfx("ui_click")

    def _draw_audio_settings(self):
        self.screen.fill((12, 20, 36))
        pygame.draw.rect(self.screen, (18, 30, 52), (0, 0, SCREEN_WIDTH, 88))
        pygame.draw.line(self.screen, COLOR_PANEL_BORDER, (0, 88), (SCREEN_WIDTH, 88), 2)

        pygame.draw.rect(self.screen, (34, 52, 84), self.audio_back_btn, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_ACCENT_CYAN, self.audio_back_btn, width=2, border_radius=8)
        b_lbl = self.font_lib.render_text("← القائمة", 18, COLOR_WHITE, bold=True)
        self.screen.blit(b_lbl, b_lbl.get_rect(center=self.audio_back_btn.center))

        title = self.font_lib.render_text("إعدادات الصوت والموسيقى (1 - 50 مستوى)", 28, COLOR_ACCENT_CYAN, bold=True)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2 + 60, 44)))

        audio = self.save_manager.audio
        music_on = bool(audio.get("music_enabled", True))
        sfx_on = bool(audio.get("sfx_enabled", True))
        vol_pct = int(round(float(audio.get("master_volume", 0.75)) * 100))

        pygame.draw.rect(
            self.screen,
            (34, 112, 76) if music_on else (78, 38, 48),
            self.audio_music_toggle_btn,
            border_radius=10,
        )
        pygame.draw.rect(
            self.screen,
            COLOR_ACCENT_GREEN if music_on else COLOR_ACCENT_RED,
            self.audio_music_toggle_btn,
            width=2,
            border_radius=10,
        )
        m_lbl = self.font_lib.render_text(
            f"موسيقى المستوى: {'مفعّلة (ON)' if music_on else 'مكتومة (OFF)'}",
            19,
            COLOR_WHITE,
            bold=True,
        )
        self.screen.blit(m_lbl, m_lbl.get_rect(center=self.audio_music_toggle_btn.center))

        pygame.draw.rect(
            self.screen,
            (34, 112, 76) if sfx_on else (78, 38, 48),
            self.audio_sfx_toggle_btn,
            border_radius=10,
        )
        pygame.draw.rect(
            self.screen,
            COLOR_ACCENT_GREEN if sfx_on else COLOR_ACCENT_RED,
            self.audio_sfx_toggle_btn,
            width=2,
            border_radius=10,
        )
        s_lbl = self.font_lib.render_text(
            f"المؤثرات الصوتية (SFX): {'مفعّلة (ON)' if sfx_on else 'مكتومة (OFF)'}",
            19,
            COLOR_WHITE,
            bold=True,
        )
        self.screen.blit(s_lbl, s_lbl.get_rect(center=self.audio_sfx_toggle_btn.center))

        vol_title = self.font_lib.render_text(f"مستوى الصوت العام: {vol_pct}%", 20, COLOR_ACCENT_GOLD, bold=True)
        self.screen.blit(vol_title, vol_title.get_rect(center=(SCREEN_WIDTH // 2, 352)))

        pygame.draw.rect(self.screen, (36, 62, 102), self.audio_vol_down_btn, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_ACCENT_CYAN, self.audio_vol_down_btn, width=2, border_radius=8)
        vd_lbl = self.font_lib.render_text("-10%", 18, COLOR_WHITE, bold=True)
        self.screen.blit(vd_lbl, vd_lbl.get_rect(center=self.audio_vol_down_btn.center))

        pygame.draw.rect(self.screen, (36, 62, 102), self.audio_vol_up_btn, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_ACCENT_CYAN, self.audio_vol_up_btn, width=2, border_radius=8)
        vu_lbl = self.font_lib.render_text("+10%", 18, COLOR_WHITE, bold=True)
        self.screen.blit(vu_lbl, vu_lbl.get_rect(center=self.audio_vol_up_btn.center))

        note = self.font_lib.render_text(
            "ملاحظة: يتغير السلم الموسيقي والإيقاع ونبرة المؤثرات تلقائياً مع كل مستوى من 1 إلى 50.",
            15,
            COLOR_MUTED_TEXT,
        )
        self.screen.blit(note, note.get_rect(center=(SCREEN_WIDTH // 2, 465)))

    def _handle_playing_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if not self.round_ended:
                    self.sound_engine.play_sfx("ui_click")
                    self.esc_menu_open = not self.esc_menu_open
                    self.paused = self.esc_menu_open
            elif event.key == pygame.K_p and not self.round_ended and not self.esc_menu_open:
                self.sound_engine.play_sfx("ui_click")
                self.paused = not self.paused

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.round_ended:
                act = self.hud.handle_end_click(pos, won_next=self.round_won and self.level_cfg.level_num < 50)
                if act == "next_level":
                    self.sound_engine.play_sfx("ui_click")
                    self.start_level(self.level_cfg.level_num + 1)
                elif act == "restart":
                    self.sound_engine.play_sfx("ui_click")
                    self.start_level(self.level_cfg.level_num)
                elif act == "open_shop":
                    self._open_shop(self.STATE_PLAYING)
                elif act == "main_menu":
                    self.sound_engine.play_sfx("ui_click")
                    self.state = self.STATE_MENU
                return

            if self.esc_menu_open:
                act = self.hud.handle_esc_click(pos)
                if act == "resume":
                    self.sound_engine.play_sfx("ui_click")
                    self.esc_menu_open = False
                    self.paused = False
                elif act == "open_shop":
                    self.esc_menu_open = True
                    self.paused = True
                    self._open_shop(self.STATE_PLAYING)
                elif act == "restart":
                    self.sound_engine.play_sfx("ui_click")
                    self.start_level(self.level_cfg.level_num)
                elif act == "main_menu":
                    self.sound_engine.play_sfx("ui_click")
                    self.esc_menu_open = False
                    self.paused = False
                    self.state = self.STATE_MENU
                return

            hud_act = self.hud.handle_hud_click(pos)
            if hud_act == "open_shop":
                self.paused = True
                self._open_shop(self.STATE_PLAYING)
            elif hud_act == "toggle_pause":
                self.sound_engine.play_sfx("ui_click")
                self.paused = not self.paused

    def run(self):
        while self.running:
            dt = min(0.05, self.clock.tick(FPS) / 1000.0)
            self.elapsed_time += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                if self.state == self.STATE_MENU:
                    self._handle_menu_event(event)
                elif self.state == self.STATE_LEVEL_SELECT:
                    self._handle_level_select_event(event)
                elif self.state == self.STATE_AUDIO_SETTINGS:
                    self._handle_audio_settings_event(event)
                elif self.state == self.STATE_SHOP:
                    res = self.shop_screen.handle_event(event)
                    if res == "back":
                        self.state = self.previous_state
                elif self.state == self.STATE_PLAYING:
                    self._handle_playing_event(event)

            self.bg_renderer.update(dt, self.level_cfg)

            if self.state == self.STATE_MENU:
                self._draw_menu()
            elif self.state == self.STATE_LEVEL_SELECT:
                self._draw_level_select()
            elif self.state == self.STATE_AUDIO_SETTINGS:
                self._draw_audio_settings()
            elif self.state == self.STATE_SHOP:
                self.shop_screen.update(dt)
                self.shop_screen.draw(self.screen)
            elif self.state == self.STATE_PLAYING:
                self._update_playing(dt)
                self._draw_playing()

            pygame.display.flip()

        self.save_manager.save()
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    IcyTowerGame().run()