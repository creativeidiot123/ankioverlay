from __future__ import annotations
import atexit
import copy
import html
import math
import os
import time
import traceback
from dataclasses import dataclass, field
from enum import Enum
from aqt import gui_hooks, mw
from aqt.qt import *
from aqt.utils import tooltip
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except Exception:
    from aqt.qt import QWebEngineView
try:
    from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
except Exception:
    try:
        from aqt.qt import QAudioOutput, QMediaPlayer
    except Exception:
        QAudioOutput = None
        QMediaPlayer = None
try:
    from pynput import keyboard
    HAS_PYNPUT = True
except Exception:
    keyboard = None
    HAS_PYNPUT = False
DEFAULT_CONFIG = {
    "deck_maps": [], "deck_themes": [],
    "width": 389, "height": 368, "opacity": 16, "pos_x": 1504, "pos_y": 649,
    "color_word": "#ff79c6", "color_pitch": "#50fa7b", "color_sent": "#bd93f9",
    "key_again": "p", "key_hard": "[", "key_good": "]", "key_easy": "9",
    "key_flip": "o", "key_replay": "/", "key_undo": "l", "key_toggle": "<ctrl>+9",
    "debug_status": False, "grade_from_question_mode": "flip_only",
    "font_size_word": 42, "font_size_translation": 26, "font_size_example": 18,
    "focus_dim_enabled": True, "focus_dim_idle_sec": 28.0, "focus_dim_warning_sec": 5.0,
    "focus_dim_punish_sec": 5.0, "focus_dim_lockdown_sec": 5.0, "focus_dim_ramp_sec": 5.0,
    "focus_dim_timing_model": "durations_v2", "focus_dim_warning_opacity": 45,
    "focus_dim_punish_opacity": 75, "focus_dim_max_opacity": 100, "focus_dim_curve": "quad",
    "focus_dim_question_only": False, "focus_dim_safe_padding": 16, "focus_dim_safe_feather": 20,
    "focus_dim_warning_text": "PAY ATTENTION", "focus_dim_warning_subtext": "Answer the card",
    "focus_dim_warning_style": "pulse", "focus_dim_warning_font_px": 30,
    "focus_dim_replay_reset_mode": "partial", "focus_dim_partial_reset_sec": 2.5,
    "focus_dim_replay_counts_as_activity": True, "focus_dim_show_message": True,
    "focus_dim_message": "PAY ATTENTION",
}
HOTKEY_KEYS = ["key_toggle", "key_flip", "key_replay", "key_undo", "key_again", "key_hard", "key_good", "key_easy"]
HOTKEY_LABELS = {"key_toggle":"Toggle","key_flip":"Flip","key_replay":"Replay","key_undo":"Undo","key_again":"Again","key_hard":"Hard","key_good":"Good","key_easy":"Easy"}
GRADE_KEYS = ("key_again", "key_hard", "key_good", "key_easy")
DECK_MAP_FIELDS = [
    ("German Word", "german_word"), ("English Word", "english_word"),
    ("German Ex 1", "german_example_1"), ("English Ex 1", "english_example_1"),
    ("German Ex 2", "german_example_2"), ("English Ex 2", "english_example_2"),
    ("German Ex 3", "german_example_3"), ("English Ex 3", "english_example_3"),
]
LEGACY_FIELD_MAP = {"german_word":"word", "english_word":"definition", "german_example_1":"sentence", "english_example_1":"image"}
THEME_MODES = ("", "full", "compact")
NUMPAD_TOKEN_TO_VK = {"<num0>":"<96>","<num1>":"<97>","<num2>":"<98>","<num3>":"<99>","<num4>":"<100>","<num5>":"<101>","<num6>":"<102>","<num7>":"<103>","<num8>":"<104>","<num9>":"<105>","<num_star>":"<106>","<num_plus>":"<107>","<num_minus>":"<109>","<num_dot>":"<110>","<num_slash>":"<111>"}
NUMPAD_VK_BY_PRIMARY_KEY = {"0":"<96>","1":"<97>","2":"<98>","3":"<99>","4":"<100>","5":"<101>","6":"<102>","7":"<103>","8":"<104>","9":"<105>","*":"<106>","-":"<109>",".":"<110>","/":"<111>"}
COMMAND_DEBOUNCE_SEC = {"flip":0.18,"again":0.18,"hard":0.18,"good":0.18,"easy":0.18,"undo":0.18,"replay":0.08,"toggle":0.2}
GRADE_SOUND_FILES = {"correct": "_tinder_correct.mp3", "wrong": "_tinder_wrong.mp3"}
GRADE_SOUND_BY_COMMAND = {"again":"wrong", "hard":"correct", "good":"correct", "easy":"correct"}
PAY_ATTENTION_SOUND_FILE = "pay_attention.mp3"
PAY_ATTENTION_INTERVAL_MS = 3000
PENDING_TIMEOUT_SEC = 4.2
QUEUED_TRANSITION_MAX_AGE_SEC = 4.5
TRANSITION_WATCHDOG_MS = 120
FOCUS_DIM_TICK_MS = 75
LEFT_MOUSE_BUTTON = Qt.MouseButton.LeftButton if hasattr(Qt, "MouseButton") else Qt.LeftButton
RESIZE_CURSOR = Qt.CursorShape.SizeFDiagCursor if hasattr(Qt, "CursorShape") else Qt.SizeFDiagCursor
DRAG_CURSOR = Qt.CursorShape.SizeAllCursor if hasattr(Qt, "CursorShape") else Qt.SizeAllCursor
ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter if hasattr(Qt, "AlignmentFlag") else Qt.AlignCenter
def _log(msg):
    print(f"[Anki Overlay] {msg}")
def _now():
    return time.monotonic()
def _clamp_float(v, default, lo, hi):
    try:
        v = float(v)
    except Exception:
        v = float(default)
    return max(float(lo), min(float(hi), v))
def _curve_value(progress, curve):
    p = max(0.0, min(1.0, float(progress)))
    return p if curve == "linear" else p * p * p if curve == "cubic" else p * p
def _qt_window_flag(name):
    if hasattr(Qt, "WindowType") and hasattr(Qt.WindowType, name):
        return getattr(Qt.WindowType, name)
    return getattr(Qt, name)
def _event_global_point(event):
    try:
        return event.globalPosition().toPoint()
    except Exception:
        return event.globalPos()
def _normalize_hotkey(value):
    combo = str(value or "").strip().lower()
    if not combo:
        return ""
    for token, vk in NUMPAD_TOKEN_TO_VK.items():
        combo = combo.replace(token, vk)
    return "<107>" if combo == "+" else combo
def _hotkey_variants(combo):
    combo = _normalize_hotkey(combo)
    if not combo:
        return []
    out, parts = [combo], combo.split("+")
    vk = NUMPAD_VK_BY_PRIMARY_KEY.get(parts[-1]) if parts else None
    if vk:
        alt = "+".join(parts[:-1] + [vk])
        if alt not in out:
            out.append(alt)
    return out
def _normalize_hex_color(value, default):
    raw = str(value or "").strip()
    if len(raw) == 7 and raw.startswith("#"):
        try:
            int(raw[1:], 16)
            return f"#{raw[1:].lower()}"
        except Exception:
            pass
    return default
def _normalize_optional_hex_color(v):
    return "" if not str(v or "").strip() else _normalize_hex_color(v, "")
def _normalize_opacity(v, default=-1):
    try:
        v = int(v)
    except Exception:
        return default
    return v if -1 <= v <= 100 else default
def _normalize_font(v, default, lo=10, hi=120):
    try:
        v = int(v)
    except Exception:
        v = default
    return max(lo, min(hi, v))
def _normalize_grade_mode(v, default="flip_only"):
    return str(v or default).strip().lower() if str(v or default).strip().lower() in {"ignore", "flip_only", "reveal_then_grade"} else default
def _normalize_curve(v, default="quad"):
    return str(v or default).strip().lower() if str(v or default).strip().lower() in {"linear", "quad", "cubic"} else default
def _normalize_replay_reset_mode(v, default="partial"):
    return str(v or default).strip().lower() if str(v or default).strip().lower() in {"none", "partial", "full"} else default
def _normalize_deck_map(entry):
    if not isinstance(entry, dict):
        return None
    out = {"deck_id": entry.get("deck_id"), "deck": entry.get("deck", "")}
    for _, key in DECK_MAP_FIELDS:
        value = entry.get(key) or entry.get(LEGACY_FIELD_MAP.get(key, ""), "") or ""
        out[key] = value
    return out
def _normalize_deck_theme(entry):
    if not isinstance(entry, dict):
        return None
    mode = str(entry.get("mode", "")).strip().lower()
    if mode not in THEME_MODES:
        mode = ""
    return {
        "deck_id": entry.get("deck_id"), "deck": entry.get("deck", ""), "mode": mode,
        "color_word": _normalize_optional_hex_color(entry.get("color_word")),
        "color_pitch": _normalize_optional_hex_color(entry.get("color_pitch")),
        "color_sent": _normalize_optional_hex_color(entry.get("color_sent")),
        "opacity": _normalize_opacity(entry.get("opacity", -1)),
    }
def _normalize_timing_values(conf, raw=None):
    raw = raw if isinstance(raw, dict) else None
    idle = _clamp_float(conf.get("focus_dim_idle_sec", DEFAULT_CONFIG["focus_dim_idle_sec"]), DEFAULT_CONFIG["focus_dim_idle_sec"], 0.5, 3600)
    warn = _clamp_float(conf.get("focus_dim_warning_sec", DEFAULT_CONFIG["focus_dim_warning_sec"]), DEFAULT_CONFIG["focus_dim_warning_sec"], 0.1, 3600)
    punish = _clamp_float(conf.get("focus_dim_punish_sec", DEFAULT_CONFIG["focus_dim_punish_sec"]), DEFAULT_CONFIG["focus_dim_punish_sec"], 0.1, 3600)
    lockdown = _clamp_float(conf.get("focus_dim_lockdown_sec", DEFAULT_CONFIG["focus_dim_lockdown_sec"]), DEFAULT_CONFIG["focus_dim_lockdown_sec"], 0.1, 3600)
    if raw is not None and "focus_dim_timing_model" not in raw:
        legacy_warning, legacy_punish, legacy_lock = warn, max(warn + 0.1, punish), max(punish + 0.1, lockdown)
        idle = _clamp_float(raw.get("focus_dim_idle_sec", legacy_warning), DEFAULT_CONFIG["focus_dim_idle_sec"], 0.5, 3600)
        warn = max(0.1, legacy_punish - legacy_warning)
        punish = max(0.1, legacy_lock - legacy_punish)
        lockdown = _clamp_float(raw.get("focus_dim_ramp_sec", punish), punish, 0.1, 3600)
    conf.update({
        "focus_dim_idle_sec": idle, "focus_dim_warning_sec": warn, "focus_dim_punish_sec": punish,
        "focus_dim_lockdown_sec": lockdown, "focus_dim_ramp_sec": warn, "focus_dim_timing_model": "durations_v2",
    })
class ConfigStore:
    def __init__(self):
        self.live = None
    def load(self):
        if self.live is not None:
            return copy.deepcopy(self.live)
        raw = mw.addonManager.getConfig(__name__)
        conf = copy.deepcopy(DEFAULT_CONFIG)
        if isinstance(raw, dict):
            conf.update(raw)
        conf["deck_maps"] = [m for m in (_normalize_deck_map(x) for x in conf.get("deck_maps", [])) if m]
        conf["deck_themes"] = [m for m in (_normalize_deck_theme(x) for x in conf.get("deck_themes", [])) if m]
        conf["color_word"] = _normalize_hex_color(conf.get("color_word"), DEFAULT_CONFIG["color_word"])
        conf["color_pitch"] = _normalize_hex_color(conf.get("color_pitch"), DEFAULT_CONFIG["color_pitch"])
        conf["color_sent"] = _normalize_hex_color(conf.get("color_sent"), DEFAULT_CONFIG["color_sent"])
        conf["grade_from_question_mode"] = _normalize_grade_mode(conf.get("grade_from_question_mode"))
        conf["focus_dim_curve"] = _normalize_curve(conf.get("focus_dim_curve"))
        conf["focus_dim_replay_reset_mode"] = _normalize_replay_reset_mode(conf.get("focus_dim_replay_reset_mode"))
        _normalize_timing_values(conf, raw)
        self.live = conf
        return copy.deepcopy(conf)
    def view(self):
        if self.live is None:
            self.load()
        return self.live
    def save(self, conf):
        conf = copy.deepcopy(conf)
        conf["deck_maps"] = [m for m in (_normalize_deck_map(x) for x in conf.get("deck_maps", [])) if m]
        conf["deck_themes"] = [m for m in (_normalize_deck_theme(x) for x in conf.get("deck_themes", [])) if m]
        conf["color_word"] = _normalize_hex_color(conf.get("color_word"), DEFAULT_CONFIG["color_word"])
        conf["color_pitch"] = _normalize_hex_color(conf.get("color_pitch"), DEFAULT_CONFIG["color_pitch"])
        conf["color_sent"] = _normalize_hex_color(conf.get("color_sent"), DEFAULT_CONFIG["color_sent"])
        conf["grade_from_question_mode"] = _normalize_grade_mode(conf.get("grade_from_question_mode"))
        conf["focus_dim_curve"] = _normalize_curve(conf.get("focus_dim_curve"))
        conf["focus_dim_replay_reset_mode"] = _normalize_replay_reset_mode(conf.get("focus_dim_replay_reset_mode"))
        _normalize_timing_values(conf)
        self.live = conf
        mw.addonManager.writeConfig(__name__, conf)
