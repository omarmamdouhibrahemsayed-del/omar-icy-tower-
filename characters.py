import math
import pygame

# ==============================================================================
# Icy Tower 50: Legends & Styles - 14 Pixel Art Characters & Abilities
# ==============================================================================


class CharacterSpec:
    """Defines a playable Pixel Art character, its stats, visual aura, and pixel grid."""

    def __init__(
        self,
        char_id,
        name_ar,
        name_en,
        category_ar,
        price,
        ability_ar,
        ability_en,
        accent_color,
        trail_color,
        jump_mult=1.0,
        momentum_mult=1.0,
        score_mult=1.0,
        coin_mult=1.0,
        slip_resist=0.0,
        pixel_grid=None,
    ):
        self.char_id = char_id
        self.name_ar = name_ar
        self.name_en = name_en
        self.category_ar = category_ar
        self.price = int(price)
        self.ability_ar = ability_ar
        self.ability_en = ability_en
        self.accent_color = accent_color
        self.trail_color = trail_color
        self.jump_mult = float(jump_mult)
        self.momentum_mult = float(momentum_mult)
        self.score_mult = float(score_mult)
        self.coin_mult = float(coin_mult)
        self.slip_resist = float(slip_resist)
        self.pixel_grid = pixel_grid or []


# Legend for 16x16 character grids:
# '.' = transparent
# 'H' = Hair / Hat primary
# 'h' = Hair / Hat highlight or brim
# 'S' = Skin tone
# 's' = Skin shadow / cheek
# 'E' = Eye / visor / glasses
# 'M' = Mouth / scarf / details
# 'C' = Outfit primary
# 'c' = Outfit secondary / stripe
# 'P' = Pants / lower suit
# 'B' = Boots / shoes / tail tip
# 'A' = Special accent (headphones, emblem, ears, etc.)


