import math
import random
import pygame
from settings import FLOOR_SPACING_BASE, FLOORS_PER_LEVEL, SCREEN_HEIGHT, SCREEN_WIDTH

# ==============================================================================
# Icy Tower 50: Legends & Styles - 50 Distinct Levels & Theme Renderer
# ==============================================================================


class ThemeSpec:
    """Visual theme specification for backgrounds, tower walls, and platform palettes."""

    def __init__(
        self,
        key,
        name_ar,
        name_en,
        sky_top,
        sky_bottom,
        wall_base,
        wall_trim,
        plat_normal,
        plat_border,
        plat_ice,
        plat_fragile,
        plat_moving,
        plat_spring,
        accent,
        ambient_kind,
    ):
        self.key = key
        self.name_ar = name_ar
        self.name_en = name_en
        self.sky_top = sky_top
        self.sky_bottom = sky_bottom
        self.wall_base = wall_base
        self.wall_trim = wall_trim
        self.plat_normal = plat_normal
        self.plat_border = plat_border
        self.plat_ice = plat_ice
        self.plat_fragile = plat_fragile
        self.plat_moving = plat_moving
        self.plat_spring = plat_spring
        self.accent = accent
        self.ambient_kind = ambient_kind


THEMES = {
    "ice": ThemeSpec(
        key="ice",
        name_ar="قمة الجليد الكلاسيكية",
        name_en="Classic Glacier",
        sky_top=(18, 52, 92),
        sky_bottom=(58, 134, 198),
        wall_base=(28, 68, 114),
        wall_trim=(110, 204, 255),
        plat_normal=(188, 232, 255),
        plat_border=(92, 168, 224),
        plat_ice=(226, 248, 255),
        plat_fragile=(214, 154, 128),
        plat_moving=(115, 225, 215),
        plat_spring=(255, 204, 72),
        accent=(125, 225, 255),
        ambient_kind="snow",
    ),
    "polar_night": ThemeSpec(
        key="polar_night",
        name_ar="الليل القطبي العميق",
        name_en="Deep Polar Night",
        sky_top=(8, 14, 34),
        sky_bottom=(24, 42, 82),
        wall_base=(16, 26, 54),
        wall_trim=(84, 126, 212),
        plat_normal=(122, 162, 226),
        plat_border=(58, 92, 156),
        plat_ice=(178, 218, 255),
        plat_fragile=(196, 122, 118),
        plat_moving=(92, 196, 228),
        plat_spring=(255, 184, 68),
        accent=(110, 178, 255),
        ambient_kind="stars",
    ),
    "crystal_cave": ThemeSpec(
        key="crystal_cave",
        name_ar="كهوف البلورات المتجمدة",
        name_en="Frozen Crystal Cavern",
        sky_top=(24, 16, 54),
        sky_bottom=(66, 36, 112),
        wall_base=(38, 22, 72),
        wall_trim=(178, 116, 255),
        plat_normal=(184, 144, 248),
        plat_border=(118, 76, 196),
        plat_ice=(158, 242, 255),
        plat_fragile=(228, 134, 168),
        plat_moving=(118, 235, 196),
        plat_spring=(255, 212, 84),
        accent=(196, 138, 255),
        ambient_kind="crystals",
    ),
    "aurora": ThemeSpec(
        key="aurora",
        name_ar="الشفق القطبي السماوي",
        name_en="Sky Aurora",
        sky_top=(10, 26, 48),
        sky_bottom=(22, 88, 108),
        wall_base=(18, 48, 68),
        wall_trim=(78, 245, 186),
        plat_normal=(146, 232, 212),
        plat_border=(64, 162, 152),
        plat_ice=(198, 255, 242),
        plat_fragile=(226, 162, 124),
        plat_moving=(112, 245, 196),
        plat_spring=(255, 216, 76),
        accent=(84, 248, 192),
        ambient_kind="aurora",
    ),
    "blizzard": ThemeSpec(
        key="blizzard",
        name_ar="عاصفة الثلج العاتية",
        name_en="Howling Blizzard",
        sky_top=(46, 68, 92),
        sky_bottom=(104, 136, 166),
        wall_base=(58, 82, 108),
        wall_trim=(208, 232, 252),
        plat_normal=(212, 228, 242),
        plat_border=(124, 152, 178),
        plat_ice=(240, 250, 255),
        plat_fragile=(218, 152, 134),
        plat_moving=(136, 206, 236),
        plat_spring=(255, 196, 68),
        accent=(225, 242, 255),
        ambient_kind="storm",
    ),
    "ancient_tower": ThemeSpec(
        key="ancient_tower",
        name_ar="الأبراج الجليدية القديمة",
        name_en="Ancient Frost Spire",
        sky_top=(32, 28, 24),
        sky_bottom=(78, 64, 52),
        wall_base=(48, 40, 34),
        wall_trim=(218, 174, 96),
        plat_normal=(198, 176, 136),
        plat_border=(128, 104, 68),
        plat_ice=(176, 228, 244),
        plat_fragile=(206, 118, 92),
        plat_moving=(142, 214, 186),
        plat_spring=(255, 202, 64),
        accent=(232, 186, 98),
        ambient_kind="embers",
    ),
    "cold_space": ThemeSpec(
        key="cold_space",
        name_ar="الفضاء المتجمد والنجوم",
        name_en="Frozen Cosmos",
        sky_top=(5, 8, 20),
        sky_bottom=(18, 24, 54),
        wall_base=(14, 20, 42),
        wall_trim=(122, 198, 255),
        plat_normal=(138, 184, 246),
        plat_border=(72, 116, 186),
        plat_ice=(188, 236, 255),
        plat_fragile=(224, 122, 156),
        plat_moving=(112, 236, 224),
        plat_spring=(255, 214, 72),
        accent=(142, 214, 255),
        ambient_kind="stars",
    ),
    "volcanic_frost": ThemeSpec(
        key="volcanic_frost",
        name_ar="فوهة الصقيع البركانية",
        name_en="Frostfire Crater",
        sky_top=(42, 14, 24),
        sky_bottom=(112, 34, 42),
        wall_base=(56, 22, 28),
        wall_trim=(255, 132, 72),
        plat_normal=(214, 148, 128),
        plat_border=(148, 76, 64),
        plat_ice=(168, 236, 255),
        plat_fragile=(242, 108, 86),
        plat_moving=(248, 184, 78),
        plat_spring=(255, 224, 84),
        accent=(255, 144, 78),
        ambient_kind="embers",
    ),
}