CFG = ConfigStore()
get_config = CFG.load
save_config = CFG.save
class ReviewUiState(Enum):
    IDLE = "idle"
    QUESTION = "question"
    ANSWER = "answer"
    TRANSITIONING = "transitioning"
@dataclass
class TransitionState:
    review_state: ReviewUiState = ReviewUiState.IDLE
    last_card_id: int | None = None
    pending_command: str | None = None
    pending_card_id: int | None = None
    pending_started_at: float = 0.0
    pending_source_state: str = ReviewUiState.IDLE.value
    pending_reveal_then_grade: dict | None = None
    queued_command: str | None = None
    queued_card_id: int | None = None
    queued_at: float = 0.0
    last_command_time: dict = field(default_factory=dict)
    last_hotkey_captured: str = ""
    last_command_attempted: str = ""
    last_command_result: str = ""
    def record(self, command, result):
        self.last_command_attempted, self.last_command_result = command, result
        _log(f"{command}: {result}")
    def current_card_id(self):
        try:
            return mw.reviewer.card.id if mw.state == "review" and getattr(mw, "reviewer", None) and mw.reviewer.card else None
        except Exception:
            return None
    def derive(self):
        try:
            if mw.state != "review" or not getattr(mw, "reviewer", None) or not mw.reviewer.card:
                return ReviewUiState.IDLE
            return ReviewUiState.QUESTION if mw.reviewer.state == "question" else ReviewUiState.ANSWER if mw.reviewer.state == "answer" else ReviewUiState.IDLE
        except Exception:
            return ReviewUiState.IDLE
    def sync(self):
        derived = self.derive()
        self.last_card_id = self.current_card_id()
        if self.pending_command and derived != ReviewUiState.IDLE and self.pending_started_at and _now() - self.pending_started_at > PENDING_TIMEOUT_SEC:
            cmd = self.pending_reveal_then_grade.get("command") if self.pending_command == "reveal_then_grade" and self.pending_reveal_then_grade else self.pending_command
            self.record(cmd, "error: transition timeout")
            self.clear(clear_reveal=True, allow_queued=False)
            self.review_state = derived
            return
        if self.pending_command == "flip" and self.pending_source_state == ReviewUiState.QUESTION.value and derived == ReviewUiState.ANSWER:
            self.record("flip", "ok: question->answer")
            self.clear()
            return
        if self.pending_command in {"again", "hard", "good", "easy"} and self.pending_source_state == ReviewUiState.ANSWER.value and derived == ReviewUiState.QUESTION:
            self.record(self.pending_command, "ok")
            self.clear()
            return
        if self.pending_command == "undo":
            if self.pending_source_state == ReviewUiState.ANSWER.value and derived == ReviewUiState.QUESTION:
                self.record("undo", "ok")
                self.clear(); return
            if self.pending_source_state == ReviewUiState.QUESTION.value and derived == ReviewUiState.ANSWER:
                self.record("undo", "ok: question->answer")
                self.clear(); return
            if self.pending_source_state == ReviewUiState.QUESTION.value and derived == ReviewUiState.QUESTION and self.pending_card_id and self.last_card_id and self.pending_card_id != self.last_card_id:
                self.record("undo", "ok: question->previous")
                self.clear(); return
        if self.pending_command == "reveal_then_grade" and derived == ReviewUiState.ANSWER and self.pending_reveal_then_grade:
            exp = self.pending_reveal_then_grade.get("card_id")
            if exp is None or exp == self.last_card_id:
                return
        if derived == ReviewUiState.IDLE and self.pending_command:
            cmd = self.pending_reveal_then_grade.get("command") if self.pending_command == "reveal_then_grade" and self.pending_reveal_then_grade else self.pending_command
            self.record(cmd, "cancelled: reviewer left review")
            self.clear(clear_reveal=True, allow_queued=False)
        self.review_state = ReviewUiState.TRANSITIONING if self.pending_command and derived != ReviewUiState.IDLE else derived
    def begin(self, command, card_id=None, source_state=None):
        self.pending_command = command
        self.pending_card_id = self.current_card_id() if card_id is None else card_id
        self.pending_started_at = _now()
        self.pending_source_state = source_state or self.derive().value
        self.review_state = ReviewUiState.TRANSITIONING
    def clear(self, clear_reveal=False, allow_queued=True):
        self.pending_command = None
        self.pending_card_id = None
        self.pending_started_at = 0.0
        self.pending_source_state = ReviewUiState.IDLE.value
        if clear_reveal:
            self.pending_reveal_then_grade = None
        self.review_state = self.derive()
        if allow_queued:
            APP.dispatch_queued_command()
        else:
            self.queued_command = None
            self.queued_card_id = None
            self.queued_at = 0.0
    def queue(self, command):
        if command not in {"flip", "again", "hard", "good", "easy", "undo", "replay"}:
            return False
        self.queued_command, self.queued_card_id, self.queued_at = command, self.current_card_id(), _now()
        return True
    def take_queued(self):
        q = (self.queued_command, self.queued_card_id, self.queued_at)
        self.queued_command = self.queued_card_id = None
        self.queued_at = 0.0
        return q
    def debounced(self, command):
        now, last = _now(), self.last_command_time.get(command, 0.0)
        if now - last < COMMAND_DEBOUNCE_SEC.get(command, 0.15):
            return True
        self.last_command_time[command] = now
        return False
class MainWindowEventFilter(QObject):
    WATCHED = {QEvent.Type.Show, QEvent.Type.Hide, QEvent.Type.WindowStateChange, QEvent.Type.ActivationChange, QEvent.Type.Move, QEvent.Type.Resize}
    def eventFilter(self, obj, event):
        if event.type() in self.WATCHED:
            APP.request_visibility_reconcile("main_window_event")
        return False
class AudioController:
    def __init__(self):
        self.grade_players, self.grade_outputs = {}, {}
        self.grade_last_command = self.grade_last_source = ""
        self.grade_last_played_at = 0.0
        self.pay_player = self.pay_output = self.pay_timer = None
        self.pay_sound_path = ""
        self.pay_active = False
        self.pay_warning_issued = False
    def _media_url(self, path):
        return QUrl.fromLocalFile(path)
    def _setup_player(self, player, path):
        url = self._media_url(path)
        if hasattr(player, "setSource"):
            player.setSource(url)
        elif hasattr(player, "setMedia"):
            player.setMedia(url)
    def _create_player(self, path):
        if QMediaPlayer is None or not path or not os.path.exists(path):
            return None, None
        player = QMediaPlayer(mw)
        output = None
        if QAudioOutput is not None and hasattr(player, "setAudioOutput"):
            output = QAudioOutput(mw)
            output.setVolume(1.0)
            player.setAudioOutput(output)
        elif hasattr(player, "setVolume"):
            player.setVolume(100)
        self._setup_player(player, path)
        return player, output
    def init_grade_sounds(self):
        media_dir = ""
        try:
            media_dir = mw.col.media.dir() if getattr(mw, "col", None) else ""
        except Exception:
            pass
        if not media_dir:
            return
        addon_dir = os.path.dirname(__file__)
        for kind, name in GRADE_SOUND_FILES.items():
            src, dst = os.path.join(addon_dir, name), os.path.join(media_dir, name)
            if os.path.exists(src) and not os.path.exists(dst):
                try:
                    import shutil
                    shutil.copy2(src, dst)
                except Exception:
                    pass
            path = dst if os.path.exists(dst) else src if os.path.exists(src) else ""
            if path:
                try:
                    self.grade_players[kind], self.grade_outputs[kind] = self._create_player(path)
                except Exception as exc:
                    _log(f"Grade sound init failed ({kind}): {exc}")
    def play_grade(self, command, source="hook"):
        if not APP.runtime_enabled:
            return
        kind = GRADE_SOUND_BY_COMMAND.get(command)
        player = self.grade_players.get(kind)
        if not player:
            return
        now = _now()
        if source == "hook" and self.grade_last_source == "hotkey" and self.grade_last_command == command and now - self.grade_last_played_at < 0.45:
            return
        try:
            player.stop()
            if hasattr(player, "setPosition"):
                player.setPosition(0)
            player.play()
            self.grade_last_command, self.grade_last_source, self.grade_last_played_at = command, source, now
        except Exception as exc:
            _log(f"Grade sound playback failed ({command}): {exc}")
    def warn_pay_attention_unavailable(self, reason):
        if self.pay_warning_issued:
            return
        self.pay_warning_issued = True
        _log(f"Pay-attention audio unavailable: {reason}")
        try:
            tooltip("Focus-dim warning sound is unavailable. Check pay_attention.mp3 and QtMultimedia.", period=5500)
        except Exception:
            pass
    def resolve_pay_attention_sound_path(self):
        if self.pay_sound_path and os.path.exists(self.pay_sound_path):
            return self.pay_sound_path
        paths = []
        try:
            media_dir = mw.col.media.dir() if getattr(mw, "col", None) else ""
        except Exception:
            media_dir = ""
        if media_dir:
            paths.append(os.path.join(media_dir, PAY_ATTENTION_SOUND_FILE))
        paths.append(os.path.join(os.path.dirname(__file__), PAY_ATTENTION_SOUND_FILE))
        for path in paths:
            if path and os.path.exists(path):
                self.pay_sound_path = path
                return path
        self.pay_sound_path = paths[0] if paths else ""
        return ""
    def ensure_pay_player(self):
        if self.pay_player is not None:
            return True
        if QMediaPlayer is None:
            self.warn_pay_attention_unavailable("QtMultimedia not available")
            return False
        path = self.resolve_pay_attention_sound_path()
        if not path or not os.path.exists(path):
            self.warn_pay_attention_unavailable("pay_attention.mp3 not found")
            return False
        try:
            self.pay_player, self.pay_output = self._create_player(path)
            if self.pay_player is None:
                raise RuntimeError("player unavailable")
            return True
        except Exception as exc:
            self.warn_pay_attention_unavailable(f"player init failed: {exc}")
            self.pay_player = self.pay_output = None
            return False
    def play_pay_attention(self):
        if not self.pay_active or not self.ensure_pay_player():
            return
        try:
            self.pay_player.stop()
            if hasattr(self.pay_player, "setPosition"):
                self.pay_player.setPosition(0)
            self.pay_player.play()
        except Exception as exc:
            _log(f"Pay-attention playback failed: {exc}")
            self.set_pay_attention(False)
    def on_pay_timeout(self):
        if self.pay_active:
            self.play_pay_attention()
        elif self.pay_timer and self.pay_timer.isActive():
            self.pay_timer.stop()
    def set_pay_attention(self, active):
        active = bool(active and APP.runtime_enabled)
        if not active:
            self.pay_active = False
            if self.pay_timer and self.pay_timer.isActive():
                self.pay_timer.stop()
            if self.pay_player:
                try:
                    self.pay_player.stop()
                except Exception:
                    pass
            return
        if not self.ensure_pay_player():
            self.pay_active = False
            return
        was_active = self.pay_active
        self.pay_active = True
        if self.pay_timer is None:
            self.pay_timer = QTimer(mw)
            self.pay_timer.setInterval(PAY_ATTENTION_INTERVAL_MS)
            self.pay_timer.timeout.connect(self.on_pay_timeout)
        if not self.pay_timer.isActive():
            self.pay_timer.start()
        if not was_active:
            self.play_pay_attention()
    def clear(self, full_release=False):
        self.set_pay_attention(False)
        for p in self.grade_players.values():
            try: p.stop()
            except Exception: pass
        if not full_release:
            return
        if self.pay_timer:
            try: self.pay_timer.stop(); self.pay_timer.deleteLater()
            except Exception: pass
        if self.pay_player:
            try: self.pay_player.stop(); self.pay_player.deleteLater()
            except Exception: pass
        if self.pay_output:
            try: self.pay_output.deleteLater()
            except Exception: pass
        self.pay_timer = self.pay_player = self.pay_output = None
        self.pay_sound_path = ""
        self.pay_warning_issued = False
