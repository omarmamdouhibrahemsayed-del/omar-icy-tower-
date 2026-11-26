import json
import os
import pygame

# ==============================================================================
# Icy Tower 50: Legends & Styles - Settings & Persistence Module
# ==============================================================================

APP_TITLE = "Icy Tower 50: Legends & Styles"
SCREEN_WIDTH = 1120
SCREEN_HEIGHT = 760
FPS = 60

SAVE_FILE_PATH = "save_data.json"
DEFAULT_UNLOCKED_CHARACTER_ID = "winter_skater"

# Gameplay & Physics Constants (Classic Icy Tower feel + modern tuning)
GRAVITY_BASE = 2150.0          # px / s^2
FAST_FALL_GRAVITY_MULT = 2.15 # Multiplier when holding Down arrow mid-air
MAX_FALL_SPEED = 1180.0

RUN_ACCEL_GROUND = 3400.0
RUN_ACCEL_AIR = 2250.0
FRICTION_GROUND = 2900.0
DRAG_AIR = 620.0
MAX_WALK_SPEED = 360.0
MAX_MOMENTUM_SPEED = 780.0
MOMENTUM_BUILD_RATE = 460.0
MOMENTUM_DECAY_RATE = 260.0

JUMP_VELOCITY_BASE = -790.0
JUMP_MOMENTUM_BOOST = -240.0
SPRING_JUMP_VELOCITY = -1140.0

PLAYER_WIDTH = 34
PLAYER_HEIGHT = 48
PLATFORM_HEIGHT = 20
FLOORS_PER_LEVEL = 22
FLOOR_SPACING_BASE = 78

# Palette
COLOR_WHITE = (248, 250, 252)
COLOR_BLACK = (10, 14, 22)
COLOR_DARK_PANEL = (18, 25, 38)
COLOR_PANEL_BORDER = (72, 104, 145)
COLOR_ACCENT_CYAN = (64, 224, 255)
COLOR_ACCENT_GOLD = (255, 208, 64)
COLOR_ACCENT_GREEN = (72, 230, 145)
COLOR_ACCENT_RED = (245, 82, 96)
COLOR_MUTED_TEXT = (158, 175, 198)


def default_save_data():
    return {
        "coins": 250,
        "total_score": 0,
        "best_score": 0,
        "highest_unlocked_level": 1,
        "selected_character": DEFAULT_UNLOCKED_CHARACTER_ID,
        "owned_characters": [DEFAULT_UNLOCKED_CHARACTER_ID],
        "audio": {
            "music_enabled": True,
            "sfx_enabled": True,
            "master_volume": 0.75,
            "music_volume": 0.55,
            "sfx_volume": 0.85,
        },
        "level_records": {},
    }


