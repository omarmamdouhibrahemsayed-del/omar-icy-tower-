import math
import pygame
from characters import CHARACTERS_LIST, render_character_sprite
from settings import (
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_GOLD,
    COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED,
    COLOR_BLACK,
    COLOR_DARK_PANEL,
    COLOR_MUTED_TEXT,
    COLOR_PANEL_BORDER,
    COLOR_WHITE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)

# ==============================================================================
# Icy Tower 50: Legends & Styles - 14-Character Pixel Art Shop UI
# ==============================================================================


class CharacterShopScreen:
    """Interactive UI for browsing, unlocking, and selecting all 14 Pixel Art characters."""

    def __init__(self, save_manager, sound_engine, font_lib):
        self.save_manager = save_manager
        self.sound_engine = sound_engine
        self.font_lib = font_lib

        self.selected_index = 0
        self.page = 0
        self.items_per_page = 7  # 7 per page -> 2 full pages for 14 characters
        self.status_message = ""
        self.status_timer = 0.0
        self.anim_clock = 0.0

        # Sync index with currently selected character
        sel_id = self.save_manager.selected_character
        for idx, ch in enumerate(CHARACTERS_LIST):
            if ch.char_id == sel_id:
                self.selected_index = idx
                self.page = idx // self.items_per_page
                break

        self.back_rect = pygame.Rect(32, 24, 175, 46)
        self.prev_page_rect = pygame.Rect(40, SCREEN_HEIGHT - 84, 150, 46)
        self.next_page_rect = pygame.Rect(206, SCREEN_HEIGHT - 84, 150, 46)
        self.action_btn_rect = pygame.Rect(SCREEN_WIDTH - 340, SCREEN_HEIGHT - 92, 295, 54)
        self.card_rects = []

    def set_status(self, msg, duration=2.2):
        self.status_message = msg
        self.status_timer = duration

    def update(self, dt):
        self.anim_clock += dt
        if self.status_timer > 0.0:
            self.status_timer = max(0.0, self.status_timer - dt)
            if self.status_timer == 0.0:
                self.status_message = ""

    def handle_event(self, event):
        """
        Returns:
          None -> stay in shop
          'back' -> return to previous screen (game or main menu)
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.sound_engine.play_sfx("ui_click")
                return "back"
            elif event.key == pygame.K_DOWN:
                self.sound_engine.play_sfx("ui_click")
                self.selected_index = (self.selected_index + 1) % len(CHARACTERS_LIST)
                self.page = self.selected_index // self.items_per_page
            elif event.key == pygame.K_UP:
                self.sound_engine.play_sfx("ui_click")
                self.selected_index = (self.selected_index - 1) % len(CHARACTERS_LIST)
                self.page = self.selected_index // self.items_per_page
            elif event.key == pygame.K_LEFT:
                self.sound_engine.play_sfx("ui_click")
                total_pages = (len(CHARACTERS_LIST) + self.items_per_page - 1) // self.items_per_page
                self.page = (self.page - 1) % total_pages
                self.selected_index = self.page * self.items_per_page
            elif event.key == pygame.K_RIGHT:
                self.sound_engine.play_sfx("ui_click")
                total_pages = (len(CHARACTERS_LIST) + self.items_per_page - 1) // self.items_per_page
                self.page = (self.page + 1) % total_pages
                self.selected_index = self.page * self.items_per_page
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate_selected_character()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.back_rect.collidepoint(pos):
                self.sound_engine.play_sfx("ui_click")
                return "back"

            if self.prev_page_rect.collidepoint(pos):
                self.sound_engine.play_sfx("ui_click")
                total_pages = (len(CHARACTERS_LIST) + self.items_per_page - 1) // self.items_per_page
                self.page = (self.page - 1) % total_pages
                self.selected_index = self.page * self.items_per_page
                return None

            if self.next_page_rect.collidepoint(pos):
                self.sound_engine.play_sfx("ui_click")
                total_pages = (len(CHARACTERS_LIST) + self.items_per_page - 1) // self.items_per_page
                self.page = (self.page + 1) % total_pages
                self.selected_index = self.page * self.items_per_page
                return None

            for idx, rect in self.card_rects:
                if rect.collidepoint(pos):
                    self.sound_engine.play_sfx("ui_click")
                    self.selected_index = idx
                    return None

            if self.action_btn_rect.collidepoint(pos):
                self._activate_selected_character()
                return None

        return None

    def _activate_selected_character(self):
        spec = CHARACTERS_LIST[self.selected_index]
        owned = spec.char_id in self.save_manager.owned_characters
        active = self.save_manager.selected_character == spec.char_id

        if active:
            self.sound_engine.play_sfx("ui_click")
            self.set_status(f"الشخصية المختارة حالياً: {spec.name_ar}")
            return

        if owned:
            self.save_manager.selected_character = spec.char_id
            self.save_manager.save()
            self.sound_engine.play_sfx("buy")
            self.set_status(f"تم اختيار الشخصية: {spec.name_ar}")
            return

        if self.save_manager.unlock_character(spec.char_id, spec.price):
            self.sound_engine.play_sfx("buy")
            self.set_status(f"مبروك! تم شراء وتفعيل {spec.name_ar}")
        else:
            self.sound_engine.play_sfx("ui_click")
            needed = max(0, spec.price - self.save_manager.coins)
            self.set_status(f"عملاتك غير كافية — ينقصك {needed} عملة")

    def draw(self, surface):
        surface.fill((12, 20, 36))

        # Top header bar
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 92)
        pygame.draw.rect(surface, (18, 30, 52), header_rect)
        pygame.draw.line(surface, COLOR_PANEL_BORDER, (0, 92), (SCREEN_WIDTH, 92), 2)

        # Back button
        pygame.draw.rect(surface, (34, 52, 84), self.back_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_ACCENT_CYAN, self.back_rect, width=2, border_radius=8)
        back_lbl = self.font_lib.render_text("← رجوع (ESC)", 18, COLOR_WHITE, bold=True)
        surface.blit(back_lbl, back_lbl.get_rect(center=self.back_rect.center))

        # Title & owned count
        title_txt = self.font_lib.render_text(
            "متجر الشخصيات • 14 شخصية Pixel Art", 28, COLOR_ACCENT_CYAN, bold=True
        )
        surface.blit(title_txt, (240, 18))

        sub_txt = self.font_lib.render_text(
            f"المملوكة: {len(self.save_manager.owned_characters)} / {len(CHARACTERS_LIST)}",
            16,
            COLOR_MUTED_TEXT,
        )
        surface.blit(sub_txt, (240, 54))

        # Coins badge on top-right
        coins_box = pygame.Rect(SCREEN_WIDTH - 250, 22, 215, 48)
        pygame.draw.rect(surface, (32, 42, 62), coins_box, border_radius=10)
        pygame.draw.rect(surface, COLOR_ACCENT_GOLD, coins_box, width=2, border_radius=10)
        pygame.draw.circle(surface, COLOR_ACCENT_GOLD, (coins_box.left + 26, coins_box.centery), 11)
        coins_lbl = self.font_lib.render_text(
            f"العملات: {self.save_manager.coins}", 20, COLOR_ACCENT_GOLD, bold=True
        )
        surface.blit(coins_lbl, (coins_box.left + 46, coins_box.centery - coins_lbl.get_height() // 2))

        # Left column: character list (7 per page)
        self.card_rects = []
        start_idx = self.page * self.items_per_page
        end_idx = min(len(CHARACTERS_LIST), start_idx + self.items_per_page)

        list_x = 32
        list_y = 112
        card_w = 540
        card_h = 74
        gap = 8

        for slot, idx in enumerate(range(start_idx, end_idx)):
            ch = CHARACTERS_LIST[idx]
            rect = pygame.Rect(list_x, list_y + slot * (card_h + gap), card_w, card_h)
            self.card_rects.append((idx, rect))

            is_sel = idx == self.selected_index
            is_owned = ch.char_id in self.save_manager.owned_characters
            is_active = self.save_manager.selected_character == ch.char_id

            bg_col = (34, 58, 96) if is_sel else (22, 33, 54)
            border_col = ch.accent_color if is_sel else COLOR_PANEL_BORDER
            pygame.draw.rect(surface, bg_col, rect, border_radius=10)
            pygame.draw.rect(surface, border_col, rect, width=3 if is_sel else 1, border_radius=10)

            # Mini pixel sprite thumbnail
            thumb = render_character_sprite(
                ch,
                width=44,
                height=58,
                facing_right=True,
                anim_phase=self.anim_clock * 0.4 if is_sel else 0.0,
                airborne=False,
                momentum_ratio=0.4 if is_sel else 0.0,
            )
            surface.blit(thumb, (rect.left + 12, rect.centery - thumb.get_height() // 2))

            name_lbl = self.font_lib.render_text(f"{idx + 1}. {ch.name_ar}", 19, COLOR_WHITE, bold=True)
            surface.blit(name_lbl, (rect.left + 68, rect.top + 11))

            cat_lbl = self.font_lib.render_text(ch.category_ar, 14, ch.accent_color)
            surface.blit(cat_lbl, (rect.left + 68, rect.top + 40))

            # Right status/price badge inside card
            if is_active:
                badge_txt = "مفعّلة"
                badge_col = COLOR_ACCENT_GREEN
            elif is_owned:
                badge_txt = "مملوكة"
                badge_col = COLOR_ACCENT_CYAN
            else:
                badge_txt = f"{ch.price} عملة"
                badge_col = COLOR_ACCENT_GOLD

            b_surf = self.font_lib.render_text(badge_txt, 16, badge_col, bold=True)
            surface.blit(b_surf, (rect.right - b_surf.get_width() - 16, rect.centery - b_surf.get_height() // 2))

        # Pagination buttons
        total_pages = (len(CHARACTERS_LIST) + self.items_per_page - 1) // self.items_per_page
        pygame.draw.rect(surface, (28, 44, 72), self.prev_page_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.prev_page_rect, width=2, border_radius=8)
        prev_lbl = self.font_lib.render_text("← صفحة سابقة", 16, COLOR_WHITE, bold=True)
        surface.blit(prev_lbl, prev_lbl.get_rect(center=self.prev_page_rect.center))

        pygame.draw.rect(surface, (28, 44, 72), self.next_page_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.next_page_rect, width=2, border_radius=8)
        next_lbl = self.font_lib.render_text("صفحة تالية →", 16, COLOR_WHITE, bold=True)
        surface.blit(next_lbl, next_lbl.get_rect(center=self.next_page_rect.center))

        page_lbl = self.font_lib.render_text(
            f"صفحة {self.page + 1} / {total_pages}", 16, COLOR_MUTED_TEXT, bold=True
        )
        surface.blit(page_lbl, (374, self.prev_page_rect.centery - page_lbl.get_height() // 2))

        # Right column: detailed preview panel for selected character
        sel_spec = CHARACTERS_LIST[self.selected_index]
        detail_rect = pygame.Rect(596, 112, SCREEN_WIDTH - 628, SCREEN_HEIGHT - 134)
        pygame.draw.rect(surface, COLOR_DARK_PANEL, detail_rect, border_radius=14)
        pygame.draw.rect(surface, sel_spec.accent_color, detail_rect, width=2, border_radius=14)

        # Showcase pedestal & large animated pixel sprite
        stage_rect = pygame.Rect(detail_rect.left + 28, detail_rect.top + 24, detail_rect.width - 56, 210)
        pygame.draw.rect(surface, (14, 22, 38), stage_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, stage_rect, width=1, border_radius=12)

        bob_y = math.sin(self.anim_clock * 4.5) * 6.0
        large_sprite = render_character_sprite(
            sel_spec,
            width=102,
            height=144,
            facing_right=True,
            anim_phase=self.anim_clock * 0.75,
            airborne=False,
            momentum_ratio=0.65,
        )
        sprite_pos = large_sprite.get_rect(center=(stage_rect.centerx, stage_rect.centery - 6 + int(bob_y)))
        surface.blit(large_sprite, sprite_pos)

        # Pedestal ring under sprite
        pygame.draw.ellipse(
            surface,
            sel_spec.accent_color,
            (stage_rect.centerx - 58, stage_rect.bottom - 34, 116, 18),
            width=3,
        )

        # Character title & English subtitle
        d_name = self.font_lib.render_text(sel_spec.name_ar, 26, COLOR_WHITE, bold=True)
        surface.blit(d_name, (detail_rect.left + 28, stage_rect.bottom + 16))

        d_sub = self.font_lib.render_text(
            f"{sel_spec.name_en}  |  {sel_spec.category_ar}", 16, sel_spec.accent_color, bold=True
        )
        surface.blit(d_sub, (detail_rect.left + 28, stage_rect.bottom + 50))

        # Ability box
        ab_rect = pygame.Rect(detail_rect.left + 28, stage_rect.bottom + 84, detail_rect.width - 56, 78)
        pygame.draw.rect(surface, (24, 36, 58), ab_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, ab_rect, width=1, border_radius=10)

        ab_head = self.font_lib.render_text("القدرة الخاصة:", 16, COLOR_ACCENT_CYAN, bold=True)
        surface.blit(ab_head, (ab_rect.left + 14, ab_rect.top + 10))

        ab_desc = self.font_lib.render_text(sel_spec.ability_ar, 17, COLOR_WHITE)
        surface.blit(ab_desc, (ab_rect.left + 14, ab_rect.top + 38))

        # Stat bars (Jump, Momentum, Score, Coins)
        stats = [
            ("القفز (Jump)", min(1.0, (sel_spec.jump_mult - 0.85) / 0.45), COLOR_ACCENT_CYAN),
            ("الزخم (Momentum)", min(1.0, (sel_spec.momentum_mult - 0.85) / 0.45), COLOR_ACCENT_GOLD),
            ("النقاط (Score)", min(1.0, (sel_spec.score_mult - 0.85) / 0.50), COLOR_ACCENT_GREEN),
            ("العملات (Coins)", min(1.0, (sel_spec.coin_mult - 0.85) / 0.55), (255, 178, 72)),
        ]
        bar_y_start = ab_rect.bottom + 18
        for idx, (s_label, s_val, s_col) in enumerate(stats):
            by = bar_y_start + idx * 32
            lbl = self.font_lib.render_text(s_label, 15, COLOR_WHITE, bold=True)
            surface.blit(lbl, (detail_rect.left + 30, by))

            track = pygame.Rect(detail_rect.left + 205, by + 3, detail_rect.width - 245, 14)
            pygame.draw.rect(surface, (14, 20, 34), track, border_radius=6)
            fill_w = max(8, int(track.width * max(0.08, min(1.0, s_val))))
            pygame.draw.rect(surface, s_col, (track.left, track.top, fill_w, track.height), border_radius=6)

        # Primary action button (Buy / Select / Active)
        is_owned = sel_spec.char_id in self.save_manager.owned_characters
        is_active = self.save_manager.selected_character == sel_spec.char_id
        can_afford = self.save_manager.coins >= sel_spec.price

        if is_active:
            btn_col = (36, 118, 78)
            btn_border = COLOR_ACCENT_GREEN
            btn_text = "✓ مفعّلة الآن"
        elif is_owned:
            btn_col = (34, 88, 142)
            btn_border = COLOR_ACCENT_CYAN
            btn_text = "اختيار الشخصية"
        elif can_afford:
            btn_col = (168, 118, 22)
            btn_border = COLOR_ACCENT_GOLD
            btn_text = f"شراء مقابل {sel_spec.price} عملة"
        else:
            btn_col = (78, 34, 42)
            btn_border = COLOR_ACCENT_RED
            btn_text = f"مطلوب {sel_spec.price} عملة"

        pygame.draw.rect(surface, btn_col, self.action_btn_rect, border_radius=10)
        pygame.draw.rect(surface, btn_border, self.action_btn_rect, width=2, border_radius=10)
        action_lbl = self.font_lib.render_text(btn_text, 19, COLOR_WHITE, bold=True)
        surface.blit(action_lbl, action_lbl.get_rect(center=self.action_btn_rect.center))

        # Status feedback message
        if self.status_message:
            st_surf = self.font_lib.render_text(self.status_message, 16, COLOR_ACCENT_GOLD, bold=True)
            surface.blit(st_surf, (detail_rect.left + 28, self.action_btn_rect.top - 28))