class FocusDimOverlay(QWidget):
    def __init__(self, screen):
        super().__init__(None)
        self._screen = screen
        self._opacity_percent = 0.0
        self._phase = "idle"
        self._stage_progress = 0.0
        self._warning_text = self._warning_subtext = ""
        self._show_message = False
        self._warning_style = "pulse"
        self._warning_font_px = 30
        self._safe_rect_global = QRect()
        self._safe_feather = 20
        self._anim_time = 0.0
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus if hasattr(Qt, "FocusPolicy") else Qt.NoFocus)
        flags = _qt_window_flag("WindowStaysOnTopHint") | _qt_window_flag("FramelessWindowHint") | _qt_window_flag("Tool")
        flags |= _qt_window_flag("WindowTransparentForInput") | _qt_window_flag("WindowDoesNotAcceptFocus")
        self.setWindowFlags(flags)
        self.sync_geometry(); self.hide()
    def sync_geometry(self):
        if self._screen:
            self.setGeometry(self._screen.geometry())
    def apply_dim(self, opacity_percent, phase, stage_progress, warning_text, warning_subtext, show_message, warning_style, warning_font_px, safe_rect_global, safe_feather, anim_time):
        self._opacity_percent = max(0.0, min(100.0, float(opacity_percent)))
        self._phase = str(phase or "idle")
        self._stage_progress = max(0.0, min(1.0, float(stage_progress)))
        self._warning_text = str(warning_text or "")
        self._warning_subtext = str(warning_subtext or "")
        self._show_message = bool(show_message)
        self._warning_style = str(warning_style or "pulse").strip().lower()
        self._warning_font_px = max(14, min(84, int(warning_font_px)))
        self._safe_rect_global = QRect(safe_rect_global) if isinstance(safe_rect_global, QRect) else QRect()
        self._safe_feather = max(0, int(safe_feather))
        self._anim_time = float(anim_time)
        if self._opacity_percent <= 0.01 and not self._show_message:
            self.hide(); return
        self.sync_geometry()
        self.show(); self.raise_(); self.update()
    def clear_dim(self):
        self._opacity_percent = 0.0; self._phase = "idle"; self._stage_progress = 0.0; self._warning_text = self._warning_subtext = ""; self._show_message = False; self._safe_rect_global = QRect(); self.hide(); self.update()
    def _safe_rect_local(self):
        if self._safe_rect_global.isNull() or not self._safe_rect_global.isValid():
            return QRect()
        local = QRect(self._safe_rect_global)
        g = self.geometry(); local.translate(-g.x(), -g.y())
        local = local.intersected(self.rect())
        return local if local.width() >= 8 and local.height() >= 8 else QRect()
    def _draw_warning(self, painter):
        if not self._show_message:
            return
        pulse = 0.5 + 0.5 * math.sin(self._anim_time * 8.0)
        jitter = int(round(4 * pulse * self._stage_progress)) if self._warning_style == "shake_glow" else 0
        base_rect = self.rect().adjusted(40, 40, -40, -40).translated(jitter, 0)
        title_rect = QRect(base_rect.x(), int(base_rect.y() + base_rect.height() * 0.28), base_rect.width(), 80)
        sub_rect = QRect(base_rect.x(), title_rect.bottom() + 8, base_rect.width(), 50)
        painter.setPen(QPen(QColor(255, 255, 255, 230)))
        font = painter.font(); font.setBold(True); font.setPixelSize(self._warning_font_px); painter.setFont(font)
        if self._warning_style in {"shake_glow", "pulse"}:
            for spread in range(4, 0, -1):
                glow = QColor(255, 80, 80, int((38 + 20 * pulse) / spread))
                painter.setPen(QPen(glow, float(2 * spread)))
                painter.drawText(title_rect, ALIGN_CENTER, self._warning_text)
        painter.setPen(QPen(QColor(255, 255, 255, 245)))
        painter.drawText(title_rect, ALIGN_CENTER, self._warning_text)
        if self._warning_subtext:
            font2 = painter.font(); font2.setBold(False); font2.setPixelSize(max(14, self._warning_font_px - 10)); painter.setFont(font2)
            painter.setPen(QPen(QColor(255, 255, 255, 210)))
            painter.drawText(sub_rect, ALIGN_CENTER, self._warning_subtext)
    def paintEvent(self, event):
        super().paintEvent(event)
        if self._opacity_percent <= 0.01 and not self._show_message:
            return
        p = QPainter(self)
        try: p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        except Exception: p.setRenderHint(QPainter.Antialiasing, True)
        alpha = int(max(0, min(255, round(self._opacity_percent * 2.55))))
        p.fillRect(self.rect(), QColor(0, 0, 0, alpha))
        safe = self._safe_rect_local()
        if not safe.isNull():
            p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear if hasattr(QPainter, 'CompositionMode') else QPainter.CompositionMode_Clear)
            p.setBrush(QColor(0, 0, 0, 0)); p.setPen(Qt.PenStyle.NoPen if hasattr(Qt, 'PenStyle') else Qt.NoPen)
            p.drawRoundedRect(safe, 16, 16)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver if hasattr(QPainter, 'CompositionMode') else QPainter.CompositionMode_SourceOver)
        self._draw_warning(p)
class OverlayAlarmLayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._intensity = self._stage_progress = self._anim_time = 0.0
        self._phase = "idle"; self._pop_until = 0.0; self.hide()
    def set_state(self, intensity, phase, stage_progress, anim_time):
        phase = str(phase or "idle")
        intensity, stage_progress, anim_time = max(0.0, min(1.0, float(intensity))), max(0.0, min(1.0, float(stage_progress))), float(anim_time)
        if phase == "lockdown" and self._phase != "lockdown":
            self._pop_until = anim_time + 0.22
        changed = abs(self._intensity - intensity) > 0.01 or self._phase != phase or abs(self._stage_progress - stage_progress) > 0.01
        self._intensity, self._phase, self._stage_progress, self._anim_time = intensity, phase, stage_progress, anim_time
        if self._intensity <= 0.01:
            self.hide(); return
        self.show()
        if changed: self.update()
    def paintEvent(self, event):
        super().paintEvent(event)
        if self._intensity <= 0.01: return
        p = QPainter(self)
        try: p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        except Exception: p.setRenderHint(QPainter.Antialiasing, True)
        pulse, pop = 0.5 + 0.5 * math.sin(self._anim_time * 9.0), 1.0 + (0.02 * ((self._pop_until - self._anim_time) / 0.22)) if self._anim_time < self._pop_until else 1.0
        base = QColor(255,215,90,255) if self._phase == "warning" else QColor(255,130,65,255) if self._phase == "punish" else QColor(255,78,72,255)
        rect = self.rect().adjusted(6, 6, -6, -6)
        if pop > 1.0:
            grow = int((pop - 1.0) * 120.0); rect = rect.adjusted(-grow, -grow, grow, grow)
        for i in range(4, 0, -1):
            spread = i * 3; alpha = int((18 + 55 * pulse) * self._intensity * (1 + i * 0.18))
            pen = QPen(QColor(base.red(), base.green(), base.blue(), max(0, min(255, alpha)))); pen.setWidthF(2.0 + i * 0.8)
            p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush if hasattr(Qt, "BrushStyle") else Qt.NoBrush)
            glow_rect = rect.adjusted(-spread, -spread, spread, spread)
            p.drawRoundedRect(glow_rect, max(10.0, 18.0 + spread * 0.4), max(10.0, 18.0 + spread * 0.4))
        pen = QPen(QColor(255, 255, 255, max(40, min(255, int((125 + 110 * pulse) * self._intensity)))))
        pen.setWidthF(2.0 + 1.5 * self._intensity); p.setPen(pen); p.drawRoundedRect(rect, 18, 18)
class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        flags = _qt_window_flag("WindowStaysOnTopHint") | _qt_window_flag("FramelessWindowHint") | _qt_window_flag("Tool") | _qt_window_flag("WindowDoesNotAcceptFocus")
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        for attr in ("WA_ShowWithoutActivating", "WA_X11DoNotAcceptFocus"):
            if hasattr(Qt.WidgetAttribute, attr):
                self.setAttribute(getattr(Qt.WidgetAttribute, attr), True)
            elif hasattr(Qt, attr):
                self.setAttribute(getattr(Qt, attr), True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus if hasattr(Qt, "FocusPolicy") else Qt.NoFocus)
        self._dragging = self._resizing = False
        self._drag_offset, self._resize_start_pos, self._resize_start_size = QPoint(), QPoint(), QSize()
        self._resize_margin = 6
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        self.web_text = QWebEngineView(); self.web_text.page().setBackgroundColor(Qt.GlobalColor.transparent)
        self.web_text.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu); self.web_text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.web_text.setFocusPolicy(Qt.FocusPolicy.NoFocus if hasattr(Qt, "FocusPolicy") else Qt.NoFocus)
        layout.addWidget(self.web_text)
        self.alarm_layer = OverlayAlarmLayer(self); self.drag_handle = QLabel("Drag", self); self.resize_handle = QWidget(self)
        self.drag_handle.setAlignment(ALIGN_CENTER); self.drag_handle.setFixedSize(56, 18); self.drag_handle.setCursor(DRAG_CURSOR)
        self.drag_handle.setStyleSheet("background: rgba(255,255,255,0.14);border:1px solid rgba(255,255,255,0.2);border-radius:4px;color:rgba(255,255,255,0.85);font-size:10px;font-weight:600;")
        self.resize_handle.setFixedSize(16, 16); self.resize_handle.setCursor(RESIZE_CURSOR)
        self.resize_handle.setStyleSheet("background: rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.25);border-radius:4px;")
        self.drag_handle.installEventFilter(self); self.resize_handle.installEventFilter(self)
        self.apply_prefs(); self._position_controls(); self.show()
    def apply_prefs(self):
        conf = get_config(); self.fixed_width, self.max_def_height = conf["width"], conf["height"]
        self.move(conf["pos_x"], conf["pos_y"]); self.update_geometry()
    def update_geometry(self):
        self.web_text.setFixedHeight(self.max_def_height); self.setFixedSize(self.fixed_width, self.max_def_height); self._position_controls()
    def _position_controls(self):
        self.alarm_layer.setGeometry(self.rect()); self.alarm_layer.raise_(); self.drag_handle.move(self._resize_margin, self._resize_margin); self.drag_handle.raise_(); self.resize_handle.move(self.width() - self.resize_handle.width() - self._resize_margin, self.height() - self.resize_handle.height() - self._resize_margin); self.resize_handle.raise_()
    def _save_window_geometry(self):
        conf = get_config(); changed = False
        for k, v in {"pos_x": self.x(), "pos_y": self.y(), "width": self.width(), "height": self.height()}.items():
            if conf.get(k) != v: conf[k] = v; changed = True
        if changed: save_config(conf)
    def eventFilter(self, obj, event):
        if obj == self.resize_handle:
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == LEFT_MOUSE_BUTTON:
                self._resizing = True; self._resize_start_pos = _event_global_point(event); self._resize_start_size = self.size(); self.resize_handle.grabMouse(); return True
            if event.type() == QEvent.Type.MouseMove and self._resizing:
                delta = _event_global_point(event) - self._resize_start_pos; self.fixed_width = max(200, min(2500, self._resize_start_size.width() + delta.x())); self.max_def_height = max(100, min(2000, self._resize_start_size.height() + delta.y())); self.update_geometry(); return True
            if event.type() == QEvent.Type.MouseButtonRelease and self._resizing:
                self._resizing = False; self.resize_handle.releaseMouse(); self._save_window_geometry(); return True
        if obj == self.drag_handle:
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == LEFT_MOUSE_BUTTON:
                self._dragging = True; self._drag_offset = _event_global_point(event) - self.frameGeometry().topLeft(); self.drag_handle.grabMouse(); return True
            if event.type() == QEvent.Type.MouseMove and self._dragging:
                self.move(_event_global_point(event) - self._drag_offset); return True
            if event.type() == QEvent.Type.MouseButtonRelease and self._dragging:
                self._dragging = False; self.drag_handle.releaseMouse(); self._save_window_geometry(); return True
        return super().eventFilter(obj, event)
    def resizeEvent(self, event):
        super().resizeEvent(event); self._position_controls()
    def set_content(self, html_body, style):
        alpha, media_url = style["opacity"] / 100.0, QUrl.fromLocalFile(mw.col.media.dir() + os.path.sep).toString()
        compact = style.get("mode") == "compact"; content_class = "content-area compact" if compact else "content-area"
        css = f"""
        <style>
        html,body{{background:transparent!important;margin:0;padding:0;color:white;font-family:sans-serif;height:100%;width:100%;overflow:hidden;}}
        .box{{background:rgba(12,12,12,{alpha});border:2px solid rgba(255,255,255,.15);border-radius:18px;height:100%;box-sizing:border-box;}}
        .content-area{{width:100%;padding:16px;box-sizing:border-box;overflow-y:auto;}} .content-area.compact{{padding:10px;}}
        .main-word{{font-size:{style['font_size_word']}px;font-weight:700;color:{style['color_word']};line-height:1.1;margin-bottom:10px;text-align:center;}}
        .answer-word{{font-size:{style['font_size_translation']}px;font-weight:600;color:{style['color_pitch']};line-height:1.2;margin-bottom:16px;text-align:center;}}
        .example-pair{{margin-top:14px;padding:10px 12px;border:1px solid rgba(255,255,255,.12);border-radius:12px;background:rgba(255,255,255,.04);}}
        .content-area.compact .example-pair{{margin-top:8px;padding:8px 10px;}}
        .example-de{{font-size:{style['font_size_example']}px;color:white;margin-bottom:6px;}} .example-en{{font-size:{style['font_size_example']}px;color:{style['color_sent']};opacity:.95;}}
        .status-line{{font-size:.8em;opacity:.75;margin-top:12px;}} hr{{border:0;border-top:1px solid rgba(255,255,255,.1);margin:8px 0;width:100%;}}
        </style>"""
        self.update_geometry(); self.web_text.setHtml(f"<html><head><base href='{media_url}'>{css}</head><body><div class='box'><div class='{content_class}'>{html_body}</div></div></body></html>", QUrl.fromLocalFile(mw.col.media.dir() + os.path.sep))
    def set_focus_alarm_intensity(self, intensity, phase="idle", stage_progress=0.0, anim_time=0.0):
        self.alarm_layer.set_state(intensity, phase, stage_progress, anim_time)