class LevelConfig:
    """Complete definition of a single level (1..50)."""

    def __init__(
        self,
        level_num,
        title_ar,
        title_en,
        theme_key,
        target_floor,
        min_combo_req,
        min_score_req,
        camera_speed,
        floor_spacing,
        plat_width_min,
        plat_width_max,
        moving_ratio,
        fragile_ratio,
        ice_ratio,
        spring_ratio,
        coin_density,
        objective_ar,
    ):
        self.level_num = int(level_num)
        self.title_ar = title_ar
        self.title_en = title_en
        self.theme_key = theme_key
        self.theme = THEMES[theme_key]
        self.target_floor = int(target_floor)
        self.min_combo_req = int(min_combo_req)
        self.min_score_req = int(min_score_req)
        self.camera_speed = float(camera_speed)
        self.floor_spacing = int(floor_spacing)
        self.plat_width_min = int(plat_width_min)
        self.plat_width_max = int(plat_width_max)
        self.moving_ratio = float(moving_ratio)
        self.fragile_ratio = float(fragile_ratio)
        self.ice_ratio = float(ice_ratio)
        self.spring_ratio = float(spring_ratio)
        self.coin_density = float(coin_density)
        self.objective_ar = objective_ar


def _build_50_levels():
    theme_cycle = [
        "ice",
        "polar_night",
        "crystal_cave",
        "aurora",
        "blizzard",
        "ancient_tower",
        "cold_space",
        "volcanic_frost",
    ]

    custom_names_ar = [
        "بداية الجليد", "نسيم الصقيع", "درجات البرد", "ممر الثلج", "ندف الفجر",
        "بوابة القطب", "سماء الشفق", "منحدرات الزجاج", "مرفأ الجليد", "عاصفة خفيفة",
        "قبة الكريستال", "ظلال الليل", "برج الحرس", "مدار النجوم", "نار وجليد",
        "متاهة الصقيع", "أصداء الكهف", "هبوب الشمال", "قوس الشفق", "أحجار الأقدمين",
        "تصدع الجليد", "سقوط النيازك", "صعود الرياح", "منصات الوميض", "هوة البرد",
        "أبراج السحاب", "نبض البلورات", "ليل بلا قمر", "زوبعة الثلج", "قاعة الملوك",
        "مجرة الصقيع", "حمم متجمدة", "قفزة العاصفة", "أعمدة النور", "وادي الكريستال",
        "ساعة الصفر", "جسر الأرواح", "طوفان الثلج", "عرش الشمال", "سديم بارد",
        "بركان الصقيع", "سباق الزمن", "قمة الأسرار", "عاصفة القمة", "مملكة الجليد",
        "أفق المذنب", "لظى الجليد", "أسطورة البرج", "تحدي العمالقة", "قمة الأساطير 50",
    ]

    levels = []
    for idx in range(1, 51):
        t_idx = (idx - 1) % len(theme_cycle)
        theme_key = theme_cycle[t_idx]
        theme = THEMES[theme_key]
        title_ar = custom_names_ar[idx - 1]
        title_en = f"Stage {idx:02d} - {theme.name_en}"

        progress = (idx - 1) / 49.0  # 0.0 -> 1.0
        target_floor = FLOORS_PER_LEVEL + ((idx - 1) // 5) * 3
        camera_speed = 36.0 + progress * 92.0 + (4.0 if idx % 10 == 0 else 0.0)
        floor_spacing = int(FLOOR_SPACING_BASE + (idx % 6) * 2 + progress * 12)

        plat_w_max = max(135, int(235 - progress * 75))
        plat_w_min = max(86, int(145 - progress * 52))

        moving_ratio = min(0.34, 0.05 + progress * 0.24 + (0.04 if idx % 3 == 0 else 0.0))
        fragile_ratio = min(0.28, 0.03 + progress * 0.20 + (0.04 if idx % 4 == 0 else 0.0))
        ice_ratio = min(0.32, 0.14 + (0.10 if theme_key in ("ice", "blizzard") else 0.02))
        spring_ratio = max(0.06, 0.14 - progress * 0.05 + (0.03 if idx % 5 == 0 else 0.0))

        # Distinct objective rules across levels
        mod_rule = idx % 5
        if idx == 50:
            min_combo_req = 5
            min_score_req = 18000
            objective_ar = f"الوصول للطابق {target_floor} + Combo 5+ + {min_score_req} نقطة"
        elif mod_rule == 1:
            min_combo_req = 0
            min_score_req = int(900 + idx * 240)
            objective_ar = f"بلوغ الطابق {target_floor} وجمع {min_score_req} نقطة على الأقل"
        elif mod_rule == 2:
            min_combo_req = 2 + (idx // 12)
            min_score_req = int(700 + idx * 180)
            objective_ar = f"الوصول للطابق {target_floor} وتحقيق Combo {min_combo_req}x"
        elif mod_rule == 3:
            min_combo_req = 0
            min_score_req = int(1100 + idx * 260)
            objective_ar = f"تحدي الصعود للطابق {target_floor} بسرعة وثبات"
        elif mod_rule == 4:
            min_combo_req = 3 + (idx // 15)
            min_score_req = int(1200 + idx * 250)
            objective_ar = f"الوصول للطابق {target_floor} + Combo {min_combo_req}x"
        else:
            min_combo_req = 4 + (idx // 16)
            min_score_req = int(1500 + idx * 280)
            objective_ar = f"تحدي النخبة: الطابق {target_floor} + Combo {min_combo_req}x"

        coin_density = max(0.28, 0.52 - progress * 0.15)

        levels.append(
            LevelConfig(
                level_num=idx,
                title_ar=title_ar,
                title_en=title_en,
                theme_key=theme_key,
                target_floor=target_floor,
                min_combo_req=min_combo_req,
                min_score_req=min_score_req,
                camera_speed=camera_speed,
                floor_spacing=floor_spacing,
                plat_width_min=plat_w_min,
                plat_width_max=plat_w_max,
                moving_ratio=moving_ratio,
                fragile_ratio=fragile_ratio,
                ice_ratio=ice_ratio,
                spring_ratio=spring_ratio,
                coin_density=coin_density,
                objective_ar=objective_ar,
            )
        )

    return levels


LEVELS_LIST = _build_50_levels()
LEVELS_BY_NUM = {lvl.level_num: lvl for lvl in LEVELS_LIST}


def get_level(level_num):
    clamped = max(1, min(50, int(level_num)))
    return LEVELS_BY_NUM[clamped]


class LevelBackgroundRenderer:
    """Draws rich themed backgrounds, side walls, and animated ambient particles."""

    def __init__(self):
        self._particles = []
        rng = random.Random(5050)
        for _ in range(55):
            self._particles.append(
                {
                    "x": rng.uniform(0, SCREEN_WIDTH),
                    "y": rng.uniform(0, SCREEN_HEIGHT),
                    "speed_y": rng.uniform(18, 75),
                    "speed_x": rng.uniform(-22, 22),
                    "size": rng.randint(2, 5),
                    "phase": rng.uniform(0, math.pi * 2),
                }
            )

    def update(self, dt, level_cfg):
        wind = -65.0 if level_cfg.theme.ambient_kind == "storm" else 0.0
        for p in self._particles:
            p["phase"] += dt * 2.4
            p["y"] += p["speed_y"] * dt
            p["x"] += (p["speed_x"] + wind + math.sin(p["phase"]) * 12.0) * dt

            if p["y"] > SCREEN_HEIGHT + 10:
                p["y"] = -10
                p["x"] = random.uniform(0, SCREEN_WIDTH)
            if p["x"] < 0:
                p["x"] += SCREEN_WIDTH
            elif p["x"] > SCREEN_WIDTH:
                p["x"] -= SCREEN_WIDTH

    def draw(self, surface, level_cfg, camera_y, elapsed_time):
        theme = level_cfg.theme

        # Vertical gradient sky
        top = theme.sky_top
        bot = theme.sky_bottom
        steps = 24
        band_h = (SCREEN_HEIGHT + steps - 1) // steps
        for i in range(steps):
            t = i / max(1, steps - 1)
            col = (
                int(top[0] + (bot[0] - top[0]) * t),
                int(top[1] + (bot[1] - top[1]) * t),
                int(top[2] + (bot[2] - top[2]) * t),
            )
            pygame.draw.rect(surface, col, (0, i * band_h, SCREEN_WIDTH, band_h + 1))

        # Theme-specific backdrop details
        if theme.ambient_kind == "aurora":
            for band in range(3):
                pts = []
                base_y = 140 + band * 125
                for x in range(0, SCREEN_WIDTH + 40, 40):
                    y = base_y + math.sin(x * 0.01 + elapsed_time * (1.2 + band * 0.3) + band) * 38
                    pts.append((x, y))
                if len(pts) >= 2:
                    pygame.draw.lines(surface, theme.accent, False, pts, 3)

        elif theme.ambient_kind == "crystals":
            for i in range(6):
                cx = 160 + i * 155
                cy = 180 + ((i * 97) % 360)
                pts = [(cx, cy - 36), (cx + 18, cy), (cx, cy + 36), (cx - 18, cy)]
                pygame.draw.polygon(surface, theme.wall_trim, pts, width=2)

        # Tower side columns with parallax scrolling
        wall_w = 56
        tile_h = 64
        offset_y = int((camera_y * 0.5) % tile_h)

        pygame.draw.rect(surface, theme.wall_base, (0, 0, wall_w, SCREEN_HEIGHT))
        pygame.draw.rect(surface, theme.wall_base, (SCREEN_WIDTH - wall_w, 0, wall_w, SCREEN_HEIGHT))

        for y in range(-tile_h + offset_y, SCREEN_HEIGHT + tile_h, tile_h):
            pygame.draw.rect(surface, theme.wall_trim, (6, y + 6, wall_w - 12, 10), border_radius=3)
            pygame.draw.rect(
                surface,
                theme.wall_trim,
                (SCREEN_WIDTH - wall_w + 6, y + 6, wall_w - 12, 10),
                border_radius=3,
            )

        pygame.draw.line(surface, theme.wall_trim, (wall_w, 0), (wall_w, SCREEN_HEIGHT), 3)
        pygame.draw.line(
            surface,
            theme.wall_trim,
            (SCREEN_WIDTH - wall_w, 0),
            (SCREEN_WIDTH - wall_w, SCREEN_HEIGHT),
            3,
        )

        # Ambient particles
        for p in self._particles:
            px = int(p["x"])
            py = int(p["y"])
            sz = p["size"]
            if theme.ambient_kind == "stars":
                twinkle = 0.5 + 0.5 * math.sin(p["phase"] * 2.0)
                r = max(1, int(sz * twinkle))
                pygame.draw.circle(surface, theme.accent, (px, py), r)
            elif theme.ambient_kind == "embers":
                pygame.draw.circle(surface, theme.accent, (px, py), max(2, sz // 2))
            else:
                pygame.draw.circle(surface, (242, 248, 255), (px, py), max(2, sz // 2))