class SaveManager:
    """Handles loading, saving, and validating persistent game data in save_data.json."""

    def __init__(self, filepath=SAVE_FILE_PATH):
        self.filepath = filepath
        self.data = default_save_data()
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            self.data = default_save_data()
            self.save()
            return self.data

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                loaded = json.load(f)
        except (OSError, json.JSONDecodeError, ValueError):
            self.data = default_save_data()
            self.save()
            return self.data

        base = default_save_data()
        if isinstance(loaded, dict):
            base["coins"] = max(0, int(loaded.get("coins", base["coins"])))
            base["total_score"] = max(0, int(loaded.get("total_score", base["total_score"])))
            base["best_score"] = max(0, int(loaded.get("best_score", base["best_score"])))
            unlocked = int(loaded.get("highest_unlocked_level", base["highest_unlocked_level"]))
            base["highest_unlocked_level"] = max(1, min(50, unlocked))

            owned = loaded.get("owned_characters", base["owned_characters"])
            if not isinstance(owned, list) or not owned:
                owned = [DEFAULT_UNLOCKED_CHARACTER_ID]
            cleaned_owned = []
            for cid in owned:
                if isinstance(cid, str) and cid not in cleaned_owned:
                    cleaned_owned.append(cid)
            if DEFAULT_UNLOCKED_CHARACTER_ID not in cleaned_owned:
                cleaned_owned.insert(0, DEFAULT_UNLOCKED_CHARACTER_ID)
            base["owned_characters"] = cleaned_owned

            selected = loaded.get("selected_character", DEFAULT_UNLOCKED_CHARACTER_ID)
            if selected not in cleaned_owned:
                selected = cleaned_owned[0]
            base["selected_character"] = selected

            audio_in = loaded.get("audio", {})
            if isinstance(audio_in, dict):
                base["audio"]["music_enabled"] = bool(audio_in.get("music_enabled", True))
                base["audio"]["sfx_enabled"] = bool(audio_in.get("sfx_enabled", True))
                base["audio"]["master_volume"] = max(0.0, min(1.0, float(audio_in.get("master_volume", 0.75))))
                base["audio"]["music_volume"] = max(0.0, min(1.0, float(audio_in.get("music_volume", 0.55))))
                base["audio"]["sfx_volume"] = max(0.0, min(1.0, float(audio_in.get("sfx_volume", 0.85))))

            records_in = loaded.get("level_records", {})
            if isinstance(records_in, dict):
                clean_records = {}
                for k, v in records_in.items():
                    if isinstance(v, dict):
                        clean_records[str(k)] = {
                            "completed": bool(v.get("completed", False)),
                            "best_score": max(0, int(v.get("best_score", 0))),
                            "best_combo": max(0, int(v.get("best_combo", 0))),
                        }
                base["level_records"] = clean_records

        self.data = base
        return self.data

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    @property
    def coins(self):
        return self.data["coins"]

    @coins.setter
    def coins(self, value):
        self.data["coins"] = max(0, int(value))

    @property
    def best_score(self):
        return int(self.data.get("best_score", 0))

    @best_score.setter
    def best_score(self, value):
        self.data["best_score"] = max(0, int(value))

    @property
    def highest_unlocked_level(self):
        return self.data["highest_unlocked_level"]

    @highest_unlocked_level.setter
    def highest_unlocked_level(self, value):
        self.data["highest_unlocked_level"] = max(1, min(50, int(value)))

    @property
    def selected_character(self):
        return self.data["selected_character"]

    @selected_character.setter
    def selected_character(self, char_id):
        if char_id in self.data["owned_characters"]:
            self.data["selected_character"] = char_id

    @property
    def owned_characters(self):
        return self.data["owned_characters"]

    @property
    def audio(self):
        return self.data["audio"]

    def unlock_character(self, char_id, price):
        if char_id in self.data["owned_characters"]:
            self.data["selected_character"] = char_id
            self.save()
            return True
        if self.data["coins"] >= price:
            self.data["coins"] -= price
            self.data["owned_characters"].append(char_id)
            self.data["selected_character"] = char_id
            self.save()
            return True
        return False

    def record_level_result(self, level_num, score, max_combo, completed):
        key = str(level_num)
        prev = self.data["level_records"].get(
            key, {"completed": False, "best_score": 0, "best_combo": 0}
        )
        prev["completed"] = prev["completed"] or completed
        prev["best_score"] = max(prev["best_score"], int(score))
        prev["best_combo"] = max(prev["best_combo"], int(max_combo))
        self.data["level_records"][key] = prev

        if score > self.data["best_score"]:
            self.data["best_score"] = int(score)
        if completed and level_num >= self.data["highest_unlocked_level"] and level_num < 50:
            self.data["highest_unlocked_level"] = level_num + 1
        self.save()


def contains_arabic(text):
    for ch in text:
        code = ord(ch)
        if (0x0600 <= code <= 0x06FF) or (0x0750 <= code <= 0x077F) or (0xFB50 <= code <= 0xFDFF) or (0xFE70 <= code <= 0xFEFF):
            return True
    return False


def shape_arabic_if_needed(text):
    """Uses python-bidi / arabic-reshaper when available, otherwise falls back safely."""
    if not contains_arabic(text):
        return text
    try:
        import arabic_reshaper  # type: ignore
        from bidi.algorithm import get_display  # type: ignore

        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


class FontLibrary:
    """Loads clean fonts supporting both Arabic and Latin glyphs across platforms."""

    ARABIC_CANDIDATES = [
        "Noto Naskh Arabic",
        "Amiri",
        "Tahoma",
        "Arial",
        "DejaVu Sans",
        "Segoe UI",
    ]
    LATIN_CANDIDATES = [
        "Segoe UI",
        "DejaVu Sans",
        "Arial",
        "Liberation Sans",
    ]

    def __init__(self):
        pygame.font.init()
        self._cache = {}
        self._arabic_font_path = self._find_font_file(self.ARABIC_CANDIDATES)
        self._latin_font_path = self._find_font_file(self.LATIN_CANDIDATES)

    def _find_font_file(self, candidates):
        for name in candidates:
            path = pygame.font.match_font(name)
            if path and os.path.exists(path):
                return path
        return None

    def get(self, size, bold=False, arabic=False):
        key = (int(size), bool(bold), bool(arabic))
        if key not in self._cache:
            chosen_path = self._arabic_font_path if arabic else self._latin_font_path
            if chosen_path:
                font = pygame.font.Font(chosen_path, int(size))
                font.set_bold(bold)
            else:
                font = pygame.font.SysFont(
                    self.ARABIC_CANDIDATES if arabic else self.LATIN_CANDIDATES,
                    int(size),
                    bold=bold,
                )
            self._cache[key] = font
        return self._cache[key]

    def render_text(self, text, size, color, bold=False, antialias=True):
        is_ar = contains_arabic(text)
        processed = shape_arabic_if_needed(text)
        font = self.get(size, bold=bold, arabic=is_ar)
        return font.render(processed, antialias, color)