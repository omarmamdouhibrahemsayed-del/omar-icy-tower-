import pygame
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
# Icy Tower 50: Legends & Styles - Gameplay HUD & Pause/ESC Overlay
# ==============================================================================


class GameplayHUD:
    """Draws live HUD telemetry, momentum meter, and the ESC pause/quick-shop menu."""

    def __init__(self, font_lib):
        self.font_lib = font_lib

        # Quick-action buttons inside HUD
        self.hud_shop_btn = pygame.Rect(SCREEN_WIDTH - 276, 14, 104, 34)
        self.hud_pause_btn = pygame.Rect(SCREEN_WIDTH - 162, 14, 96, 34)

        # ESC overlay buttons
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        btn_w = 340
        btn_h = 50
        self.esc_panel = pygame.Rect(cx - 230, cy - 190, 460, 390)
        self.btn_resume = pygame.Rect(cx - btn_w // 2, cy - 95, btn_w, btn_h)
        self.btn_open_shop = pygame.Rect(cx - btn_w // 2, cy - 32, btn_w, btn_h)
        self.btn_restart = pygame.Rect(cx - btn_w // 2, cy + 31, btn_w, btn_h)
        self.btn_main_menu = pygame.Rect(cx - btn_w // 2, cy + 94, btn_w, btn_h)

        # End-of-round overlay buttons
        self.end_panel = pygame.Rect(cx - 250, cy - 185, 500, 370)
        self.btn_next_level = pygame.Rect(cx - btn_w // 2, cy + 35, btn_w, btn_h)
        self.btn_retry_level = pygame.Rect(cx - btn_w // 2, cy + 95, btn_w, btn_h)
        self.btn_end_shop = pygame.Rect(cx - 166, cy - 22, 160, 44)
        self.btn_end_menu = pygame.Rect(cx + 6, cy - 22, 160, 44)

    def handle_hud_click(self, pos):
        if self.hud_shop_btn.collidepoint(pos):
            return "open_shop"
        if self.hud_pause_btn.collidepoint(pos):
            return "toggle_pause"
        return None

    def handle_esc_click(self, pos):
        if self.btn_resume.collidepoint(pos):
            return "resume"
        if self.btn_open_shop.collidepoint(pos):
            return "open_shop"
        if self.btn_restart.collidepoint(pos):
            return "restart"
        if self.btn_main_menu.collidepoint(pos):
            return "main_menu"
        return None

    def handle_end_click(self, pos, can_advance):
        if can_advance and self.btn_next_level.collidepoint(pos):
            return "next_level"
        if self.btn_retry_level.collidepoint(pos):
            return "restart"
        if self.btn_end_shop.collidepoint(pos):
            return "open_shop"
        if self.btn_end_menu.collidepoint(pos):
            return "main_menu"
        return None

    def draw_top_hud(
        self,
        surface,
        level_cfg,
        player,
        score,
        session_coins,
        total_coins,
        paused,
        banner_text="",
    ):
        # Translucent top bar
        bar = pygame.Surface((SCREEN_WIDTH, 86), pygame.SRCALPHA)
        bar.fill((12, 18, 30, 215))
        surface.blit(bar, (0, 0))
        pygame.draw.line(surface, level_cfg.theme.wall_trim, (0, 86), (SCREEN_WIDTH, 86), 2)

        # Level & theme info (left)
        lvl_lbl = self.font_lib.render_text(
            f"المستوى {level_cfg.level_num}/50: {level_cfg.title_ar}",
            20,
            COLOR_ACCENT_CYAN,
            bold=True,
        )
        surface.blit(lvl_lbl, (72, 10))

        theme_lbl = self.font_lib.render_text(
            f"الثيم: {level_cfg.theme.name_ar}  |  الهدف: {level_cfg.objective_ar}",
            14,
            COLOR_MUTED_TEXT,
        )
        surface.blit(theme_lbl, (72, 36))

        floor_lbl = self.font_lib.render_text(
            f"الطابق: {player.current_floor} / {level_cfg.target_floor}",
            16,
            COLOR_WHITE,
            bold=True,
        )
        surface.blit(floor_lbl, (72, 58))

        # Score, Combo, Coins (center)
        score_lbl = self.font_lib.render_text(f"النقاط: {int(score)}", 20, COLOR_WHITE, bold=True)
        surface.blit(score_lbl, (455, 12))

        combo_col = COLOR_ACCENT_GOLD if player.combo >= 2 else COLOR_MUTED_TEXT
        combo_lbl = self.font_lib.render_text(
            f"Combo: {player.combo}x (أقصى: {player.max_combo}x)",
            16,
            combo_col,
            bold=player.combo >= 2,
        )
        surface.blit(combo_lbl, (455, 38))

        coins_lbl = self.font_lib.render_text(
            f"العملات: {total_coins} (+{session_coins})",
            16,
            COLOR_ACCENT_GOLD,
            bold=True,
        )
        surface.blit(coins_lbl, (455, 60))

        # Momentum bar (below top bar on left wall edge)
        mom_box = pygame.Rect(72, 94, 210, 22)
        pygame.draw.rect(surface, (16, 24, 38), mom_box, border_radius=6)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, mom_box, width=1, border_radius=6)
        fill_w = int((mom_box.width - 4) * max(0.0, min(1.0, player.momentum)))
        if fill_w > 0:
            m_col = COLOR_ACCENT_GOLD if player.momentum >= 0.45 else COLOR_ACCENT_CYAN
            pygame.draw.rect(
                surface,
                m_col,
                (mom_box.left + 2, mom_box.top + 2, fill_w, mom_box.height - 4),
                border_radius=4,
            )
        m_txt = self.font_lib.render_text(
            f"الزخم Momentum: {int(player.momentum * 100)}%",
            13,
            COLOR_WHITE,
            bold=True,
        )
        surface.blit(m_txt, m_txt.get_rect(center=mom_box.center))

        # Quick Shop & Pause buttons on top-right
        pygame.draw.rect(surface, (42, 68, 112), self.hud_shop_btn, border_radius=6)
        pygame.draw.rect(surface, COLOR_ACCENT_GOLD, self.hud_shop_btn, width=1, border_radius=6)
        s_txt = self.font_lib.render_text("المتجر", 15, COLOR_ACCENT_GOLD, bold=True)
        surface.blit(s_txt, s_txt.get_rect(center=self.hud_shop_btn.center))

        p_label = "متابعة" if paused else "إيقاف"
        pygame.draw.rect(surface, (42, 62, 92), self.hud_pause_btn, border_radius=6)
        pygame.draw.rect(surface, COLOR_ACCENT_CYAN, self.hud_pause_btn, width=1, border_radius=6)
        p_txt = self.font_lib.render_text(p_label, 15, COLOR_WHITE, bold=True)
        surface.blit(p_txt, p_txt.get_rect(center=self.hud_pause_btn.center))

        # Floating banner (combo callouts / level hints)
        if banner_text:
            b_surf = self.font_lib.render_text(banner_text, 22, COLOR_ACCENT_GOLD, bold=True)
            b_rect = b_surf.get_rect(center=(SCREEN_WIDTH // 2, 112))
            bg = pygame.Surface((b_rect.width + 24, b_rect.height + 10), pygame.SRCALPHA)
            bg.fill((12, 18, 32, 185))
            surface.blit(bg, (b_rect.left - 12, b_rect.top - 5))
            surface.blit(b_surf, b_rect)

    def draw_esc_menu(self, surface, paused):
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((6, 10, 18, 175))
        surface.blit(dim, (0, 0))

        pygame.draw.rect(surface, COLOR_DARK_PANEL, self.esc_panel, border_radius=14)
        pygame.draw.rect(surface, COLOR_ACCENT_CYAN, self.esc_panel, width=2, border_radius=14)

        status_title = "اللعبة متوقفة مؤقتاً (ESC)" if paused else "قائمة التنقل السريع (ESC)"
        title_surf = self.font_lib.render_text(status_title, 24, COLOR_ACCENT_CYAN, bold=True)
        surface.blit(title_surf, title_surf.get_rect(center=(self.esc_panel.centerx, self.esc_panel.top + 38)))

        sub_surf = self.font_lib.render_text(
            "يمكنك فتح المتجر مباشرة أو متابعة اللعب أو العودة للقائمة",
            15,
            COLOR_MUTED_TEXT,
        )
        surface.blit(sub_surf, sub_surf.get_rect(center=(self.esc_panel.centerx, self.esc_panel.top + 70)))

        buttons = [
            (self.btn_resume, "استئناف اللعب (Resume)", (34, 112, 76), COLOR_ACCENT_GREEN),
            (self.btn_open_shop, "الانتقال إلى المتجر (Shop)", (148, 104, 24), COLOR_ACCENT_GOLD),
            (self.btn_restart, "إعادة المحاولة (Restart)", (36, 68, 114), COLOR_ACCENT_CYAN),
            (self.btn_main_menu, "القائمة الرئيسية (Main Menu)", (78, 38, 48), COLOR_ACCENT_RED),
        ]
        for rect, label, fill, border in buttons:
            pygame.draw.rect(surface, fill, rect, border_radius=8)
            pygame.draw.rect(surface, border, rect, width=2, border_radius=8)
            lbl = self.font_lib.render_text(label, 18, COLOR_WHITE, bold=True)
            surface.blit(lbl, lbl.get_rect(center=rect.center))

    def draw_end_overlay(self, surface, level_cfg, won, score, max_combo, coins_earned, reason_ar):
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((8, 12, 22, 185))
        surface.blit(dim, (0, 0))

        border_col = COLOR_ACCENT_GREEN if won else COLOR_ACCENT_RED
        pygame.draw.rect(surface, COLOR_DARK_PANEL, self.end_panel, border_radius=14)
        pygame.draw.rect(surface, border_col, self.end_panel, width=3, border_radius=14)

        head_txt = (
            f"أحسنت! تم اجتياز المستوى {level_cfg.level_num}"
            if won
            else f"انتهت المحاولة — المستوى {level_cfg.level_num}"
        )
        head_surf = self.font_lib.render_text(head_txt, 24, border_col, bold=True)
        surface.blit(head_surf, head_surf.get_rect(center=(self.end_panel.centerx, self.end_panel.top + 36)))

        reason_surf = self.font_lib.render_text(reason_ar, 16, COLOR_WHITE)
        surface.blit(reason_surf, reason_surf.get_rect(center=(self.end_panel.centerx, self.end_panel.top + 70)))

        stats_lines = [
            f"النقاط النهائية: {int(score)}  (المطلوب: {level_cfg.min_score_req})",
            f"أقصى Combo: {max_combo}x  (المطلوب: {level_cfg.min_combo_req}x)",
            f"العملات المكتسبة: +{coins_earned}",
        ]
        for i, line in enumerate(stats_lines):
            s_surf = self.font_lib.render_text(line, 17, COLOR_ACCENT_GOLD if i == 2 else COLOR_WHITE, bold=(i == 2))
            surface.blit(s_surf, s_surf.get_rect(center=(self.end_panel.centerx, self.end_panel.top + 104 + i * 24)))

        can_advance = won and level_cfg.level_num < 50

        pygame.draw.rect(surface, (148, 104, 24), self.btn_end_shop, border_radius=8)
        pygame.draw.rect(surface, COLOR_ACCENT_GOLD, self.btn_end_shop, width=2, border_radius=8)
        sh_lbl = self.font_lib.render_text("المتجر", 17, COLOR_WHITE, bold=True)
        surface.blit(sh_lbl, sh_lbl.get_rect(center=self.btn_end_shop.center))

        pygame.draw.rect(surface, (36, 68, 114), self.btn_end_menu, border_radius=8)
        pygame.draw.rect(surface, COLOR_ACCENT_CYAN, self.btn_end_menu, width=2, border_radius=8)
        mn_lbl = self.font_lib.render_text("القائمة الرئيسية", 17, COLOR_WHITE, bold=True)
        surface.blit(mn_lbl, mn_lbl.get_rect(center=self.btn_end_menu.center))

        if can_advance:
            pygame.draw.rect(surface, (34, 118, 78), self.btn_next_level, border_radius=8)
            pygame.draw.rect(surface, COLOR_ACCENT_GREEN, self.btn_next_level, width=2, border_radius=8)
            nx_lbl = self.font_lib.render_text("المستوى التالي →", 18, COLOR_WHITE, bold=True)
            surface.blit(nx_lbl, nx_lbl.get_rect(center=self.btn_next_level.center))

        pygame.draw.rect(surface, (44, 72, 116), self.btn_retry_level, border_radius=8)
        pygame.draw.rect(surface, COLOR_ACCENT_CYAN, self.btn_retry_level, width=2, border_radius=8)
        rt_lbl = self.font_lib.render_text("إعادة المستوى", 18, COLOR_WHITE, bold=True)
        surface.blit(rt_lbl, rt_lbl.get_rect(center=self.btn_retry_level.center))