def _build_all_characters():
    chars = []

    # 1. Winter Skater (Human - Default)
    chars.append(
        CharacterSpec(
            char_id="winter_skater",
            name_ar="متزلج شتوي",
            name_en="Winter Skater",
            category_ar="بشري • ستايل شتوي",
            price=0,
            ability_ar="ثبات متوازن على الجليد ومقاومة انزلاق +25%",
            ability_en="Balanced Ice Grip (+25% slip control)",
            accent_color=(72, 210, 255),
            trail_color=(140, 235, 255),
            jump_mult=1.02,
            momentum_mult=1.04,
            score_mult=1.0,
            coin_mult=1.0,
            slip_resist=0.25,
            pixel_grid=[
                ".....HHHHHH.....",
                "....HHHHHHHH....",
                "...hhHHHHHHhh...",
                "....SSSSSSSS....",
                "....SEESSEES....",
                "....SSSSssSS....",
                ".....SMMMMS.....",
                "...CCCCCCCCCC...",
                "..cCCCCCCCCCCc..",
                "..cCCcCCCCcCCc..",
                "....CCCCCCCC....",
                ".....PPPPPP.....",
                ".....PP..PP.....",
                "....BBB..BBB....",
                "...BBBB..BBBB...",
                "................",
            ],
        )
    )

    # 2. Street Runner (Human)
    chars.append(
        CharacterSpec(
            char_id="street_runner",
            name_ar="عداء شوارع",
            name_en="Street Runner",
            category_ar="بشري • رياضي",
            price=180,
            ability_ar="اكتساب سريع للزخم الأفقي (+18% Momentum)",
            ability_en="Fast Momentum Gain (+18%)",
            accent_color=(255, 145, 48),
            trail_color=(255, 185, 95),
            jump_mult=1.03,
            momentum_mult=1.18,
            score_mult=1.05,
            coin_mult=1.0,
            slip_resist=0.10,
            pixel_grid=[
                ".....HHHHHH.....",
                "....HHHHHHHH....",
                "....hHHHHHHh....",
                "....SSSSSSSS....",
                "....SEESSEES....",
                "....SSSSSSSS....",
                ".....SMMMMS.....",
                "...cCCCCCCCCc...",
                "..ACCCCCCCCCCA..",
                "..aCCccccccCCa..",
                "....CCCCCCCC....",
                ".....PP..PP.....",
                "....PP....PP....",
                "...BBB....BBB...",
                "..cBBB....BBBc..",
                "................",
            ],
        )
    )

    # 3. Glacier Explorer (Human)
    chars.append(
        CharacterSpec(
            char_id="glacier_explorer",
            name_ar="مستكشف جليدي",
            name_en="Glacier Explorer",
            category_ar="بشري • مغامر",
            price=260,
            ability_ar="مضاعفة العملات المكتسبة (+25% Coins)",
            ability_en="Coin Magnet Luck (+25% Coins)",
            accent_color=(255, 210, 70),
            trail_color=(255, 228, 130),
            jump_mult=1.04,
            momentum_mult=1.05,
            score_mult=1.05,
            coin_mult=1.25,
            slip_resist=0.30,
            pixel_grid=[
                "....hhhhhhhh....",
                "...HHHHHHHHHH...",
                "..hhEEEEEEEEhh..",
                "....SSSSSSSS....",
                "....SSSSSSSS....",
                "....SsSSSSsS....",
                ".....SMMMMS.....",
                "..cCCCCCCCCCCc..",
                "..cCCcCCCCcCCc..",
                "..cCCcCCCCcCCc..",
                "....CCCCCCCC....",
                ".....PPPPPP.....",
                "....PP....PP....",
                "...BBB....BBB...",
                "...BBB....BBB...",
                "................",
            ],
        )
    )

    # 4. University Coder (Human)
    chars.append(
        CharacterSpec(
            char_id="uni_coder",
            name_ar="طالب جامعي مبرمج",
            name_en="Campus Coder",
            category_ar="بشري • جامعي",
            price=320,
            ability_ar="ذكاء حسابي يرفع النقاط (+15% Score)",
            ability_en="Smart Multiplier (+15% Score)",
            accent_color=(95, 235, 165),
            trail_color=(140, 250, 195),
            jump_mult=1.03,
            momentum_mult=1.06,
            score_mult=1.15,
            coin_mult=1.10,
            slip_resist=0.15,
            pixel_grid=[
                ".....HHHHHH.....",
                "....HHHHHHHH....",
                "...HHHHHHHHHH...",
                "....SSSSSSSS....",
                "...cEEESSEEEc...",
                "...cE..SS..Ec...",
                ".....SMMMMS.....",
                "...CCCCCCCCCC...",
                "..cCCcCCCCcCCc..",
                "..cCCcCCCCcCCc..",
                "....CCCCCCCC....",
                ".....PPPPPP.....",
                ".....PP..PP.....",
                "....BBB..BBB....",
                "....BBB..BBB....",
                "................",
            ],
        )
    )

    # 5. Frost Boxer (Human)
    chars.append(
        CharacterSpec(
            char_id="frost_boxer",
            name_ar="ملاكم الصقيع",
            name_en="Frost Boxer",
            category_ar="بشري • قتالي",
            price=420,
            ability_ar="قفزة قوية واندفاع عمودي مرتفع (+12% Jump)",
            ability_en="Power Leap (+12% Jump)",
            accent_color=(245, 78, 92),
            trail_color=(255, 130, 140),
            jump_mult=1.12,
            momentum_mult=1.10,
            score_mult=1.08,
            coin_mult=1.05,
            slip_resist=0.20,
            pixel_grid=[
                ".....HHHHHH.....",
                "....HHHHHHHH....",
                "....SSSSSSSS....",
                "....SEESSEES....",
                "....SSSSSSSS....",
                ".....SMMMMS.....",
                "..AA.CCCCCC.AA..",
                ".AAAAccccccAAAA.",
                ".AAAA.CCCC.AAAA.",
                "..AA..CCCC..AA..",
                "......PPPP......",
                ".....PP..PP.....",
                "....PP....PP....",
                "...BBB....BBB...",
                "...BBB....BBB...",
                "................",
            ],
        )
    )

    # 6. Moto Racer (Human)
    chars.append(
        CharacterSpec(
            char_id="moto_racer",
            name_ar="متسابق دراجات",
            name_en="Moto Racer",
            category_ar="بشري • سرعة",
            price=500,
            ability_ar="سرعة قصوى وزخم عالٍ (+22% Momentum & +8% Jump)",
            ability_en="Turbo Drift (+22% Momentum)",
            accent_color=(255, 196, 38),
            trail_color=(255, 222, 110),
            jump_mult=1.08,
            momentum_mult=1.22,
            score_mult=1.10,
            coin_mult=1.12,
            slip_resist=0.22,
            pixel_grid=[
                "....HHHHHHHH....",
                "...HHHHHHHHHH...",
                "...hhEEEEEEhh...",
                "...hhEEEEEEhh...",
                "....SSSSSSSS....",
                ".....SMMMMS.....",
                "...cCCCCCCCCc...",
                "..cCCccccccCCc..",
                "..cCCccccccCCc..",
                "....CCCCCCCC....",
                ".....PPPPPP.....",
                "....PP....PP....",
                "...BBB....BBB...",
                "..cBBB....BBBc..",
                "................",
            ],
        )
    )

    # 7. Crimson Cap & Headphones Hero (Cartoon-inspired)
    chars.append(
        CharacterSpec(
            char_id="redcap_beats",
            name_ar="بطل القبعة الحمراء والسماعات",
            name_en="Crimson Cap & Beats",
            category_ar="كرتوني • أيقونة شبابية",
            price=600,
            ability_ar="إيقاع متناغم يرفع النقاط (+18% Score) والقفز (+7%)",
            ability_en="Beat Boost (+18% Score, +7% Jump)",
            accent_color=(235, 52, 68),
            trail_color=(255, 115, 128),
            jump_mult=1.07,
            momentum_mult=1.12,
            score_mult=1.18,
            coin_mult=1.10,
            slip_resist=0.15,
            pixel_grid=[
                ".....HHHHHH.....",
                "....HHHHHHHH....",
                "...HHHHHHHHHHh..",
                "..AASSSSSSSSAA..",
                "..AASSSSEESSAA..",
                "..AASSSSSSSSAA..",
                "...a.SMMMMS.a...",
                "...CCCCCCCCCC...",
                "..cCCcCCCCcCCc..",
                "..cCCcCCCCcCCc..",
                "....CCCCCCCC....",
                ".....PPPPPP.....",
                ".....PP..PP.....",
                "....BBB..BBB....",
                "...BBBB..BBBB...",
                "................",
            ],
        )
    )

    # 8. Sunny Bucket-Hat Kid (Cartoon-inspired)
    chars.append(
        CharacterSpec(
            char_id="sunny_hat_kid",
            name_ar="فتى القبعة الصفراء",
            name_en="Sunny Hat Kid",
            category_ar="كرتوني • مرح وسريع",
            price=700,
            ability_ar="خفة حركة وقفز مرن (+10% Jump & +20% Coins)",
            ability_en="Bouncy Hop (+10% Jump, +20% Coins)",
            accent_color=(255, 214, 42),
            trail_color=(255, 238, 125),
            jump_mult=1.10,
            momentum_mult=1.10,
            score_mult=1.10,
            coin_mult=1.20,
            slip_resist=0.20,
            pixel_grid=[
                "....HHHHHHHH....",
                "...HHHHHHHHHH...",
                "..hhhhhhhhhhhh..",
                "....SSSSSSSS....",
                "....SEESSEES....",
                "....SsSSSSsS....",
                ".....SMMMMS.....",
                "...CCCCCCCCCC...",
                "..cCCccccccCCc..",
                "..cCCccccccCCc..",
                "....CCCCCCCC....",
                ".....PPPPPP.....",
                ".....PP..PP.....",
                "....BBB..BBB....",
                "....BBB..BBB....",
                "................",
            ],
        )
    )

    # 9. Emerald Cap Hero (Cartoon-inspired)
    chars.append(
        CharacterSpec(
            char_id="emerald_cap_hero",
            name_ar="بطل القبعة الخضراء",
            name_en="Emerald Cap Hero",
            category_ar="كرتوني • بطل المغامرة",
            price=820,
            ability_ar="توازن خارق وثبات على الجليد (+45% Slip Resist & +10% Jump)",
            ability_en="Forest Grip (+45% Ice Control)",
            accent_color=(42, 205, 112),
            trail_color=(115, 240, 168),
            jump_mult=1.10,
            momentum_mult=1.14,
            score_mult=1.12,
            coin_mult=1.15,
            slip_resist=0.45,
            pixel_grid=[
                ".....HHHHHH.....",
                "....HHHHHHHH....",
                "...HHHHHHHHHHh..",
                "....SSSSSSSS....",
                "....SEESSEES....",
                "....SSSSSSSS....",
                ".....SMMMMS.....",
                "...CCCCCCCCCC...",
                "..cCCcCCCCcCCc..",
                "..cCCcCCCCcCCc..",
                "....CCCCCCCC....",
                ".....PPPPPP.....",
                "....PP....PP....",
                "...BBB....BBB...",
                "....BBB..BBB....",
                "................",
            ],
        )
    )

    # 10. Round-Glasses Wizard Kid (Cartoon-inspired)
    chars.append(
        CharacterSpec(
            char_id="round_glasses_kid",
            name_ar="فتى النظارات المستديرة",
            name_en="Round Glasses Kid",
            category_ar="كرتوني • سحر البرج",
            price=950,
            ability_ar="قفزة سحرية وزيادة النقاط (+14% Jump & +22% Score)",
            ability_en="Arcane Leap (+14% Jump, +22% Score)",
            accent_color=(145, 95, 255),
            trail_color=(190, 155, 255),
            jump_mult=1.14,
            momentum_mult=1.12,
            score_mult=1.22,
            coin_mult=1.15,
            slip_resist=0.25,
            pixel_grid=[
                ".....HHHHHH.....",
                "....HHHHHHHH....",
                "...HHHHHHHHHH...",
                "....SSSSSSSS....",
                "...cEEESSEEEc...",
                "...cEEESSSEEc...",
                ".....SMMMMS.....",
                "...CCCCCCCCCC...",
                "..cCCcCCCCcCCc..",
                "..cCCcCCCCcCCc..",
                "....CCCCCCCC....",
                ".....PPPPPP.....",
                ".....PP..PP.....",
                "....BBB..BBB....",
                "....BBB..BBB....",
                "................",
            ],
        )
    )

    # 11. Red & Blue Hero Suit (Cartoon-inspired)
    chars.append(
        CharacterSpec(
            char_id="red_blue_hero",
            name_ar="بطل البدلة الحمراء والزرقاء",
            name_en="Red & Blue Hero",
            category_ar="كرتوني • خارق",
            price=1100,
            ability_ar="اندفاع بطولي وقفز مرتفع (+16% Jump & +16% Momentum)",
            ability_en="Heroic Surge (+16% Jump & Speed)",
            accent_color=(235, 58, 72),
            trail_color=(85, 165, 255),
            jump_mult=1.16,
            momentum_mult=1.16,
            score_mult=1.16,
            coin_mult=1.15,
            slip_resist=0.30,
            pixel_grid=[
                ".....CCCCCC.....",
                "....CCCCCCCC....",
                "...CCcCCCCcCC...",
                "....SSSSSSSS....",
                "....SEESSEES....",
                "....SSSSSSSS....",
                ".....SMMMMS.....",
                "...CCCCCCCCCC...",
                "..cCCcAAAAcCCc..",
                "..cCCcCCCCcCCc..",
                "....PPPPPPPP....",
                "....PP....PP....",
                "...PPP....PPP...",
                "...BBB....BBB...",
                "..cBBB....BBBc..",
                "................",
            ],
        )
    )

    # 12. Dash Cartoon Bunny (Cartoon-inspired)
    chars.append(
        CharacterSpec(
            char_id="dash_bunny",
            name_ar="أرنب كرتوني سريع",
            name_en="Dash Bunny",
            category_ar="كرتوني • أرنب القفز",
            price=1250,
            ability_ar="قفزة مزدوجة الاندفاع عمودياً (+20% Jump & +15% Momentum)",
            ability_en="Super Bunny Hop (+20% Jump)",
            accent_color=(245, 165, 200),
            trail_color=(255, 205, 225),
            jump_mult=1.20,
            momentum_mult=1.15,
            score_mult=1.15,
            coin_mult=1.20,
            slip_resist=0.25,
            pixel_grid=[
                "...HH....HH.....",
                "...HH....HH.....",
                "...Hh....hH.....",
                "....SSSSSSSS....",
                "....SEESSEES....",
                "....SsSMMsSS....",
                ".....SMMMMS.....",
                "...CCCCCCCCCC...",
                "..cCCcCCCCcCCc..",
                "....CCCCCCCC....",
                ".....PPPPPP.....",
                "....PP....PP....",
                "...BBB....BBB...",
                "..BBBB....BBBB..",
                "......BBBB......",
                "................",
            ],
        )
    )

    # 13. Blue Cartoon Cat (Cartoon-inspired)
    chars.append(
        CharacterSpec(
            char_id="blue_toon_cat",
            name_ar="قط كرتوني أزرق",
            name_en="Blue Toon Cat",
            category_ar="كرتوني • رفيق القمة",
            price=1450,
            ability_ar="رشاقة عالية وجمع وفير للعملات (+18% Jump & +35% Coins)",
            ability_en="Cat Agility (+18% Jump, +35% Coins)",
            accent_color=(64, 175, 255),
            trail_color=(140, 215, 255),
            jump_mult=1.18,
            momentum_mult=1.18,
            score_mult=1.20,
            coin_mult=1.35,
            slip_resist=0.35,
            pixel_grid=[
                "..HH........HH..",
                ".HHHH......HHHH.",
                "..HhCCCCCCCChH..",
                "...CCCCCCCCCC...",
                "...CEEESSSEEC...",
                "...CCcSMMscCC...",
                "....CCCCCCCC....",
                "..AA.CCCCCC.AA..",
                ".....cCCCCc.....",
                "......PPPP......",
                ".....PP..PP.....",
                "....PP....PP....",
                "...BBB....BBB...",
                "....BBB..BBB..BB",
                "..............BB",
                "................",
            ],
        )
    )

    # 14. Frost Dragon Legend (Cartoon/Fantasy Legend)
    chars.append(
        CharacterSpec(
            char_id="frost_dragon_legend",
            name_ar="أسطورة تنين الصقيع",
            name_en="Frost Dragon Legend",
            category_ar="كرتوني • أسطورة القمة 50",
            price=1800,
            ability_ar="قدرة أسطورية شاملة (+24% Jump, +24% Momentum, +30% Score & Coins)",
            ability_en="Legend Mastery (All Stats Boosted)",
            accent_color=(255, 212, 68),
            trail_color=(95, 235, 255),
            jump_mult=1.24,
            momentum_mult=1.24,
            score_mult=1.30,
            coin_mult=1.30,
            slip_resist=0.50,
            pixel_grid=[
                "...AA......AA...",
                "..AAAA....AAAA..",
                "...CCCCCCCCCC...",
                "..cCCcCCCCcCCc..",
                "..cCEEESSEEEcC..",
                "..cCCcSMMscCCc..",
                "....CCCCCCCC....",
                ".AA.cCCAAcCC.AA.",
                "AAA..CCCCCC..AAA",
                ".....cCCCCc.....",
                "......PPPP......",
                ".....PP..PP.....",
                "....PP....PP....",
                "...BBB....BBB..B",
                "..cBBB....BBBcBB",
                "................",
            ],
        )
    )

    return chars