class HotkeyRecorder(QPushButton):
    def __init__(self, current_key, parent=None):
        super().__init__(current_key or "None", parent)
        self.current_key = current_key; self.recording = False; self.setFixedWidth(150); self.setCheckable(True); self.clicked.connect(self.toggle_recording)
    def toggle_recording(self):
        self.recording = self.isChecked(); self.setText("... ? ..." if self.recording else self.current_key or "None")
        if self.recording: self.setFocus()
    def keyPressEvent(self, event):
        if not self.recording: return super().keyPressEvent(event)
        if event.key() in [Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta]: return
        parts, mod = [], event.modifiers()
        for bit, token in [(Qt.KeyboardModifier.ControlModifier, "<ctrl>"), (Qt.KeyboardModifier.ShiftModifier, "<shift>"), (Qt.KeyboardModifier.AltModifier, "<alt>"), (Qt.KeyboardModifier.MetaModifier, "<meta>")]:
            if mod & bit: parts.append(token)
        key_str = QKeySequence(event.key()).toString().lower()
        mapping = {"backspace":"<backspace>","del":"<delete>","ins":"<insert>","return":"<enter>","enter":"<enter>","capslock":"<caps_lock>"}
        keypad = {"0":"<num0>","1":"<num1>","2":"<num2>","3":"<num3>","4":"<num4>","5":"<num5>","6":"<num6>","7":"<num7>","8":"<num8>","9":"<num9>","*":"<num_star>","+":"<num_plus>","-":"<num_minus>",".":"<num_dot>","/":"<num_slash>"}
        parts.append((keypad if mod & Qt.KeyboardModifier.KeypadModifier else mapping).get(key_str, mapping.get(key_str, key_str)))
        self.current_key = "+".join(parts); self.setText(self.current_key); self.recording = False; self.setChecked(False)
