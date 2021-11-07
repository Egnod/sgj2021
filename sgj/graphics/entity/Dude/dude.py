import os
import random
import time

import arcade

from sgj.graphics.constants import SPRITE_DIR

# Поведение Ой
# Реакция на ховер любой карты (фразы вроде "уверен?", "вкус так себе")
# Реакция на бездействие (10 секунд?)
# Реакция на любой выбор (подтасовывание карты, перекрытие облаком диалога)
# Реакция на долгий ховер?
# Реакция на большую награду? За новость?
# Спонтанная фраза в случае если давно не было фраз
# *Не повторяться со спонтанными фразами


class Dude:
    SPRITE_DUDE_PATH = os.path.join(SPRITE_DIR, "Interface", "dude.png")
    SPRITE_DUDE_SHIFT = 50, 10
    SPRITE_DIALOG_PATH = os.path.join(SPRITE_DIR, "Interface", "cloud.png")
    SPRITE_DIALOG_SHIFT = 150, 50

    DIALOG_SHOWING_DELAY = 4  # in sec
    TRICK_IDLE_DELAY = 10  # in sec

    CHANCE_IDLE = 0.001
    EACH_N_HOVER = 10
    CHANCE_CARD_HOVER = 0.01
    CHANCE_BAD_NEWS = 0.1

    PHRASES = {
        "Idle": [
            "Здрасте-здрасте, забор покрасте.",
            "Ты же помнишь, что все зависит от тебя?",
            "Тебе отвечать за последствия.",
            "В самом начале ты мне казался более сообразительным конечно",
            "Скукотииища",
        ],
        "CardHover": [
            "Ой, кажется я что-то тебе спутал, мне очень жаль :)",
            "ДАВАЙ ЖЕ ЖМИ",
            "Ты точно уверен в своём решении?",
            "М-да, вкус у тебя так себе",
            "По моему, соседняя карточка выглядит куда привлекательнее, но решать, "
            "конечно, тебе",
        ],
        "BadNews": [
            "Ой как неосмотрительно",
            "Кто бы мог подумать, что ты так жесток",
        ],
    }

    def __init__(self):
        self.dude_sprite = arcade.Sprite(self.SPRITE_DUDE_PATH)
        self.dude_sprite.center_x += self.SPRITE_DUDE_SHIFT[0]
        self.dude_sprite.center_y += self.SPRITE_DUDE_SHIFT[1]

        self.dialog_sprite = arcade.Sprite(self.SPRITE_DIALOG_PATH)
        self.dialog_sprite.center_x += self.SPRITE_DIALOG_SHIFT[0]
        self.dialog_sprite.center_y += self.SPRITE_DIALOG_SHIFT[1]

        self.time_since_last_action = 0.0
        self.hover_counter = 0

        self.dialog_left_time = 0.0
        self.text = ""

        self.last_action_time = (
            time.time() + self.TRICK_IDLE_DELAY
        )  # даём пользователю в начале больше времени

    def draw(self):
        self.dude_sprite.draw()
        if self._need_show_dialog():
            self.dialog_sprite.draw()

            arcade.draw_text(
                self.text,
                self.SPRITE_DIALOG_SHIFT[0] + self.dialog_sprite.width / 4,
                self.SPRITE_DIALOG_SHIFT[1] + self.dialog_sprite.height / 3 * 2,
                multiline=True,
                width=int(self.dialog_sprite.width // 2),
                color=arcade.color.BLACK,
            )

    def is_blocking_other(self):
        return self._need_show_dialog()

    def count_action(self):
        self.last_action_time = time.time()

    def _react(self, group_name: str, chance: float):
        throw_result = 1 - random.uniform(0, 1)
        if throw_result >= chance:
            if len(self.PHRASES[group_name]) > 0:
                random.shuffle(self.PHRASES[group_name])
                self._show_dialog(
                    self.PHRASES[group_name].pop(0),
                    self.DIALOG_SHOWING_DELAY,
                )
                return True
        return False

    def update_reaction_on_news(self, rewards: dict):
        if rewards["angry"] > 0 or rewards["fatum"] > 0:
            self._react("BadNews", self.CHANCE_BAD_NEWS)

    def try_react_on_hover(self):
        if self.EACH_N_HOVER < self.hover_counter:
            if self._react("CardHover", self.CHANCE_CARD_HOVER):
                self.hover_counter = 0

    def _show_dialog(self, text: str, dialog_time: float):
        self.text = text
        self.dialog_left_time = dialog_time

    def _hide_dialog(self):
        self.text = ""

    def _need_show_dialog(self):
        return self.text != ""

    def update(self, dt: float):
        self.dialog_left_time -= dt
        if self.dialog_left_time < 0:
            self._hide_dialog()

        time_passed = time.time() - self.last_action_time
        if time_passed > self.TRICK_IDLE_DELAY:
            if self._react("Idle", self.CHANCE_IDLE):
                self.last_action_time = time.time()
