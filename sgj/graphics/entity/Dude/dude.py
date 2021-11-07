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

    CHANCE_IDLE = 0.01
    CHANCE_CARD_HOVER = 0.1
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
        ]
    }

    def __init__(self):
        self.dude_sprite = arcade.Sprite(self.SPRITE_DUDE_PATH)
        self.dude_sprite.center_x += self.SPRITE_DUDE_SHIFT[0]
        self.dude_sprite.center_y += self.SPRITE_DUDE_SHIFT[1]

        self.dialog_sprite = arcade.Sprite(self.SPRITE_DIALOG_PATH)
        self.dialog_sprite.center_x += self.SPRITE_DIALOG_SHIFT[0]
        self.dialog_sprite.center_y += self.SPRITE_DIALOG_SHIFT[1]

        # self.actions_sice_last_trick = 0
        self.time_since_last_action = 0.0

        self.dialog_left_time = 0.0
        self.text = ""

        self.last_action_time = time.time() - self.TRICK_IDLE_DELAY  # даём пользователю в начале больше времени

    def draw(self):
        self.dude_sprite.draw()

    def count_action(self):
        # self.actions_sice_last_trick += 1
        self.last_action_time = time.time()

    def _react(self, group_name: str, chance: float):
        throw_result = random.uniform(0, 1)
        if throw_result >= chance:
            self._show_dialog(self.PHRASES[group_name], self.DIALOG_SHOWING_DELAY)

    def update_reaction_on_news(self, rewards: dict):
        if rewards['angry'] > 0 or rewards['fatum'] > 0:
            self._react('BadNews', self.CHANCE_BAD_NEWS)

    def try_react_on_hover(self):
        # TODO: not each time call this
        self._react('CardHover', self.CHANCE_CARD_HOVER)

    def _show_dialog(self, text: str, time: float):
        self.text = text
        self.dialog_left_time = time

    def _hide_dialog(self):
        self.text = ""

    def _need_show_dialog(self):
        return self.text != ""

    def update(self, dt: float):
        self.dialog_left_time -= dt
        if self.dialog_left_time < 0:
            self._hide_dialog()
        if self.last_action_time - time.time() > self.TRICK_IDLE_DELAY:
            self._react('Idle', self.CHANCE_IDLE)
