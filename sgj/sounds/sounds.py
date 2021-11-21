import os
from enum import Enum
from typing import Optional

import arcade
from pyglet.media import Player

from sgj.graphics.constants import SOUNDS_DIR, MAX_VOLUME, trim

MUISC_PATH_MAIN_THEME = os.path.join(SOUNDS_DIR, "music2.wav")
MUISC_PATH_MENU = os.path.join(SOUNDS_DIR, "main_menu.wav")
current_player: Optional[Player] = None

# TODO: Move it to global settings structure
VOLUME = MAX_VOLUME // 2  # Volume global settings.

class Effect(Enum):
    CARD_MOVING = os.path.join(SOUNDS_DIR, "card_moving.wav")
    EFFECT = os.path.join(SOUNDS_DIR, "effect.wav")
    NEWS_QUICK = os.path.join(SOUNDS_DIR, "news_quick.wav")
    NEWS = os.path.join(SOUNDS_DIR, "news.wav")
    TRICK1 = os.path.join(SOUNDS_DIR, "trick1.wav")
    TRICK2 = os.path.join(SOUNDS_DIR, "trick2.wav")
    CLICK = os.path.join(SOUNDS_DIR, "click.wav")
    TAP_SCROLL = os.path.join(SOUNDS_DIR, "tap_scroll.wav")


def stop_current_theme():
    if current_player is not None:
        arcade.stop_sound(current_player)


def play_new_current_theme(sound_path):
    stop_current_theme()
    current_theme = arcade.load_sound(sound_path)
    if current_theme:
        global current_player
        current_player = arcade.play_sound(current_theme, looping=True, volume=VOLUME)


def play_main_theme():
    play_new_current_theme(MUISC_PATH_MENU)


def play_menu_theme():
    play_new_current_theme(MUISC_PATH_MAIN_THEME)


def play_effect(effect: Effect):
    arcade.Sound(effect.value).play(volume=VOLUME)


def set_volume(volume: int):
    global VOLUME
    new_volume = trim(0, get_max_volume(), volume)
    if VOLUME != new_volume:
        VOLUME = trim(0, get_max_volume(), volume)
        current_player.volume = VOLUME / get_max_volume()


def get_volume() -> int:
    return VOLUME


def get_max_volume() -> int:
    return MAX_VOLUME


def change_volume(delta: int):
    set_volume(get_volume() + delta)