class Runtime:
    def __init__(self):
        self.overlay = None
        self.runtime_enabled = True
        self.addon_active = False
        self.listener = None
        self.listener_sig = None
        self.listener_toggle_only = None
        self.missing_pynput_warned = False
        self.state = TransitionState()
        self.audio = AudioController()
        self.init_timer = self.refresh_timer = self.transition_watchdog = self.focus_timer = None
        self.main_window_filter = None
        self.overlay_user_hidden = False
        self.overlay_auto_hidden_by_window = False
        self.overlay_refresh_flags = {"content": False, "style": False, "visibility": False, "force": False}
        self.last_overlay_render_key = self.last_overlay_style_key = None
        self.last_external_overlay_refresh_at = 0.0
        self.dim_overlays = []
        self.focus_dim_enabled = False
        self.focus_fail_open_active = False
        self.idle_started_at = self.last_activity_at = 0.0
        self.dim_phase = "idle"
        self.dim_target_opacity = self.focus_dim_current_opacity = 0.0
        self.focus_dim_last_idle_elapsed = self.focus_dim_stage_progress = self.focus_dim_last_ramp_progress = 0.0
        self.focus_dim_last_activity_source = ""
        self.last_focus_dim_card_id = self.last_focus_dim_side = None
    def conf(self):
        return CFG.view()
    def current_card_id(self):
        return self.state.current_card_id()
    def deck_name_from_id(self, deck_id):
        try:
            deck = mw.col.decks.get(int(deck_id))
            return deck.get("name", "") if deck else ""
        except Exception:
            return ""
    def deck_map_for_card(self, conf, card):
        deck = mw.col.decks.get(card.did) or {}
        deck_name = deck.get("name", "")
        for m in conf.get("deck_maps", []):
            if not isinstance(m, dict): continue
            if m.get("deck_id") is not None:
                try:
                    if int(m.get("deck_id")) == int(card.did): return m
                except Exception:
                    pass
            if m.get("deck") == deck_name: return m
        return None
    def deck_theme_for_card(self, conf, card):
        deck = mw.col.decks.get(card.did) or {}
        deck_name = deck.get("name", "")
        for m in conf.get("deck_themes", []):
            if not isinstance(m, dict): continue
            if m.get("deck_id") is not None:
                try:
                    if int(m.get("deck_id")) == int(card.did): return m
                except Exception:
                    pass
            if m.get("deck") == deck_name: return m
        return None
    def effective_style(self, conf, deck_theme):
        style = {
            "color_word": conf.get("color_word", DEFAULT_CONFIG["color_word"]),
            "color_pitch": conf.get("color_pitch", DEFAULT_CONFIG["color_pitch"]),
            "color_sent": conf.get("color_sent", DEFAULT_CONFIG["color_sent"]),
            "opacity": int(conf.get("opacity", DEFAULT_CONFIG["opacity"])),
            "font_size_word": _normalize_font(conf.get("font_size_word", DEFAULT_CONFIG["font_size_word"]), DEFAULT_CONFIG["font_size_word"], 20, 160),
            "font_size_translation": _normalize_font(conf.get("font_size_translation", DEFAULT_CONFIG["font_size_translation"]), DEFAULT_CONFIG["font_size_translation"], 12, 120),
            "font_size_example": _normalize_font(conf.get("font_size_example", DEFAULT_CONFIG["font_size_example"]), DEFAULT_CONFIG["font_size_example"], 10, 96),
            "mode": "",
        }
        if deck_theme:
            for key in ("color_word", "color_pitch", "color_sent"):
                if deck_theme.get(key): style[key] = deck_theme[key]
            if deck_theme.get("opacity", -1) >= 0: style["opacity"] = deck_theme["opacity"]
            if deck_theme.get("mode") in {"full", "compact"}: style["mode"] = deck_theme["mode"]
        return style
    def safe_field(self, note, field_name):
        if not field_name: return ""
        try: return html.escape(str(note[field_name] or "").strip())
        except Exception: return ""
    def build_example_pair(self, de, en):
        de, en = de or "", en or ""
        if not de and not en: return ""
        return f"<div class='example-pair'>{f'<div class=\"example-de\">{de}</div>' if de else ''}{f'<div class=\"example-en\">{en}</div>' if en else ''}</div>"
    def is_main_window_minimized(self):
        try:
            if not getattr(mw, "isVisible", None) or not mw.isVisible(): return True
            return bool(int(mw.windowState()) & int(_qt_window_flag("WindowMinimized")))
        except Exception:
            return False
    def ensure_overlay_within_visible_screen(self):
        if not self.overlay: return
        app = QApplication.instance(); screens = app.screens() if app else []
        if not screens: return
        target, frame = None, self.overlay.frameGeometry()
        for s in screens:
            if s.availableGeometry().intersects(frame): target = s; break
        if target is None:
            try: target = app.screenAt(mw.frameGeometry().center()) if hasattr(app, "screenAt") else None
            except Exception: target = None
        target = target or app.primaryScreen() or screens[0]
        if not target: return
        available = target.availableGeometry(); w, h = max(1, self.overlay.width()), max(1, self.overlay.height())
        x = min(max(self.overlay.pos().x(), available.x()), available.x() + max(0, available.width() - w))
        y = min(max(self.overlay.pos().y(), available.y()), available.y() + max(0, available.height() - h))
        if (x, y) != (self.overlay.pos().x(), self.overlay.pos().y()):
            self.overlay.move(x, y); self.overlay._save_window_geometry()
    def overlay_screen_key(self):
        app = QApplication.instance(); screens = app.screens() if app else []
        if not screens: return None
        target = None
        if self.overlay:
            frame = self.overlay.frameGeometry()
            for s in screens:
                try:
                    if s.availableGeometry().intersects(frame): target = s; break
                except Exception:
                    pass
        if target is None:
            try: target = app.screenAt(mw.frameGeometry().center()) if hasattr(app, "screenAt") else None
            except Exception: target = None
        target = target or app.primaryScreen() or screens[0]
        if not target: return None
        ag = target.availableGeometry(); return (getattr(target, 'name', lambda: '')(), ag.x(), ag.y(), ag.width(), ag.height())
    def request_visibility_reconcile(self, reason="", force_show=False):
        if not self.addon_active: return
        QTimer.singleShot(0, lambda: self.reconcile_visibility(reason, force_show))
    def reconcile_visibility(self, reason="", force_show=False):
        if not self.overlay: return
        if not self.runtime_enabled:
            self.overlay.hide(); self.reset_focus(clear_overlay=True); return
        if force_show: self.overlay_user_hidden = False
        if self.is_main_window_minimized():
            if self.overlay.isVisible() and not self.overlay_user_hidden: self.overlay_auto_hidden_by_window = True
            self.overlay.hide(); self.reset_focus(clear_overlay=True); return
        if self.overlay_user_hidden:
            self.overlay_auto_hidden_by_window = False; self.overlay.hide(); self.reset_focus(clear_overlay=True); return
        self.ensure_overlay_within_visible_screen()
        if self.overlay_auto_hidden_by_window or force_show or not self.overlay.isVisible():
            self.overlay.show(); self.overlay.raise_(); self.overlay_auto_hidden_by_window = False; self.request_refresh(0, visibility=True, style=True)
        if self.focus_dim_enabled: self.focus_tick()
    def ensure_app_state_hooks(self):
        app = QApplication.instance()
        if not app: return
        if self.main_window_filter is None:
            if hasattr(app, "applicationStateChanged"):
                app.applicationStateChanged.connect(lambda *_: self.request_visibility_reconcile("app_state"))
            self.main_window_filter = MainWindowEventFilter(mw)
            try: mw.installEventFilter(self.main_window_filter)
            except Exception: pass
    def disconnect_app_state_hooks(self):
        app = QApplication.instance()
        if app and hasattr(app, "applicationStateChanged"):
            try: app.applicationStateChanged.disconnect()
            except Exception: pass
        if self.main_window_filter is not None:
            try: mw.removeEventFilter(self.main_window_filter)
            except Exception: pass
        self.main_window_filter = None
    def validate_hotkey_combo(self, combo):
        if not combo: return False
        if not HAS_PYNPUT: return True
        try: keyboard.HotKey.parse(combo); return True
        except Exception: return False
    def validate_hotkeys(self, conf):
        seen, issues, shared_flip = {}, [], []
        for key in HOTKEY_KEYS:
            label, combo = HOTKEY_LABELS[key], _normalize_hotkey(conf.get(key, ""))
            if not combo: issues.append(f"{label} is empty"); continue
            if not self.validate_hotkey_combo(combo): issues.append(f"{label} is invalid ({combo})"); continue
            for variant in _hotkey_variants(combo):
                other = seen.get(variant)
                if other is None: continue
                allow = (key == "key_flip" and other in GRADE_KEYS) or (other == "key_flip" and key in GRADE_KEYS)
                if allow:
                    grade = key if key in GRADE_KEYS else other
                    if grade not in shared_flip: shared_flip.append(grade)
                    if len(shared_flip) > 1: issues.append(f"Flip can share with only one grade key (currently {', '.join(HOTKEY_LABELS[g] for g in shared_flip)})")
                    continue
                issues.append(f"{label} duplicates {HOTKEY_LABELS[other]} ({combo})")
            for variant in _hotkey_variants(combo): seen[variant] = key
        return issues
    def _enqueue(self, command):
        def _runner():
            if not self.addon_active: return
            self.state.last_hotkey_captured = command
            mw.taskman.run_on_main(lambda: self.dispatch_command(command))
        return _runner
    def _enqueue_flip_or_grade(self, grade_command):
        def _runner():
            if not self.addon_active: return
            def _dispatch():
                self.state.sync(); command = "flip" if self.state.review_state == ReviewUiState.QUESTION else grade_command
                self.state.last_hotkey_captured = command; self.dispatch_command(command)
            mw.taskman.run_on_main(_dispatch)
        return _runner
    def stop_listener(self):
        if self.listener:
            try: self.listener.stop()
            except Exception as exc: _log(f"Listener stop failed: {exc}")
        self.listener = None; self.listener_sig = self.listener_toggle_only = None
    def start_listener(self, show_feedback=False, toggle_only=False):
        if not self.addon_active: return
        if not HAS_PYNPUT:
            if show_feedback or not self.missing_pynput_warned:
                tooltip("Overlay hotkeys unavailable: install pynput in Anki Python env.", period=4000)
            self.missing_pynput_warned = True; return
        conf, sig = get_config(), tuple((k, _normalize_hotkey(get_config().get(k, ""))) for k in HOTKEY_KEYS)
        if self.listener and sig == self.listener_sig and bool(toggle_only) == self.listener_toggle_only: return
        self.stop_listener(); toggle_combo = _normalize_hotkey(conf.get("key_toggle"))
        if toggle_only:
            if not toggle_combo or not self.validate_hotkey_combo(toggle_combo):
                if show_feedback: tooltip("Toggle hotkey is invalid; cannot keep listener while disabled.", period=4500)
                return
        else:
            issues = self.validate_hotkeys(conf)
            if issues:
                tooltip(f"Overlay hotkey config issue: {'; '.join(issues[:3])}", period=4500); return
        hotkeys, sources, runtime_issues = {}, {}, []
        def register(combo, cb, name):
            if not combo: return
            for variant in _hotkey_variants(combo):
                existing = sources.get(variant)
                if existing and existing != name:
                    runtime_issues.append(f"{variant}: {existing} vs {name}")
                    return
            for variant in _hotkey_variants(combo): hotkeys[variant] = cb; sources[variant] = name
        register(toggle_combo, self._enqueue("toggle"), "toggle")
        if not toggle_only:
            for ck, cmd in (("key_replay", "replay"), ("key_undo", "undo")): register(_normalize_hotkey(conf.get(ck)), self._enqueue(cmd), cmd)
            flip_combo, shared = _normalize_hotkey(conf.get("key_flip")), None
            for ck, cmd in (("key_again", "again"), ("key_hard", "hard"), ("key_good", "good"), ("key_easy", "easy")):
                if _normalize_hotkey(conf.get(ck)) == flip_combo: shared = cmd; break
            if flip_combo: register(flip_combo, self._enqueue_flip_or_grade(shared) if shared else self._enqueue("flip"), f"flip_or_{shared}" if shared else "flip")
            for ck, cmd in (("key_again", "again"), ("key_hard", "hard"), ("key_good", "good"), ("key_easy", "easy")):
                combo = _normalize_hotkey(conf.get(ck))
                if combo and not (combo == flip_combo and shared == cmd): register(combo, self._enqueue(cmd), cmd)
        if runtime_issues or not hotkeys:
            if runtime_issues: tooltip("Overlay hotkey runtime collision. Review bindings in settings.", period=5000)
            return
        try:
            self.listener = keyboard.GlobalHotKeys(hotkeys); self.listener.daemon = True; self.listener.start(); self.listener_sig, self.listener_toggle_only = sig, bool(toggle_only)
        except Exception as exc:
            self.listener = None; self.listener_sig = self.listener_toggle_only = None; tooltip("Overlay hotkeys failed to start. Check add-on console.", period=4500); _log(f"Hotkey listener startup failed: {exc}")
    def is_undo_available(self):
        try:
            action = getattr(getattr(mw, "form", None), "actionUndo", None)
            if action is not None and hasattr(action, "isEnabled"): return bool(action.isEnabled())
        except Exception: pass
        try:
            col = getattr(mw, "col", None)
            if col is not None and hasattr(col, "undo_status"):
                status = col.undo_status()
                if status is None: return False
                if hasattr(status, "can_undo"): return bool(status.can_undo)
                if hasattr(status, "undo"): return bool(status.undo)
                if isinstance(status, (tuple, list)) and status and isinstance(status[0], bool): return status[0]
        except Exception: pass
        return True
    def set_runtime_enabled(self, enabled, reason="toggle"):
        enabled = bool(enabled)
        if self.runtime_enabled == enabled: return
        self.runtime_enabled = enabled
        if not enabled:
            self.state.pending_command = None; self.state.pending_card_id = None; self.state.pending_reveal_then_grade = None; self.state.pending_started_at = 0.0; self.state.pending_source_state = ReviewUiState.IDLE.value; self.state.review_state = self.state.derive()
            self.clear_refresh_queue(stop_timer=True); self.state.queued_command = self.state.queued_card_id = None; self.state.queued_at = 0.0
            self.stop_transition_watchdog(); self.stop_focus_timer(); self.audio.set_pay_attention(False); self.audio.clear(full_release=False)
            self.overlay_user_hidden = True; self.reconcile_visibility(f"{reason}:disabled"); self.start_listener(toggle_only=True)
            try: tooltip("Overlay add-on disabled", period=1200)
            except Exception: pass
            return
        self.overlay_user_hidden = False; self.start_listener(toggle_only=False); self.refresh_focus_controller(force_rebuild=True); self.reconcile_visibility(f"{reason}:enabled", force_show=True); self.request_refresh(0, content=True, style=True, force=True)
        try: tooltip("Overlay add-on enabled", period=1200)
        except Exception: pass
    def toggle_runtime(self):
        self.set_runtime_enabled(not self.runtime_enabled, reason="manual_toggle")
    def dispatch_queued_command(self):
        command, queued_card_id, queued_at = self.state.take_queued()
        if not command or queued_at <= 0 or _now() - queued_at > QUEUED_TRANSITION_MAX_AGE_SEC: return
        current = self.current_card_id()
        if queued_card_id is not None and (current is None or current != queued_card_id): return
        current_state = self.state.derive()
        if command == "flip" and current_state != ReviewUiState.QUESTION: return
        if command in {"again", "hard", "good", "easy"} and current_state != ReviewUiState.ANSWER: return
        QTimer.singleShot(0, lambda: self.dispatch_command(command, skip_debounce=True) if self.addon_active else None)
    def handle_pending_reveal_then_grade(self, card_id):
        req = self.state.pending_reveal_then_grade; self.state.pending_reveal_then_grade = None
        if not req: self.state.clear(); return
        if req.get("card_id") != card_id: self.state.record(req.get("command", "reveal_then_grade"), "ignored: card changed before grade"); self.state.clear(); return
        command, ease = req.get("command"), req.get("ease")
        self.state.begin(command, card_id, ReviewUiState.ANSWER.value)
        try:
            mw.reviewer._answerCard(ease); self.state.record(command, "requested: reveal_then_grade->answered"); self.mark_review_activity(command, True); self.audio.play_grade(command, source="hotkey" if not hasattr(gui_hooks, "reviewer_did_answer_card") else "hook")
        except Exception as exc:
            self.state.record(command, f"error: {exc}"); _log(traceback.format_exc()); self.state.clear()
    def dispatch_command(self, command, skip_debounce=False):
        if not self.addon_active: self.state.record(command, "ignored: addon inactive"); return
        self.state.sync()
        if command == "toggle":
            if self.state.debounced(command): self.state.record(command, "ignored: debounced"); return
            self.toggle_runtime(); self.state.record(command, "ok"); return
        if not self.runtime_enabled: self.state.record(command, "ignored: addon toggled off"); return
        if self.state.review_state == ReviewUiState.IDLE: self.state.record(command, "ignored: not in review"); return
        if self.state.review_state == ReviewUiState.TRANSITIONING:
            self.state.record(command, f"queued: transitioning ({self.state.pending_command or 'pending'})" if self.state.queue(command) else f"ignored: transitioning ({self.state.pending_command or 'pending'})"); return
        if not skip_debounce and self.state.debounced(command): self.state.record(command, "ignored: debounced"); return
        if command == "replay":
            try: mw.reviewer.replayAudio(); self.state.record(command, "ok"); self.mark_review_activity(command, True)
            except Exception as exc: self.state.record(command, f"error: {exc}"); _log(traceback.format_exc())
            return
        if command == "undo":
            if not self.is_undo_available(): self.state.record(command, "ignored: nothing to undo"); return
            try: mw.onUndo(); self.state.record(command, "requested"); self.mark_review_activity("undo", True); self.schedule_external_refresh("undo_command")
            except Exception as exc: self.state.record(command, f"error: {exc}"); _log(traceback.format_exc())
            return
        if command == "flip":
            if self.state.review_state != ReviewUiState.QUESTION: self.state.record(command, "ignored: already on answer"); return
            try: self.state.begin("flip", self.current_card_id(), self.state.review_state.value); mw.reviewer._showAnswer(); self.state.record(command, "requested: question->answer"); self.mark_review_activity("flip", True); self.schedule_transition_followups()
            except Exception as exc: self.state.record(command, f"error: {exc}"); _log(traceback.format_exc()); self.state.clear(clear_reveal=True)
            return
        if command in {"again", "hard", "good", "easy"}:
            ease_map, card_id = {"again": 1, "hard": 2, "good": 3, "easy": 4}, self.current_card_id()
            if self.state.review_state == ReviewUiState.QUESTION:
                mode = _normalize_grade_mode(get_config().get("grade_from_question_mode", "flip_only"))
                if mode == "reveal_then_grade":
                    self.state.pending_reveal_then_grade = {"command": command, "ease": ease_map[command], "card_id": card_id}
                    try: self.state.begin("reveal_then_grade", card_id, self.state.review_state.value); mw.reviewer._showAnswer(); self.state.record(command, "requested: reveal_then_grade"); self.schedule_transition_followups()
                    except Exception as exc: self.state.record(command, f"error: {exc}"); _log(traceback.format_exc()); self.state.clear(clear_reveal=True)
                elif mode == "flip_only":
                    try: self.state.begin("flip", card_id, self.state.review_state.value); mw.reviewer._showAnswer(); self.state.record(command, "requested: flip_only(question->answer)"); self.mark_review_activity("flip", True); self.schedule_transition_followups()
                    except Exception as exc: self.state.record(command, f"error: {exc}"); _log(traceback.format_exc()); self.state.clear(clear_reveal=True)
                else:
                    self.state.record(command, "ignored: grading on question side")
                return
            if self.state.review_state != ReviewUiState.ANSWER: self.state.record(command, f"ignored: invalid state {self.state.review_state.value}"); return
            try: self.state.begin(command, card_id, self.state.review_state.value); mw.reviewer._answerCard(ease_map[command]); self.state.record(command, f"requested: answered {command}"); self.mark_review_activity(command, True); self.schedule_transition_followups();
            except Exception as exc: self.state.record(command, f"error: {exc}"); _log(traceback.format_exc()); self.state.clear(clear_reveal=True)
            if not hasattr(gui_hooks, "reviewer_did_answer_card"):
                self.audio.play_grade(command, source="hotkey")
            return
        self.state.record(command, "ignored: unknown command")
    def schedule_transition_followups(self):
        self.ensure_transition_watchdog()
        for delay in (0, 60, 180, 420):
            QTimer.singleShot(delay, lambda: self.request_refresh(0, content=True, style=True))
    def schedule_external_refresh(self, reason=""):
        now = _now()
        if now - self.last_external_overlay_refresh_at < 0.08: return
        self.last_external_overlay_refresh_at = now
        for delay in (0, 60, 180, 420):
            QTimer.singleShot(delay, lambda: self.request_refresh(0, content=True, style=True, force=True))
    def transition_snapshot(self):
        reviewer_state = None
        try: reviewer_state = getattr(getattr(mw, "reviewer", None), "state", None)
        except Exception: pass
        return (mw.state, reviewer_state, self.current_card_id(), self.state.pending_command, self.state.review_state.value)
    def ensure_transition_watchdog(self):
        if self.transition_watchdog is None:
            self.transition_watchdog = QTimer(mw); self.transition_watchdog.setInterval(TRANSITION_WATCHDOG_MS); self.transition_watchdog.timeout.connect(self.transition_watchdog_tick)
        if not self.transition_watchdog.isActive(): self.transition_watchdog.start()
    def stop_transition_watchdog(self):
        if self.transition_watchdog and self.transition_watchdog.isActive(): self.transition_watchdog.stop()
    def transition_watchdog_tick(self):
        if not self.state.pending_command:
            self.stop_transition_watchdog(); return
        before = self.transition_snapshot(); self.state.sync(); after = self.transition_snapshot()
        if before != after or self.state.pending_command:
            self.request_refresh(0, content=True, style=True)
        if self.state.pending_command == "reveal_then_grade" and self.state.derive() == ReviewUiState.ANSWER and self.state.pending_reveal_then_grade:
            exp = self.state.pending_reveal_then_grade.get("card_id")
            if exp is None or exp == self.current_card_id():
                self.handle_pending_reveal_then_grade(self.current_card_id())
        if not self.state.pending_command:
            self.stop_transition_watchdog()
    def request_refresh(self, delay_ms=0, content=False, style=False, visibility=False, force=False):
        self.overlay_refresh_flags["content"] |= bool(content)
        self.overlay_refresh_flags["style"] |= bool(style)
        self.overlay_refresh_flags["visibility"] |= bool(visibility)
        self.overlay_refresh_flags["force"] |= bool(force)
        if self.refresh_timer is None:
            self.refresh_timer = QTimer(mw); self.refresh_timer.setSingleShot(True); self.refresh_timer.timeout.connect(self.run_refresh_request)
        if not self.refresh_timer.isActive() or delay_ms <= 0:
            self.refresh_timer.start(max(0, int(delay_ms)))
    def clear_refresh_queue(self, stop_timer=False):
        if stop_timer and self.refresh_timer and self.refresh_timer.isActive(): self.refresh_timer.stop()
        self.overlay_refresh_flags = {"content": False, "style": False, "visibility": False, "force": False}
    def compute_overlay_render_key(self):
        conf, card_id, derived = self.conf(), self.current_card_id(), self.state.derive().value
        active_deck_id = mapped_sig = theme_sig = None
        try:
            if mw.state == "review" and getattr(mw, "reviewer", None) and mw.reviewer.card:
                card = mw.reviewer.card; active_deck_id = getattr(card, "did", None)
                deck_cfg = self.deck_map_for_card(conf, card)
                if deck_cfg: mapped_sig = tuple(deck_cfg.get(k, "") for _, k in DECK_MAP_FIELDS)
                deck_theme = self.deck_theme_for_card(conf, card); style = self.effective_style(conf, deck_theme)
                theme_sig = tuple(style.get(k) for k in ("color_word", "color_pitch", "color_sent", "opacity", "font_size_word", "font_size_translation", "font_size_example", "mode"))
        except Exception: pass
        return (card_id, derived, self.runtime_enabled, self.overlay_user_hidden, bool(conf.get("debug_status", False)), active_deck_id, mapped_sig, theme_sig)
    def compute_overlay_style_key(self):
        conf = self.conf()
        return (bool(conf.get("focus_dim_enabled", False)), self.dim_phase, round(self.dim_target_opacity, 3), round(self.focus_dim_current_opacity, 3), self.overlay_auto_hidden_by_window)
    def refresh_overlay_content(self):
        if not self.overlay or not self.runtime_enabled: return False
        self.state.sync(); conf = self.conf()
        if mw.state != "review" or not getattr(mw, "reviewer", None) or not mw.reviewer.card:
            self.overlay.set_content("<div class='main-word' style='opacity:0.3;'>Standby</div>", self.effective_style(conf, None)); return True
        card, note = mw.reviewer.card, mw.reviewer.card.note(); deck_cfg = self.deck_map_for_card(conf, card); style = self.effective_style(conf, self.deck_theme_for_card(conf, card))
        if not deck_cfg:
            self.overlay.set_content("<div class='main-word' style='opacity:0.3;'>Deck Not Mapped</div>", style); return True
        is_ans = mw.reviewer.state == "answer"
        gw = self.safe_field(note, deck_cfg.get("german_word")); ew = self.safe_field(note, deck_cfg.get("english_word")) if is_ans else ""
        g1 = self.safe_field(note, deck_cfg.get("german_example_1")); e1 = self.safe_field(note, deck_cfg.get("english_example_1")) if is_ans else ""
        g2 = self.safe_field(note, deck_cfg.get("german_example_2")) if is_ans else ""; e2 = self.safe_field(note, deck_cfg.get("english_example_2")) if is_ans else ""
        g3 = self.safe_field(note, deck_cfg.get("german_example_3")) if is_ans else ""; e3 = self.safe_field(note, deck_cfg.get("english_example_3")) if is_ans else ""
        body = f"<div class='main-word'>{gw or 'No German Word'}</div>{f'<div class=\"answer-word\">{ew}</div>' if is_ans else ''}{self.build_example_pair(g1, e1 if is_ans else '')}{self.build_example_pair(g2, e2)}{self.build_example_pair(g3, e3)}"
        if conf.get("debug_status"):
            dim_visible = any(d.isVisible() for d in self.dim_overlays)
            body += f"<hr><div class='status-line'>state={self.state.review_state.value} | last={html.escape(str(self.state.last_command_attempted))} | result={html.escape(str(self.state.last_command_result))}<br>dim_enabled={str(bool(conf.get('focus_dim_enabled', False))).lower()} | dim_phase={self.dim_phase} | idle_elapsed={self.focus_dim_last_idle_elapsed:.2f}s | stage={self.focus_dim_stage_progress:.2f} | dim_opacity={self.focus_dim_current_opacity:.1f} | dim_shown={str(dim_visible).lower()} | dim_source={html.escape(str(self.focus_dim_last_activity_source))}</div>"
        self.overlay.set_content(body, style); return True
    def current_overlay_global_rect(self):
        if not self.overlay or not self.overlay.isVisible(): return QRect()
        g = self.overlay.frameGeometry(); return QRect(g.x(), g.y(), self.overlay.width(), self.overlay.height())
    def focus_alarm_intensity(self, phase, progress):
        if phase == "warning": return 0.12 + 0.18 * progress
        if phase == "punish": return 0.35 + 0.45 * progress
        if phase == "lockdown": return 0.85 + 0.15 * progress
        return 0.0
    def rebuild_focus_overlays(self):
        for d in self.dim_overlays:
            try: d.hide(); d.deleteLater()
            except Exception: pass
        self.dim_overlays = []
        app = QApplication.instance(); screens = app.screens() if app else []
        for screen in screens or []:
            self.dim_overlays.append(FocusDimOverlay(screen))
    def ensure_focus_timer(self):
        if self.focus_timer is None:
            self.focus_timer = QTimer(mw); self.focus_timer.setInterval(FOCUS_DIM_TICK_MS); self.focus_timer.timeout.connect(self.focus_tick)
        if not self.focus_timer.isActive(): self.focus_timer.start()
    def stop_focus_timer(self):
        if self.focus_timer and self.focus_timer.isActive(): self.focus_timer.stop()
    def reset_focus(self, clear_overlay=False):
        self.idle_started_at = self.last_activity_at = 0.0; self.dim_phase = "idle"; self.dim_target_opacity = self.focus_dim_current_opacity = 0.0; self.focus_dim_last_idle_elapsed = self.focus_dim_stage_progress = self.focus_dim_last_ramp_progress = 0.0; self.focus_dim_last_activity_source = ""; self.last_focus_dim_card_id = self.last_focus_dim_side = None; self.audio.set_pay_attention(False)
        if clear_overlay:
            for d in self.dim_overlays:
                try: d.clear_dim()
                except Exception: pass
            if self.overlay:
                try: self.overlay.set_focus_alarm_intensity(0.0, "idle", 0.0, _now())
                except Exception: pass
    def focus_fail_open(self, reason, exc=None):
        if self.focus_fail_open_active: return
        self.focus_fail_open_active = True
        try:
            _log(f"Focus-dim fail-open ({reason}{': ' + str(exc) if exc else ''})")
            self.focus_dim_enabled = False; self.dim_phase = "idle"; self.dim_target_opacity = 0.0
            try:
                conf = get_config()
                if conf.get("focus_dim_enabled", False): conf["focus_dim_enabled"] = False; save_config(conf)
            except Exception: pass
            self.stop_focus_timer(); self.audio.set_pay_attention(False)
            for d in self.dim_overlays:
                try: d.clear_dim()
                except Exception: pass
            if self.overlay:
                try: self.overlay.set_focus_alarm_intensity(0.0, "idle", 0.0, _now())
                except Exception: pass
            try: tooltip("Focus dim disabled after runtime error. Open settings to re-enable.", period=5000)
            except Exception: pass
        finally:
            self.focus_fail_open_active = False
    def is_review_active_for_dim(self, conf):
        try:
            if mw.state != "review" or not getattr(mw, "reviewer", None) or not mw.reviewer.card: return False
            if conf.get("focus_dim_question_only", False) and mw.reviewer.state != "question": return False
            return True
        except Exception:
            return False
    def sync_focus_baseline_for_card(self):
        card_id, side = self.current_card_id(), self.state.derive().value
        if card_id != self.last_focus_dim_card_id or side != self.last_focus_dim_side:
            self.last_focus_dim_card_id, self.last_focus_dim_side = card_id, side
            self.last_activity_at = _now(); self.idle_started_at = self.last_activity_at; self.dim_phase = "idle"; self.dim_target_opacity = 0.0; self.focus_dim_stage_progress = self.focus_dim_last_ramp_progress = self.focus_dim_last_idle_elapsed = 0.0
    def compute_focus_stage(self, conf, idle_elapsed):
        idle = conf.get("focus_dim_idle_sec", DEFAULT_CONFIG["focus_dim_idle_sec"])
        warn_dur = conf.get("focus_dim_warning_sec", DEFAULT_CONFIG["focus_dim_warning_sec"])
        punish_dur = conf.get("focus_dim_punish_sec", DEFAULT_CONFIG["focus_dim_punish_sec"])
        lock_dur = conf.get("focus_dim_lockdown_sec", DEFAULT_CONFIG["focus_dim_lockdown_sec"])
        warn_op = _clamp_float(conf.get("focus_dim_warning_opacity", DEFAULT_CONFIG["focus_dim_warning_opacity"]), DEFAULT_CONFIG["focus_dim_warning_opacity"], 0, 100)
        punish_op = max(warn_op, _clamp_float(conf.get("focus_dim_punish_opacity", DEFAULT_CONFIG["focus_dim_punish_opacity"]), DEFAULT_CONFIG["focus_dim_punish_opacity"], 0, 100))
        max_op = max(punish_op, _clamp_float(conf.get("focus_dim_max_opacity", DEFAULT_CONFIG["focus_dim_max_opacity"]), DEFAULT_CONFIG["focus_dim_max_opacity"], 0, 100))
        curve = _normalize_curve(conf.get("focus_dim_curve", DEFAULT_CONFIG["focus_dim_curve"]))
        if idle_elapsed <= idle: return "idle", 0.0, 0.0
        t = idle_elapsed - idle
        if t <= warn_dur:
            p = _curve_value(t / max(0.1, warn_dur), curve); return "warning", p, warn_op * p
        t -= warn_dur
        if t <= punish_dur:
            p = _curve_value(t / max(0.1, punish_dur), curve); return "punish", p, warn_op + (punish_op - warn_op) * p
        t -= punish_dur
        if t <= lock_dur:
            p = _curve_value(t / max(0.1, lock_dur), curve); return "lockdown", p, punish_op + (max_op - punish_op) * p
        return "lockdown", 1.0, max_op
    def advance_focus_opacity(self, now):
        # authoritative opacity tracks current stage target directly; keeps old behavior stable and removes stale dual-ramp logic
        self.focus_dim_current_opacity = self.dim_target_opacity
        self.apply_focus_visuals(self.conf())
    def apply_partial_focus_reset(self, conf):
        partial = _clamp_float(conf.get("focus_dim_partial_reset_sec", DEFAULT_CONFIG["focus_dim_partial_reset_sec"]), DEFAULT_CONFIG["focus_dim_partial_reset_sec"], 0.2, 30.0)
        self.last_activity_at = max(_now() - partial, self.last_activity_at)
    def refresh_focus_controller(self, force_rebuild=False):
        conf = self.conf(); self.focus_dim_enabled = bool(conf.get("focus_dim_enabled", False)) and self.runtime_enabled
        if not self.focus_dim_enabled:
            self.stop_focus_timer(); self.reset_focus(clear_overlay=True); return
        if force_rebuild or not self.dim_overlays: self.rebuild_focus_overlays()
        now = _now(); self.last_activity_at = self.last_activity_at or now; self.idle_started_at = self.idle_started_at or self.last_activity_at
        self.ensure_focus_timer(); self.focus_tick()
    def mark_review_activity(self, command, accepted):
        if not accepted or not self.runtime_enabled: return
        conf = self.conf()
        if not conf.get("focus_dim_enabled", False): return
        try:
            if mw.state != "review" or not getattr(mw, "reviewer", None) or not mw.reviewer.card: return
        except Exception:
            return
        reset_mode = "none"
        if command in {"again", "hard", "good", "easy", "undo", "answered_card"}: reset_mode = "full"
        elif command == "flip": reset_mode = "partial"
        elif command == "replay": reset_mode = _normalize_replay_reset_mode(conf.get("focus_dim_replay_reset_mode", DEFAULT_CONFIG["focus_dim_replay_reset_mode"]))
        now = _now(); self.focus_dim_last_activity_source = command
        if reset_mode == "full": self.last_activity_at = now
        elif reset_mode == "partial": self.apply_partial_focus_reset(conf)
        elif reset_mode == "none": return
        self.idle_started_at = self.last_activity_at; self.dim_phase = "idle"; self.dim_target_opacity = 0.0; self.focus_dim_stage_progress = self.focus_dim_last_ramp_progress = 0.0; self.focus_tick()
    def apply_focus_visuals(self, conf):
        try:
            punish_active = self.dim_phase in {"punish", "lockdown"}; self.audio.set_pay_attention(punish_active)
            if not self.dim_overlays: return
            warning_text = str(conf.get("focus_dim_warning_text", DEFAULT_CONFIG["focus_dim_warning_text"]) or DEFAULT_CONFIG["focus_dim_warning_text"])
            warning_sub = str(conf.get("focus_dim_warning_subtext", DEFAULT_CONFIG["focus_dim_warning_subtext"]) or DEFAULT_CONFIG["focus_dim_warning_subtext"])
            warning_style = str(conf.get("focus_dim_warning_style", DEFAULT_CONFIG["focus_dim_warning_style"]) or DEFAULT_CONFIG["focus_dim_warning_style"])
            warning_font = int(_clamp_float(conf.get("focus_dim_warning_font_px", DEFAULT_CONFIG["focus_dim_warning_font_px"]), DEFAULT_CONFIG["focus_dim_warning_font_px"], 14, 84))
            safe_pad = int(_clamp_float(conf.get("focus_dim_safe_padding", DEFAULT_CONFIG["focus_dim_safe_padding"]), DEFAULT_CONFIG["focus_dim_safe_padding"], 0, 140))
            safe_feather = int(_clamp_float(conf.get("focus_dim_safe_feather", DEFAULT_CONFIG["focus_dim_safe_feather"]), DEFAULT_CONFIG["focus_dim_safe_feather"], 0, 180))
            safe_rect = self.current_overlay_global_rect()
            if safe_rect.isValid() and not safe_rect.isNull() and safe_pad > 0: safe_rect = safe_rect.adjusted(-safe_pad, -safe_pad, safe_pad, safe_pad)
            anim = _now(); show_message = self.dim_phase in {"punish", "lockdown"}
            for d in self.dim_overlays:
                d.apply_dim(self.focus_dim_current_opacity, self.dim_phase, self.focus_dim_stage_progress, warning_text, warning_sub, show_message, warning_style, warning_font, safe_rect, safe_feather, anim)
            if self.overlay and self.overlay.isVisible():
                self.overlay.set_focus_alarm_intensity(self.focus_alarm_intensity(self.dim_phase, self.focus_dim_stage_progress), self.dim_phase, self.focus_dim_stage_progress, anim)
                if self.focus_dim_current_opacity > 0: self.overlay.raise_()
        except Exception as exc:
            traceback.print_exc(); self.focus_fail_open("focus visuals", exc)
    def focus_tick(self):
        try:
            conf = self.conf(); self.focus_dim_enabled = bool(conf.get("focus_dim_enabled", False))
            if not self.focus_dim_enabled: self.stop_focus_timer(); self.reset_focus(clear_overlay=True); return
            if not self.dim_overlays: self.rebuild_focus_overlays()
            self.state.sync(); self.sync_focus_baseline_for_card(); now = _now(); self.last_activity_at = self.last_activity_at or now
            if not self.is_review_active_for_dim(conf):
                self.dim_phase = "idle"; self.dim_target_opacity = self.focus_dim_last_idle_elapsed = self.focus_dim_stage_progress = self.focus_dim_last_ramp_progress = 0.0; self.idle_started_at = 0.0; self.advance_focus_opacity(now); self.request_refresh(0, style=True)
                if mw.state != "review" or not getattr(mw, "reviewer", None) or not mw.reviewer.card: self.stop_focus_timer()
                return
            idle_elapsed = max(0.0, now - self.last_activity_at); self.focus_dim_last_idle_elapsed = idle_elapsed
            self.dim_phase, self.focus_dim_stage_progress, self.dim_target_opacity = self.compute_focus_stage(conf, idle_elapsed)
            self.focus_dim_last_ramp_progress = self.focus_dim_stage_progress; self.advance_focus_opacity(now); self.request_refresh(0, style=True)
        except Exception as exc:
            traceback.print_exc(); self.focus_fail_open("focus tick", exc)
    def refresh_overlay_visuals(self):
        conf = self.conf()
        if not self.runtime_enabled or not conf.get("focus_dim_enabled", False):
            self.audio.set_pay_attention(False)
            if self.overlay and self.overlay.isVisible(): self.overlay.set_focus_alarm_intensity(0.0, "idle", 0.0, _now())
            return True
        self.apply_focus_visuals(conf); return True
    def force_refresh(self, *, content=True, style=True, visibility=False, force=False):
        if not self.runtime_enabled or not (content or style or visibility): return
        render_key = self.compute_overlay_render_key() if content else self.last_overlay_render_key
        style_key = self.compute_overlay_style_key() if (style or visibility) else self.last_overlay_style_key
        do_content, do_style = bool(content), bool(style or visibility)
        if not force:
            if do_content and render_key == self.last_overlay_render_key: do_content = False
            if do_style and style_key == self.last_overlay_style_key: do_style = False
            if not do_content and not do_style: return
        ok_content = True
        if do_content:
            ok_content = self.refresh_overlay_content();
            if ok_content: self.last_overlay_render_key = render_key
        if do_style:
            ok_style = self.refresh_overlay_visuals()
            if ok_style: self.last_overlay_style_key = style_key
        if do_content and not ok_content and do_style: self.refresh_overlay_visuals()
    def run_refresh_request(self):
        flags = dict(self.overlay_refresh_flags); self.clear_refresh_queue()
        if flags.get("visibility"): self.reconcile_visibility("refresh_visibility")
        self.force_refresh(content=flags["content"], style=flags["style"], visibility=flags["visibility"], force=flags["force"])
    def show_config(self):
        ConfigDialog().exec()
    def on_show_question(self, card):
        self.state.sync()
        if self.state.pending_command == "undo" and self.state.pending_source_state == ReviewUiState.ANSWER.value:
            self.state.record("undo", "ok"); self.state.clear();
        elif self.state.pending_command in {"again", "hard", "good", "easy"}:
            self.state.record(self.state.pending_command, "ok"); self.state.clear()
        elif self.state.pending_command == "flip":
            if self.state.pending_card_id == self.current_card_id(): self.state.record("flip", "ignored: still on question")
            self.state.clear()
        elif self.state.pending_command == "reveal_then_grade":
            cmd = self.state.pending_reveal_then_grade["command"] if self.state.pending_reveal_then_grade else "reveal_then_grade"
            self.state.record(cmd, "cancelled: returned to question"); self.state.pending_reveal_then_grade = None; self.state.clear()
        self.request_refresh(0, content=True, style=True)
    def on_show_answer(self, card):
        self.state.sync()
        if self.state.pending_command == "reveal_then_grade" and self.state.pending_reveal_then_grade:
            exp = self.state.pending_reveal_then_grade.get("card_id")
            if exp is None or exp == self.current_card_id():
                self.handle_pending_reveal_then_grade(self.current_card_id()); self.request_refresh(0, content=True, style=True); return
        if self.state.pending_command == "flip" and self.state.pending_source_state == ReviewUiState.QUESTION.value:
            self.state.record("flip", "ok: question->answer"); self.state.clear()
        elif self.state.pending_command == "undo" and self.state.pending_source_state == ReviewUiState.QUESTION.value:
            self.state.record("undo", "ok: question->answer"); self.state.clear()
        self.request_refresh(0, content=True, style=True)
    def on_answered_card(self, reviewer, card, ease):
        cmd = {1: "again", 2: "hard", 3: "good", 4: "easy"}.get(ease)
        if cmd: self.audio.play_grade(cmd, source="hook")
        self.mark_review_activity("answered_card", True)
    def init_overlay_once(self):
        self.init_timer = None; self.last_overlay_render_key = self.last_overlay_style_key = None; self.ensure_app_state_hooks()
        existing = getattr(mw, "_anki_overlay_instance", None)
        if existing is not None:
            self.overlay = existing; self.start_listener(toggle_only=not self.runtime_enabled); self.refresh_focus_controller(force_rebuild=True); self.reconcile_visibility("init_existing", force_show=True); return
        self.overlay = Overlay(); mw._anki_overlay_instance = self.overlay; self.start_listener(toggle_only=not self.runtime_enabled); self.refresh_focus_controller(force_rebuild=True); self.reconcile_visibility("init_new", force_show=True); self.request_refresh(0, content=True, style=True, force=True)
    def ensure_settings_action(self):
        if getattr(mw, "_anki_overlay_action", None): return
        act = QAction("Overlay Preferences", mw)
        act.triggered.connect(self.show_config)
        mw.form.menuTools.addAction(act)
        mw._anki_overlay_action = act
    def on_profile_open(self):
        self.addon_active = self.runtime_enabled = True; self.overlay_user_hidden = self.overlay_auto_hidden_by_window = False; self.state = TransitionState(); self.clear_refresh_queue(stop_timer=True)
        self.ensure_app_state_hooks(); self.ensure_settings_action(); self.audio.init_grade_sounds(); self.refresh_focus_controller(force_rebuild=True)
        if self.init_timer:
            try: self.init_timer.stop(); self.init_timer.deleteLater()
            except Exception: pass
        self.init_timer = QTimer(mw); self.init_timer.setSingleShot(True); self.init_timer.timeout.connect(self.init_overlay_once); self.init_timer.start(1000)
    def cleanup(self):
        self.addon_active = False; self.stop_transition_watchdog(); self.stop_listener(); self.stop_focus_timer(); self.disconnect_app_state_hooks(); self.audio.clear(full_release=True); self.clear_refresh_queue(stop_timer=True)
