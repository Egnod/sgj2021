import os
from enum import Enum

import arcade

from sgj.graphics.constants import SOUNDS_DIR, MAX_VOLUME

# card_moving.wav	effect.wav	music1.wav	music3.wav	news_quick.wav	trick1.wav
# click.wav	main_menu.wav	music2.wav	news.wav	tap_scroll.wav	trick2.wav

MUISC_PATH_MAIN_THEME = os.path.join(SOUNDS_DIR, "music2.wav")
MUISC_PATH_MENU = os.path.join(SOUNDS_DIR, "main_menu.wav")
current_player = None  # type Optional[arcade.media.player.Player]

VOLUME = MAX_VOLUME // 2


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
    global current_player
    if current_player is not None:
        arcade.stop_sound(current_player)


def play_new_current_theme(sound_path):
    global current_player
    stop_current_theme()
    current_theme = arcade.load_sound(sound_path)
    if current_theme:
        current_player = arcade.play_sound(current_theme, looping=True, volume=VOLUME)


def play_main_theme():
    play_new_current_theme(MUISC_PATH_MENU)


def play_menu_theme():
    play_new_current_theme(MUISC_PATH_MAIN_THEME)


def play_effect(effect: Effect):
    arcade.Sound(effect.value).play(volume=VOLUME)


def set_volume(volume: int):
    global current_player
    global VOLUME
    VOLUME = volume
    current_player.volume = VOLUME / MAX_VOLUME
    print("prev: {} new: {}".format(VOLUME, volume))