CHARACTERS_LIST = _build_all_characters()
CHARACTERS_BY_ID = {c.char_id: c for c in CHARACTERS_LIST}


def get_character(char_id):
    return CHARACTERS_BY_ID.get(char_id, CHARACTERS_LIST[0])


def _shade(color, factor):
    return (
        max(0, min(255, int(color[0] * factor))),
        max(0, min(255, int(color[1] * factor))),
        max(0, min(255, int(color[2] * factor))),
    )


def render_character_sprite(
    spec,
    width=34,
    height=48,
    facing_right=True,
    anim_phase=0.0,
    airborne=False,
    momentum_ratio=0.0,
):
    """
    Renders a crisp, detailed Pixel Art surface from the character's 16x16 grid,
    including running stride, airborne/momentum tilt, and distinct character details.
    """
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    grid = spec.pixel_grid
    rows = len(grid)
    cols = len(grid[0]) if rows else 16

    palette = {
        "H": spec.accent_color,
        "h": _shade(spec.accent_color, 1.25),
        "S": (244, 198, 162),
        "s": (214, 158, 120),
        "E": (22, 28, 42),
        "M": (185, 72, 82),
        "C": _shade(spec.accent_color, 0.78),
        "c": (235, 244, 255),
        "P": (44, 66, 108),
        "B": (34, 40, 56),
        "A": (255, 214, 68),
    }

    # Character-specific fine tuning for visual variety across all 14 sprites
    if spec.char_id == "winter_skater":
        palette["H"] = (48, 168, 235)
        palette["h"] = (240, 248, 255)
        palette["C"] = (34, 86, 152)
        palette["M"] = (232, 72, 92)
    elif spec.char_id == "street_runner":
        palette["H"] = (62, 46, 36)
        palette["C"] = (238, 118, 36)
        palette["P"] = (38, 44, 58)
    elif spec.char_id == "glacier_explorer":
        palette["H"] = (218, 162, 54)
        palette["h"] = (120, 78, 28)
        palette["E"] = (72, 225, 255)
        palette["C"] = (182, 68, 52)
    elif spec.char_id == "uni_coder":
        palette["H"] = (38, 34, 48)
        palette["C"] = (48, 138, 112)
        palette["c"] = (120, 245, 185)
    elif spec.char_id == "frost_boxer":
        palette["H"] = (54, 42, 38)
        palette["C"] = (214, 48, 66)
        palette["A"] = (245, 66, 82)
    elif spec.char_id == "moto_racer":
        palette["H"] = (235, 175, 28)
        palette["E"] = (35, 215, 245)
        palette["C"] = (42, 48, 64)
        palette["c"] = (245, 195, 45)
    elif spec.char_id == "redcap_beats":
        palette["H"] = (228, 48, 64)
        palette["h"] = (248, 248, 252)
        palette["A"] = (255, 205, 52)
        palette["C"] = (52, 68, 104)
    elif spec.char_id == "sunny_hat_kid":
        palette["H"] = (248, 206, 36)
        palette["h"] = (225, 172, 18)
        palette["C"] = (66, 152, 235)
    elif spec.char_id == "emerald_cap_hero":
        palette["H"] = (36, 188, 98)
        palette["h"] = (135, 245, 175)
        palette["C"] = (42, 128, 78)
        palette["P"] = (238, 242, 246)
    elif spec.char_id == "round_glasses_kid":
        palette["H"] = (42, 36, 52)
        palette["c"] = (235, 205, 72)
        palette["C"] = (118, 68, 224)
    elif spec.char_id == "red_blue_hero":
        palette["C"] = (224, 46, 62)
        palette["c"] = (248, 248, 252)
        palette["P"] = (36, 88, 196)
        palette["A"] = (255, 216, 64)
    elif spec.char_id == "dash_bunny":
        palette["H"] = (246, 248, 252)
        palette["h"] = (245, 145, 185)
        palette["S"] = (246, 248, 252)
        palette["s"] = (245, 155, 190)
        palette["C"] = (72, 155, 242)
    elif spec.char_id == "blue_toon_cat":
        palette["H"] = (54, 156, 242)
        palette["h"] = (245, 150, 185)
        palette["C"] = (54, 156, 242)
        palette["c"] = (195, 232, 255)
        palette["A"] = (255, 205, 52)
    elif spec.char_id == "frost_dragon_legend":
        palette["C"] = (56, 178, 245)
        palette["c"] = (175, 242, 255)
        palette["A"] = (255, 206, 54)
        palette["P"] = (38, 86, 154)

    # Pixel-art grid surface
    px_w = max(2, width // cols)
    px_h = max(2, height // rows)
    grid_surf = pygame.Surface((cols * px_w, rows * px_h), pygame.SRCALPHA)

    stride = int(math.sin(anim_phase * 8.0) * 2) if not airborne else 0

    for r_idx, row in enumerate(grid):
        for c_idx, ch in enumerate(row):
            if ch == "." or ch not in palette:
                continue
            col = palette[ch]
            x_off = c_idx * px_w
            y_off = r_idx * px_h

            # Subtle leg stride in lower rows when running on ground
            if not airborne and r_idx >= 11 and abs(momentum_ratio) > 0.08:
                if c_idx < cols // 2:
                    x_off += stride
                else:
                    x_off -= stride

            pygame.draw.rect(grid_surf, col, (x_off, y_off, px_w, px_h))

    if not facing_right:
        grid_surf = pygame.transform.flip(grid_surf, True, False)

    # Tilt slightly when running fast or airborne
    tilt_angle = 0.0
    if airborne and abs(momentum_ratio) > 0.25:
        tilt_angle = -10.0 * momentum_ratio if facing_right else -10.0 * momentum_ratio
    elif abs(momentum_ratio) > 0.35:
        tilt_angle = -5.0 * momentum_ratio

    if abs(tilt_angle) > 0.5:
        grid_surf = pygame.transform.rotate(grid_surf, tilt_angle)

    dest_rect = grid_surf.get_rect(center=(width // 2, height // 2))
    surf.blit(grid_surf, dest_rect)

    # Momentum / jump aura indicator
    if abs(momentum_ratio) > 0.35 or airborne:
        aura_alpha = int(min(130, 45 + abs(momentum_ratio) * 85))
        aura_surf = pygame.Surface((width + 12, height + 12), pygame.SRCALPHA)
        pygame.draw.ellipse(
            aura_surf,
            (*spec.trail_color[:3], aura_alpha),
            (2, 2, width + 8, height + 8),
            width=2,
        )
        surf.blit(aura_surf, (-6, -6))

    return surf