APP = Runtime()
class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__(mw)
        self.setWindowTitle("Overlay Preferences")
        self.resize(900, 620)
        self.conf = get_config()
        self.all_decks = sorted(mw.col.decks.all_names())
        self.init_ui()
    def combo_row(self, value):
        box = QComboBox(); box.addItems(["Select Deck..."] + self.all_decks)
        if value: box.setCurrentText(value)
        return box
    def deck_fields(self, deck_name):
        try:
            did = mw.col.decks.id(deck_name)
            mids = mw.col.db.list("select distinct n.mid from cards c join notes n on c.nid=n.id where c.did = ?", did)
            shared = None
            for mid in mids:
                model = mw.col.models.get(mid)
                if not model: continue
                names = {f["name"] for f in model.get("flds", [])}
                shared = names if shared is None else shared.intersection(names)
            return sorted(shared or [])
        except Exception:
            return []
    def add_mapping_row(self, data=None):
        data = _normalize_deck_map(data or {}) or _normalize_deck_map({})
        r = self.table.rowCount(); self.table.insertRow(r)
        deck_name = APP.deck_name_from_id(data.get("deck_id")) or data.get("deck", "")
        deck_cb = self.combo_row(deck_name); combos = []
        def update_fields():
            fields = self.deck_fields(deck_cb.currentText()) if deck_cb.currentText() != "Select Deck..." else []
            for i, (_, key) in enumerate(DECK_MAP_FIELDS):
                current = combos[i].currentText() if combos else ""
                combos[i].clear(); combos[i].addItems([""] + fields)
                selected = data.get(key) or current
                if selected: combos[i].setCurrentText(selected)
        deck_cb.currentTextChanged.connect(update_fields)
        self.table.setCellWidget(r, 0, deck_cb)
        for i, (_, key) in enumerate(DECK_MAP_FIELDS, start=1):
            cb = QComboBox(); combos.append(cb); self.table.setCellWidget(r, i, cb)
        update_fields()
    def add_theme_row(self, data=None):
        data = _normalize_deck_theme(data or {}) or _normalize_deck_theme({})
        r = self.theme_table.rowCount(); self.theme_table.insertRow(r)
        deck_name = APP.deck_name_from_id(data.get("deck_id")) or data.get("deck", "")
        deck_cb = self.combo_row(deck_name)
        word = QLineEdit(data.get("color_word", "")); trans = QLineEdit(data.get("color_pitch", "")); sent = QLineEdit(data.get("color_sent", ""))
        op = QSpinBox(); op.setRange(-1, 100); op.setSpecialValueText("Default"); op.setValue(_normalize_opacity(data.get("opacity", -1)))
        mode = QComboBox(); mode.addItems(["Default", "full", "compact"]); mode.setCurrentText(data.get("mode") or "Default")
        for c, w in enumerate([deck_cb, word, trans, sent, op, mode]): self.theme_table.setCellWidget(r, c, w)
    def init_ui(self):
        layout = QVBoxLayout(self); tabs = QTabWidget(); layout.addWidget(tabs)
        # mappings
        deck_tab = QWidget(); dvl = QVBoxLayout(deck_tab)
        self.table = QTableWidget(0, len(DECK_MAP_FIELDS) + 1); self.table.setHorizontalHeaderLabels(["Deck"] + [label for label, _ in DECK_MAP_FIELDS]); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for row in self.conf.get("deck_maps", []): self.add_mapping_row(row)
        hb = QHBoxLayout(); a = QPushButton("+ Add Mapping"); r = QPushButton("- Remove Selected"); a.clicked.connect(lambda: self.add_mapping_row({})); r.clicked.connect(lambda: self.table.removeRow(self.table.currentRow())); hb.addWidget(a); hb.addWidget(r)
        dvl.addWidget(self.table); dvl.addLayout(hb); tabs.addTab(deck_tab, "Decks Mapping")
        # general
        gen = QWidget(); gl = QFormLayout(gen)
        self.w = QSpinBox(); self.w.setRange(200, 2500); self.w.setValue(self.conf["width"])
        self.h = QSpinBox(); self.h.setRange(100, 2000); self.h.setValue(self.conf["height"])
        self.op = QSlider(Qt.Orientation.Horizontal); self.op.setRange(0,100); self.op.setValue(int(self.conf["opacity"]))
        self.cw = QLineEdit(self.conf["color_word"]); self.cp = QLineEdit(self.conf["color_pitch"]); self.cs = QLineEdit(self.conf["color_sent"])
        self.fw = QSpinBox(); self.fw.setRange(20,160); self.fw.setValue(_normalize_font(self.conf.get("font_size_word", 42), 42, 20, 160))
        self.ft = QSpinBox(); self.ft.setRange(12,120); self.ft.setValue(_normalize_font(self.conf.get("font_size_translation", 26), 26, 12, 120))
        self.fe = QSpinBox(); self.fe.setRange(10,96); self.fe.setValue(_normalize_font(self.conf.get("font_size_example", 18), 18, 10, 96))
        self.grade_mode = QComboBox(); self.grade_mode.addItem("Use Grade Keys To Flip (Recommended)", "flip_only"); self.grade_mode.addItem("Ignore Grade Keys On Question", "ignore"); self.grade_mode.addItem("Reveal Then Auto-Grade", "reveal_then_grade"); self.grade_mode.setCurrentIndex(max(0, self.grade_mode.findData(_normalize_grade_mode(self.conf.get("grade_from_question_mode")))))
        for label, widget in [("Width:", self.w), ("Answer Box Height:", self.h), ("Opacity %:", self.op), ("Word Color:", self.cw), ("Translation Color:", self.cp), ("Example Color:", self.cs), ("Word Font Size:", self.fw), ("Translation Font Size:", self.ft), ("Example Font Size:", self.fe), ("Question-Side Grade Keys:", self.grade_mode)]: gl.addRow(label, widget)
        note = QLabel("Text mode: mapped note fields are rendered as plain text (HTML is escaped)."); note.setWordWrap(True); gl.addRow("", note)
        # focus controls
        self.fd_enable = QCheckBox(); self.fd_enable.setChecked(bool(self.conf.get("focus_dim_enabled", False)))
        self.fd_idle = QDoubleSpinBox(); self.fd_idle.setRange(0.5, 600); self.fd_idle.setDecimals(1); self.fd_idle.setSingleStep(0.1); self.fd_idle.setValue(_clamp_float(self.conf.get("focus_dim_idle_sec"), DEFAULT_CONFIG["focus_dim_idle_sec"], 0.5, 600))
        self.fd_warn = QDoubleSpinBox(); self.fd_warn.setRange(0.1, 600); self.fd_warn.setDecimals(1); self.fd_warn.setSingleStep(0.1); self.fd_warn.setValue(_clamp_float(self.conf.get("focus_dim_warning_sec"), DEFAULT_CONFIG["focus_dim_warning_sec"], 0.1, 600))
        self.fd_punish = QDoubleSpinBox(); self.fd_punish.setRange(0.1, 600); self.fd_punish.setDecimals(1); self.fd_punish.setSingleStep(0.1); self.fd_punish.setValue(_clamp_float(self.conf.get("focus_dim_punish_sec"), DEFAULT_CONFIG["focus_dim_punish_sec"], 0.1, 600))
        self.fd_lock = QDoubleSpinBox(); self.fd_lock.setRange(0.1, 600); self.fd_lock.setDecimals(1); self.fd_lock.setSingleStep(0.1); self.fd_lock.setValue(_clamp_float(self.conf.get("focus_dim_lockdown_sec"), DEFAULT_CONFIG["focus_dim_lockdown_sec"], 0.1, 600))
        self.fd_warn_op = QSlider(Qt.Orientation.Horizontal); self.fd_warn_op.setRange(0,100); self.fd_warn_op.setValue(int(_clamp_float(self.conf.get("focus_dim_warning_opacity"), DEFAULT_CONFIG["focus_dim_warning_opacity"], 0, 100)))
        self.fd_punish_op = QSlider(Qt.Orientation.Horizontal); self.fd_punish_op.setRange(0,100); self.fd_punish_op.setValue(int(_clamp_float(self.conf.get("focus_dim_punish_opacity"), DEFAULT_CONFIG["focus_dim_punish_opacity"], 0, 100)))
        self.fd_max_op = QSlider(Qt.Orientation.Horizontal); self.fd_max_op.setRange(0,100); self.fd_max_op.setValue(int(_clamp_float(self.conf.get("focus_dim_max_opacity"), DEFAULT_CONFIG["focus_dim_max_opacity"], 0, 100)))
        self.fd_curve = QComboBox(); self.fd_curve.addItem("Quadratic (Default)", "quad"); self.fd_curve.addItem("Linear", "linear"); self.fd_curve.addItem("Cubic", "cubic"); self.fd_curve.setCurrentIndex(max(0, self.fd_curve.findData(_normalize_curve(self.conf.get("focus_dim_curve")))))
        self.fd_q_only = QCheckBox(); self.fd_q_only.setChecked(bool(self.conf.get("focus_dim_question_only", False)))
        self.fd_pad = QSpinBox(); self.fd_pad.setRange(0, 140); self.fd_pad.setValue(int(_clamp_float(self.conf.get("focus_dim_safe_padding"), DEFAULT_CONFIG["focus_dim_safe_padding"], 0, 140)))
        self.fd_feather = QSpinBox(); self.fd_feather.setRange(0,180); self.fd_feather.setValue(int(_clamp_float(self.conf.get("focus_dim_safe_feather"), DEFAULT_CONFIG["focus_dim_safe_feather"], 0, 180)))
        self.fd_text = QLineEdit(str(self.conf.get("focus_dim_warning_text", DEFAULT_CONFIG["focus_dim_warning_text"])))
        self.fd_sub = QLineEdit(str(self.conf.get("focus_dim_warning_subtext", DEFAULT_CONFIG["focus_dim_warning_subtext"])))
        self.fd_style = QComboBox(); self.fd_style.addItem("Shake + Glow", "shake_glow"); self.fd_style.addItem("Pulse", "pulse"); self.fd_style.setCurrentIndex(max(0, self.fd_style.findData(str(self.conf.get("focus_dim_warning_style", DEFAULT_CONFIG["focus_dim_warning_style"])).strip().lower())))
        self.fd_font = QSpinBox(); self.fd_font.setRange(14,84); self.fd_font.setValue(int(_clamp_float(self.conf.get("focus_dim_warning_font_px"), DEFAULT_CONFIG["focus_dim_warning_font_px"], 14, 84)))
        self.fd_replay = QComboBox(); self.fd_replay.addItem("Partial Relief (Recommended)", "partial"); self.fd_replay.addItem("Full Reset", "full"); self.fd_replay.addItem("No Relief", "none"); self.fd_replay.setCurrentIndex(max(0, self.fd_replay.findData(_normalize_replay_reset_mode(self.conf.get("focus_dim_replay_reset_mode")))))
        self.fd_partial = QDoubleSpinBox(); self.fd_partial.setRange(0.2, 30); self.fd_partial.setDecimals(1); self.fd_partial.setSingleStep(0.1); self.fd_partial.setValue(_clamp_float(self.conf.get("focus_dim_partial_reset_sec"), DEFAULT_CONFIG["focus_dim_partial_reset_sec"], 0.2, 30))
        for label, widget in [("Focus Dim Enabled:", self.fd_enable), ("Idle Grace (sec):", self.fd_idle), ("Warning Duration (sec):", self.fd_warn), ("Punish Duration (sec):", self.fd_punish), ("Lockdown Duration (sec):", self.fd_lock), ("Warning Opacity:", self.fd_warn_op), ("Punish Opacity:", self.fd_punish_op), ("Focus Dim Max Opacity:", self.fd_max_op), ("Punish Curve:", self.fd_curve), ("Focus Dim Question Only:", self.fd_q_only), ("Safe Zone Padding:", self.fd_pad), ("Safe Zone Feather:", self.fd_feather), ("Warning Text:", self.fd_text), ("Warning Subtext:", self.fd_sub), ("Warning Style:", self.fd_style), ("Warning Font Size:", self.fd_font), ("Replay Relief:", self.fd_replay), ("Partial Relief Seconds:", self.fd_partial)]: gl.addRow(label, widget)
        tabs.addTab(gen, "General")
        # hotkeys
        hot = QWidget(); hl = QFormLayout(hot); self.hk = {k: HotkeyRecorder(self.conf.get(k, "")) for k in HOTKEY_KEYS}
        for k in HOTKEY_KEYS: hl.addRow(f"{HOTKEY_LABELS[k]}:", self.hk[k])
        self.debug_box = QCheckBox(); self.debug_box.setChecked(bool(self.conf.get("debug_status", False))); hl.addRow("Debug Status:", self.debug_box)
        tabs.addTab(hot, "Hotkeys")
        # themes
        theme_tab = QWidget(); tvl = QVBoxLayout(theme_tab)
        self.theme_table = QTableWidget(0, 6); self.theme_table.setHorizontalHeaderLabels(["Deck", "Word", "Translation", "Example", "Opacity", "Mode"]); self.theme_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for row in self.conf.get("deck_themes", []): self.add_theme_row(row)
        hb2 = QHBoxLayout(); add_t = QPushButton("+ Add Theme"); del_t = QPushButton("- Remove Selected"); add_t.clicked.connect(lambda: self.add_theme_row({})); del_t.clicked.connect(lambda: self.theme_table.removeRow(self.theme_table.currentRow())); hb2.addWidget(add_t); hb2.addWidget(del_t)
        tvl.addWidget(self.theme_table); tvl.addLayout(hb2); tabs.addTab(theme_tab, "Deck Themes")
        # buttons
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.save_all); btns.rejected.connect(self.reject); layout.addWidget(btns)
    def save_all(self):
        new_maps = []
        for r in range(self.table.rowCount()):
            deck_cb = self.table.cellWidget(r, 0)
            if deck_cb and deck_cb.currentText() != "Select Deck...":
                deck_name = deck_cb.currentText()
                try: deck_id = mw.col.decks.id(deck_name)
                except Exception: deck_id = None
                row = {"deck_id": deck_id, "deck": deck_name}
                for col, (_, key) in enumerate(DECK_MAP_FIELDS, start=1): row[key] = self.table.cellWidget(r, col).currentText()
                new_maps.append(row)
        new_themes = []
        for r in range(self.theme_table.rowCount()):
            deck_cb = self.theme_table.cellWidget(r, 0)
            if deck_cb and deck_cb.currentText() != "Select Deck...":
                deck_name = deck_cb.currentText()
                try: deck_id = mw.col.decks.id(deck_name)
                except Exception: deck_id = None
                mode_widget = self.theme_table.cellWidget(r, 5); mode_value = mode_widget.currentText().strip().lower() if mode_widget else ""
                if mode_value == "default": mode_value = ""
                new_themes.append({
                    "deck_id": deck_id, "deck": deck_name,
                    "color_word": _normalize_optional_hex_color(self.theme_table.cellWidget(r, 1).text().strip()),
                    "color_pitch": _normalize_optional_hex_color(self.theme_table.cellWidget(r, 2).text().strip()),
                    "color_sent": _normalize_optional_hex_color(self.theme_table.cellWidget(r, 3).text().strip()),
                    "opacity": self.theme_table.cellWidget(r, 4).value(), "mode": mode_value,
                })
        warn_op = int(self.fd_warn_op.value()); punish_op = max(warn_op, int(self.fd_punish_op.value())); max_op = max(punish_op, int(self.fd_max_op.value()))
        final = get_config(); final.update({
            "deck_maps": new_maps, "deck_themes": new_themes, "width": self.w.value(), "height": self.h.value(), "opacity": self.op.value(),
            "color_word": _normalize_hex_color(self.cw.text(), DEFAULT_CONFIG["color_word"]), "color_pitch": _normalize_hex_color(self.cp.text(), DEFAULT_CONFIG["color_pitch"]), "color_sent": _normalize_hex_color(self.cs.text(), DEFAULT_CONFIG["color_sent"]),
            "font_size_word": self.fw.value(), "font_size_translation": self.ft.value(), "font_size_example": self.fe.value(),
            "grade_from_question_mode": _normalize_grade_mode(self.grade_mode.currentData()), "debug_status": self.debug_box.isChecked(),
            "focus_dim_enabled": self.fd_enable.isChecked(), "focus_dim_idle_sec": float(self.fd_idle.value()), "focus_dim_warning_sec": float(self.fd_warn.value()),
            "focus_dim_punish_sec": float(self.fd_punish.value()), "focus_dim_lockdown_sec": float(self.fd_lock.value()), "focus_dim_timing_model": "durations_v2",
            "focus_dim_warning_opacity": warn_op, "focus_dim_punish_opacity": punish_op, "focus_dim_max_opacity": max_op,
            "focus_dim_curve": _normalize_curve(self.fd_curve.currentData()), "focus_dim_question_only": self.fd_q_only.isChecked(),
            "focus_dim_safe_padding": self.fd_pad.value(), "focus_dim_safe_feather": self.fd_feather.value(), "focus_dim_warning_text": self.fd_text.text(),
            "focus_dim_warning_subtext": self.fd_sub.text(), "focus_dim_warning_style": self.fd_style.currentData(), "focus_dim_warning_font_px": self.fd_font.value(),
            "focus_dim_replay_reset_mode": _normalize_replay_reset_mode(self.fd_replay.currentData()), "focus_dim_partial_reset_sec": self.fd_partial.value(),
            "focus_dim_ramp_sec": max(0.1, float(self.fd_warn.value())), "focus_dim_replay_counts_as_activity": self.fd_replay.currentData() != "none", "focus_dim_show_message": True, "focus_dim_message": self.fd_text.text(),
            "pos_x": final.get("pos_x", 50), "pos_y": final.get("pos_y", 50),
        })
        for k, w in self.hk.items(): final[k] = _normalize_hotkey(w.current_key)
        flip_combo = _normalize_hotkey(final.get("key_flip", ""))
        if flip_combo and any(flip_combo == _normalize_hotkey(final.get(k, "")) for k in GRADE_KEYS) and _normalize_grade_mode(final.get("grade_from_question_mode")) == "ignore":
            final["grade_from_question_mode"] = "flip_only"
        issues = APP.validate_hotkeys(final)
        if issues:
            tooltip(f"Fix hotkeys before saving: {'; '.join(issues[:3])}", period=5000); return
        save_config(final); tooltip("Saved!", period=1500)
        if APP.overlay: APP.overlay.apply_prefs(); APP.reconcile_visibility("config_saved", force_show=not APP.overlay_user_hidden)
        APP.start_listener(show_feedback=True, toggle_only=not APP.runtime_enabled); APP.refresh_focus_controller(force_rebuild=True); APP.request_refresh(0, content=True, style=True, force=True); self.accept()
