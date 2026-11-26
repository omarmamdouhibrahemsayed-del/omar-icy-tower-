import io
import math
import random
import struct
import wave
import pygame

# ==============================================================================
# Icy Tower 50: Legends & Styles - Procedural & Level-Adaptive Sound Engine
# ==============================================================================


class SoundEngine:
    """
    Generates clean, non-fatiguing synthesized WAV effects and level-tuned
    background music loops in memory using wave + struct + pygame.mixer.
    Every level (1..50) alters musical scale, tempo, harmonic timbre, and SFX
    pitch/texture based on level number and theme.
    """

    SAMPLE_RATE = 22050

    SCALES = {
        "ice": [261.63, 293.66, 329.63, 392.00, 440.00, 523.25],       # C Major Pentatonic
        "polar_night": [220.00, 246.94, 261.63, 329.63, 349.23, 440.00], # A Minor
        "crystal_cave": [293.66, 329.63, 369.99, 440.00, 493.88, 587.33], # D Lydian-ish
        "aurora": [246.94, 277.18, 329.63, 369.99, 415.30, 493.88],      # B Major Pentatonic
        "blizzard": [233.08, 261.63, 277.18, 349.23, 392.00, 466.16],    # Bb Dorian-ish
        "ancient_tower": [196.00, 220.00, 261.63, 293.66, 329.63, 392.00], # G Mixolydian
        "cold_space": [277.18, 311.13, 369.99, 415.30, 466.16, 554.37],  # C# Minor Pentatonic
        "volcanic_frost": [207.65, 233.08, 261.63, 311.13, 349.23, 415.30], # Ab Phrygian/Minor
    }

    def __init__(self, audio_settings):
        self.music_enabled = bool(audio_settings.get("music_enabled", True))
        self.sfx_enabled = bool(audio_settings.get("sfx_enabled", True))
        self.master_volume = float(audio_settings.get("master_volume", 0.75))
        self.music_volume = float(audio_settings.get("music_volume", 0.55))
        self.sfx_volume = float(audio_settings.get("sfx_volume", 0.85))

        self.initialized = False
        self.current_level = 0
        self.current_theme = ""
        self.music_channel = None
        self.current_music_sound = None
        self.sfx_cache = {}

        self._init_mixer()
        self.configure_for_level(1, "ice")

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=self.SAMPLE_RATE, size=-16, channels=1, buffer=512)
            pygame.mixer.set_num_channels(16)
            self.music_channel = pygame.mixer.Channel(0)
            self.initialized = True
        except Exception:
            self.initialized = False

    def sync_settings(self, audio_settings):
        self.music_enabled = bool(audio_settings.get("music_enabled", True))
        self.sfx_enabled = bool(audio_settings.get("sfx_enabled", True))
        self.master_volume = float(audio_settings.get("master_volume", 0.75))
        self.music_volume = float(audio_settings.get("music_volume", 0.55))
        self.sfx_volume = float(audio_settings.get("sfx_volume", 0.85))
        self._apply_music_volume()

    def _effective_music_vol(self):
        if not self.music_enabled:
            return 0.0
        return max(0.0, min(1.0, self.master_volume * self.music_volume * 0.42))

    def _effective_sfx_vol(self):
        if not self.sfx_enabled:
            return 0.0
        return max(0.0, min(1.0, self.master_volume * self.sfx_volume))

    def _apply_music_volume(self):
        if not self.initialized or not self.music_channel:
            return
        vol = self._effective_music_vol()
        self.music_channel.set_volume(vol)
        if vol <= 0.001:
            self.music_channel.pause()
        else:
            self.music_channel.unpause()
            if not self.music_channel.get_busy() and self.current_music_sound is not None:
                self.music_channel.play(self.current_music_sound, loops=-1)

    def _samples_to_sound(self, samples):
        if not self.initialized:
            return None
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.SAMPLE_RATE)
            frames = bytearray()
            for s in samples:
                clamped = max(-1.0, min(1.0, s))
                frames.extend(struct.pack("<h", int(clamped * 32767)))
            wf.writeframes(bytes(frames))
        buf.seek(0)
        try:
            return pygame.mixer.Sound(file=buf)
        except Exception:
            return None

    def _level_pitch_factor(self, level_num):
        # Smooth pitch progression across levels 1..50 without harsh high frequencies
        clamped = max(1, min(50, int(level_num)))
        return 0.88 + ((clamped - 1) / 49.0) * 0.34

    def configure_for_level(self, level_num, theme_key):
        level_num = max(1, min(50, int(level_num)))
        if level_num == self.current_level and theme_key == self.current_theme:
            self._apply_music_volume()
            return

        self.current_level = level_num
        self.current_theme = theme_key
        self.sfx_cache.clear()
        self._build_level_music(level_num, theme_key)
        self._apply_music_volume()

    def _build_level_music(self, level_num, theme_key):
        if not self.initialized:
            return

        scale = self.SCALES.get(theme_key, self.SCALES["ice"])
        pitch_mult = self._level_pitch_factor(level_num)
        # Tempo increases subtly with level
        bpm = 96 + (level_num % 10) * 4 + (level_num // 10) * 3
        beat_sec = 60.0 / bpm
        steps = 16
        step_samples = int(self.SAMPLE_RATE * beat_sec * 0.5)
        total_samples = step_samples * steps

        rng = random.Random(level_num * 1009 + sum(ord(c) for c in theme_key))
        pattern = [rng.choice(scale) * pitch_mult for _ in range(steps)]
        # Anchor roots on beats 0, 4, 8, 12
        pattern[0] = scale[0] * pitch_mult
        pattern[4] = scale[2 % len(scale)] * pitch_mult
        pattern[8] = scale[4 % len(scale)] * pitch_mult
        pattern[12] = scale[1 % len(scale)] * pitch_mult

        out = [0.0] * total_samples
        two_pi = 2.0 * math.pi
        wave_mode = level_num % 4

        for step_idx, freq in enumerate(pattern):
            start = step_idx * step_samples
            for i in range(step_samples):
                t = i / self.SAMPLE_RATE
                env = math.sin(math.pi * min(1.0, i / max(1, step_samples))) ** 0.7
                phase = two_pi * freq * t
                if wave_mode == 0:
                    val = 0.65 * math.sin(phase) + 0.25 * math.sin(2.0 * phase)
                elif wave_mode == 1:
                    val = 0.55 * math.sin(phase) + 0.30 * math.sin(3.0 * phase)
                elif wave_mode == 2:
                    tri = 2.0 * abs(2.0 * ((freq * t) % 1.0) - 1.0) - 1.0
                    val = 0.50 * tri + 0.35 * math.sin(0.5 * phase)
                else:
                    val = 0.60 * math.sin(phase) + 0.20 * math.sin(1.5 * phase)
                out[start + i] = val * env * 0.36

        self.current_music_sound = self._samples_to_sound(out)
        if self.current_music_sound and self.music_channel:
            self.music_channel.play(self.current_music_sound, loops=-1)
            self._apply_music_volume()

    def _get_sfx(self, key):
        if not self.initialized or self._effective_sfx_vol() <= 0.001:
            return None
        if key in self.sfx_cache:
            return self.sfx_cache[key]

        pitch = self._level_pitch_factor(self.current_level)
        lvl_mod = 1.0 + ((self.current_level - 1) % 7) * 0.025
        f_mult = pitch * lvl_mod
        two_pi = 2.0 * math.pi
        samples = []

        if key == "jump":
            dur = 0.16
            n = int(self.SAMPLE_RATE * dur)
            for i in range(n):
                prog = i / n
                env = (1.0 - prog) ** 1.4
                freq = (270.0 + prog * 360.0) * f_mult
                samples.append(math.sin(two_pi * freq * (i / self.SAMPLE_RATE)) * env * 0.45)

        elif key == "momentum_jump":
            dur = 0.24
            n = int(self.SAMPLE_RATE * dur)
            for i in range(n):
                prog = i / n
                env = (1.0 - prog) ** 1.2
                freq = (340.0 + prog * 540.0) * f_mult
                s = 0.65 * math.sin(two_pi * freq * (i / self.SAMPLE_RATE)) + 0.35 * math.sin(
                    two_pi * freq * 1.5 * (i / self.SAMPLE_RATE)
                )
                samples.append(s * env * 0.48)

        elif key == "land":
            dur = 0.09
            n = int(self.SAMPLE_RATE * dur)
            for i in range(n):
                prog = i / n
                env = (1.0 - prog) ** 2.2
                freq = (180.0 - prog * 70.0) * f_mult
                samples.append(math.sin(two_pi * freq * (i / self.SAMPLE_RATE)) * env * 0.42)

        elif key == "spring":
            dur = 0.28
            n = int(self.SAMPLE_RATE * dur)
            for i in range(n):
                prog = i / n
                env = (1.0 - prog) ** 1.1
                freq = (240.0 + 420.0 * math.sin(prog * math.pi * 2.0)) * f_mult
                samples.append(math.sin(two_pi * freq * (i / self.SAMPLE_RATE)) * env * 0.5)

        elif key == "break_plat":
            dur = 0.15
            n = int(self.SAMPLE_RATE * dur)
            rng = random.Random(self.current_level * 37)
            for i in range(n):
                prog = i / n
                env = (1.0 - prog) ** 1.8
                noise = rng.uniform(-1.0, 1.0)
                tone = math.sin(two_pi * (150.0 * f_mult) * (i / self.SAMPLE_RATE))
                samples.append((0.65 * noise + 0.35 * tone) * env * 0.45)

        elif key == "combo":
            dur = 0.22
            n = int(self.SAMPLE_RATE * dur)
            for i in range(n):
                prog = i / n
                env = (1.0 - prog) ** 1.3
                base = (440.0 if prog < 0.5 else 587.33) * f_mult
                samples.append(math.sin(two_pi * base * (i / self.SAMPLE_RATE)) * env * 0.42)

        elif key == "coin":
            dur = 0.13
            n = int(self.SAMPLE_RATE * dur)
            for i in range(n):
                prog = i / n
                env = (1.0 - prog) ** 1.5
                freq = (784.0 if prog < 0.45 else 1046.5) * min(1.25, f_mult)
                samples.append(math.sin(two_pi * freq * (i / self.SAMPLE_RATE)) * env * 0.35)

        elif key == "level_up":
            notes = [523.25, 659.25, 783.99, 1046.50]
            note_n = int(self.SAMPLE_RATE * 0.085)
            for idx, note in enumerate(notes):
                f = note * min(1.2, f_mult)
                for i in range(note_n):
                    prog = i / note_n
                    env = (1.0 - prog) ** 1.3
                    samples.append(math.sin(two_pi * f * (i / self.SAMPLE_RATE)) * env * 0.42)

        elif key == "ui_click":
            dur = 0.055
            n = int(self.SAMPLE_RATE * dur)
            for i in range(n):
                prog = i / n
                env = (1.0 - prog) ** 2.0
                samples.append(math.sin(two_pi * (620.0 * f_mult) * (i / self.SAMPLE_RATE)) * env * 0.3)

        elif key == "buy":
            notes = [587.33, 880.0]
            note_n = int(self.SAMPLE_RATE * 0.09)
            for note in notes:
                for i in range(note_n):
                    prog = i / note_n
                    env = (1.0 - prog) ** 1.4
                    samples.append(math.sin(two_pi * note * (i / self.SAMPLE_RATE)) * env * 0.4)

        elif key == "game_over":
            dur = 0.45
            n = int(self.SAMPLE_RATE * dur)
            for i in range(n):
                prog = i / n
                env = (1.0 - prog) ** 1.2
                freq = (360.0 - prog * 210.0) * pitch
                samples.append(math.sin(two_pi * freq * (i / self.SAMPLE_RATE)) * env * 0.45)

        snd = self._samples_to_sound(samples)
        if snd:
            snd.set_volume(self._effective_sfx_vol())
            self.sfx_cache[key] = snd
        return snd

    def play_sfx(self, key):
        snd = self._get_sfx(key)
        if snd:
            snd.set_volume(self._effective_sfx_vol())
            snd.play()

    def set_music_enabled(self, enabled):
        self.music_enabled = bool(enabled)
        self._apply_music_volume()

    def set_sfx_enabled(self, enabled):
        self.sfx_enabled = bool(enabled)

    def set_volumes(self, master=None, music=None, sfx=None):
        if master is not None:
            self.master_volume = max(0.0, min(1.0, float(master)))
        if music is not None:
            self.music_volume = max(0.0, min(1.0, float(music)))
        if sfx is not None:
            self.sfx_volume = max(0.0, min(1.0, float(sfx)))
        self._apply_music_volume()