def _on_show_question(card): APP.on_show_question(card)
def _on_show_answer(card): APP.on_show_answer(card)
def _on_answered_card(reviewer, card, ease): APP.on_answered_card(reviewer, card, ease)
def _on_profile_close(*_args): APP.cleanup()
def on_profile_open(): APP.on_profile_open()
def _atexit_cleanup(): APP.cleanup()
if not getattr(mw, "_anki_overlay_hooks_registered", False):
    gui_hooks.profile_did_open.append(on_profile_open)
    gui_hooks.reviewer_did_show_question.append(_on_show_question)
    gui_hooks.reviewer_did_show_answer.append(_on_show_answer)
    if hasattr(gui_hooks, "undo_state_did_change"): gui_hooks.undo_state_did_change.append(lambda *_: APP.schedule_external_refresh("undo_state"))
    if hasattr(gui_hooks, "operation_did_execute"): gui_hooks.operation_did_execute.append(lambda *_: APP.schedule_external_refresh("operation_executed"))
    if hasattr(gui_hooks, "reviewer_did_answer_card"): gui_hooks.reviewer_did_answer_card.append(_on_answered_card)
    if hasattr(gui_hooks, "profile_will_close"): gui_hooks.profile_will_close.append(_on_profile_close)
    if hasattr(gui_hooks, "main_window_will_close"): gui_hooks.main_window_will_close.append(_on_profile_close)
    mw._anki_overlay_hooks_registered = True
if not getattr(mw, "_anki_overlay_atexit_registered", False):
    atexit.register(_atexit_cleanup)
    mw._anki_overlay_atexit_registered = True
