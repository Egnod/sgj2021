import math
from datetime import datetime
from functools import partial
from typing import List, Optional

import arcade

from sgj.graphics.constants import HORIZONTAL_CARDS_PADDING, SELECT_CARD_SCALE
from sgj.graphics.entity.select.sprite import SelectCardSprite


class SelectCardController:
    def __init__(self, event_card, cards):
        from sgj.graphics.game_view import GameView

        self.default_speed = 30  # Default speed for any card actions

        self.event_card = event_card
        self.cards: List[SelectCardSprite] = cards

        self.events_stack = []
        self.draw_events_stack = []
        self.turnover_alpha = 0

        self.chosen_effect_finish = False
        self.chosen_card_texture_changed = False

        self.turnover_card = arcade.load_animated_gif(
            "./sgj/graphics/assets/imgs/card_turnover.gif",
        )
        self.turnover_card.alpha = 0

        self.set_consequence_at = None
        self.consequence_card = None
        self.after_consequence = False
        self.after_consequence_end = False

        self.game_view: Optional[GameView] = None

    def check_for_next_round(self):
        if self.consequence_card and not self.after_consequence:
            self.after_consequence = True
            self.set_hide(
                self.consequence_card,
            )
            return True

    def set_game_view(self, view):
        self.game_view = view

    def render_events(self):
        new_stack = []

        for event in self.events_stack:
            result = event()

            if not result:
                new_stack.append(event)

        self.events_stack = new_stack

    def draw_events(self):
        new_stack = []

        for event in self.draw_events_stack:
            result = event()

            if not result:
                new_stack.append(event)

        self.draw_events_stack = new_stack

    def pre_render(self):
        PADDING = arcade.get_window().width * HORIZONTAL_CARDS_PADDING
        chunk_size = (arcade.get_window().width - PADDING * 2) / len(self.cards)
        pos_shift = chunk_size / 2 + PADDING

        for index, card in enumerate(self.cards):
            card.start_x = card.center_x = chunk_size * index + pos_shift
            card.start_y = 0

            card.center_y = -card.height

            self.set_show(card)

    def set_hide(self, card):
        """
        Hide card after use.
        """
        self.events_stack.append(partial(self._set_hide, card))

    def set_show(self, card):
        """
        Show card for use.
        """
        self.events_stack.append(partial(self._set_show, card))

    def set_to_start(self, card):
        """
        Move card to start position.
        """
        if card.center_y == card.start_y and card.center_x == card.start_x:
            return None

        self.events_stack.append(partial(self._set_to_start, card))

    def set_hover(self, card):
        """
        Actions on card hover.
        """
        if (
            not card.hover_start
            and not card.hovered
            and (
                not card.hovered_at
                or (
                    datetime.now() > card.hovered_at
                    and (datetime.now() - card.hovered_at).total_seconds() > 0.8
                )
            )
        ):
            self.events_stack.append(partial(self._set_hover, card))

    def unset_hover(self, card, force: bool = False):
        """
        Actions on card un-hover.
        """
        if (
            not force
            and card.hovered_at
            and datetime.now() > card.hovered_at
            and (datetime.now() - card.hovered_at).total_seconds() < 0.8
        ):
            return None

        self.events_stack.append(partial(self._unset_hover, card))

    def set_chosen(self, card):
        """
        Set card as chosen.
        """
        card.hovered = False
        card.chosen = True

        self.events_stack.append(partial(self._set_chosen, card))

    def set_selected_scale(self, card):
        """
        Set selected card scale.
        """
        card.scale = 0.2

    def set_default_scale(self, card):
        """
        Set default card scale after actions.
        """
        card.scale = SELECT_CARD_SCALE

    def set_turnover(self, card):
        """
        Set default card scale after actions.
        """
        if card.chosen:
            self.turnover_alpha = 0
            self.draw_events_stack.append(partial(self._set_turnover_draw, card))
            self.events_stack.append(partial(self._set_turnover_update, card))

    def set_consequence(self, card):
        """
        Set card consequence time-message.
        """
        self.draw_events_stack.append(partial(self._set_consequence_draw, card))

    def set_round_end_tip(self, card):
        """
        Set round end tip (press any key).
        """
        self.draw_events_stack.append(partial(self._set_round_end_tip, card))

    def _set_round_end_tip(self, card: SelectCardSprite):
        if self.after_consequence:
            return True

        arcade.draw_text(
            "Нажмите любую клавишу для следующего события",
            self.game_view.window.width / 2,
            self.game_view.window.height / 4,
            width=math.floor(card.width) - 15,
            multiline=True,
            color=arcade.color.BLACK,
            anchor_x="center",
            anchor_y="center",
            align="center",
        )

        return False

    def _set_description_draw(self, card: SelectCardSprite):
        return True

    def _set_consequence_draw(self, card: SelectCardSprite):
        if not self.consequence_card:
            self.consequence_card = card

        if not self.set_consequence_at:
            self.set_consequence_at = datetime.now()

        if self.after_consequence:
            return True

        arcade.draw_rectangle_filled(
            card.center_x,
            card.center_y,
            card.width,
            card.height,
            (0, 0, 0, 100),
        )

        start_x = card.center_x
        start_y = card.center_y
        lr_shift = 30

        arcade.draw_text(
            card.get_consequence(),
            start_x,
            start_y,
            width=math.floor(card.width) - lr_shift,
            multiline=True,
            anchor_y="center",
            anchor_x="center",
        )

        return False

    def _set_turnover_draw(self, card: SelectCardSprite):
        if not self.turnover_card:
            return True

        if not self.chosen_card_texture_changed:
            alpha = 255
            alpha_speed = 3

        else:
            alpha = 0
            alpha_speed = -3

        if self.chosen_effect_finish:
            if not self.chosen_card_texture_changed:
                if self.turnover_alpha < alpha:
                    if self.turnover_alpha + alpha_speed > alpha:
                        self.turnover_alpha += alpha - self.turnover_alpha

                    else:
                        self.turnover_alpha += alpha_speed
            else:
                if self.turnover_alpha > alpha:
                    if self.turnover_alpha + alpha_speed < alpha:
                        self.turnover_alpha -= self.turnover_alpha - alpha

                    else:
                        self.turnover_alpha += alpha_speed

                if self.turnover_card == 0:
                    self.turnover_card.remove_from_sprite_lists()

            self.turnover_card.center_x = card.center_x
            self.turnover_card.center_y = card.center_y
            self.turnover_card.scale = card.scale
            self.turnover_card.width = card.width
            self.turnover_card.height = card.height
            self.turnover_card.alpha = self.turnover_alpha

            self.turnover_card.draw()

        return False

    def _set_turnover_update(self, card: SelectCardSprite):
        if self.chosen_card_texture_changed or not self.turnover_card:
            self.set_consequence(card)
            self.set_round_end_tip(card)
            return True

        if self.chosen_effect_finish:
            self.turnover_card.update_animation()

            if self.turnover_card.alpha >= 255 and not self.chosen_card_texture_changed:
                card.set_to_consequence_texture()

                card.center_x = self.event_card.center_x
                card.center_y = self.event_card.center_y
                card.width = self.event_card.width
                card.height = self.event_card.height

                self.chosen_card_texture_changed = True
                self.event_card.remove_from_sprite_lists()

        return False

    def _set_chosen(self, card):
        speed = 15
        expand_speed = 5

        if (
            card.center_x == self.event_card.center_x
            and card.center_y == self.event_card.center_y
            and card.height == self.event_card.height
            and card.width == self.event_card.width
        ):
            card.center_x = self.event_card.center_x
            card.center_y = self.event_card.center_y
            card.width = self.event_card.width
            card.height = self.event_card.height

            self.game_view.manager.process_decision(card.index)
            return True

        if card.center_x != self.event_card.center_x:
            if card.center_x < self.event_card.center_x:
                if card.center_x + speed > self.event_card.center_x:
                    card.change_x = self.event_card.center_x - card.center_x
                elif card.center_x + speed < self.event_card.center_x:
                    card.change_x = speed
            elif card.center_x > self.event_card.center_x:
                if card.center_x - speed < self.event_card.center_x:
                    card.change_x = -(
                        abs(card.center_x) - abs(self.event_card.center_x)
                    )
                elif card.center_x - speed > self.event_card.center_x:
                    card.change_x = -speed

        if card.center_y != self.event_card.center_y:
            if card.center_y < self.event_card.center_y:
                if card.center_y + speed > self.event_card.center_y:
                    card.change_y = self.event_card.center_y - card.center_y
                elif card.center_y + speed < self.event_card.center_y:
                    card.change_y = speed
            elif card.center_y > self.event_card.center_y:
                if card.center_y - speed < self.event_card.center_y:
                    card.change_y = -(
                        abs(card.center_y) - abs(self.event_card.center_y)
                    )
                elif card.center_y - speed > self.event_card.center_y:
                    card.change_y = -speed

        if card.width != self.event_card.width:
            if card.width + expand_speed > self.event_card.width:
                card.width += self.event_card.width - card.width

            else:
                card.width += expand_speed

        if card.height != self.event_card.height:
            if card.height + expand_speed > self.event_card.height:
                card.height += self.event_card.height - card.height

            else:
                card.height += expand_speed

        self.chosen_effect_finish = True

        return False

    def _unset_hover(self, card):
        speed = 10

        card.hover_start = False

        if card.center_y == card.start_y or card.hovered:
            card.hovered = False
            return True

        if card.center_y - speed < card.start_y:
            card.change_y = card.start_y - card.center_y
        else:
            card.change_y = -speed

        return False

    def _set_hover(self, card):
        card.hover_start = True

        speed = card.height / 2
        target_y = card.start_y + speed

        card.hovered_at = datetime.now()

        if card.center_y == target_y:
            card.hovered = True
            return True

        if card.center_y + speed > target_y:
            card.center_y = target_y - card.center_y
        else:
            card.change_y = speed

        return False

    def _set_hide(self, card):
        card.change_y -= self.default_speed

        if card.top < 0:  # remove after off screen
            card.remove_from_sprite_lists()

            if self.after_consequence:
                self.after_consequence_end = True
            return True

        return False

    def _set_show(self, card):
        if card.center_y + self.default_speed > card.start_y:
            card.change_y = card.start_y - card.center_y
            return True

        card.change_y = self.default_speed

        return False

    def _set_to_start(self, card):
        if card.start_x == card.center_x and card.start_y == card.center_y:
            return True

        if card.center_x != card.start_x:
            if card.center_x < card.start_x:
                if card.center_x + self.default_speed > card.start_x:
                    card.change_x = card.start_x - card.center_x
                elif card.center_x + self.default_speed < card.start_x:
                    card.change_x = self.default_speed
            elif card.center_x > card.start_x:
                if card.center_x - self.default_speed < card.start_x:
                    card.change_x = -(abs(card.center_x) - abs(card.start_x))
                elif card.center_x - self.default_speed > card.start_x:
                    card.change_x = -self.default_speed

        if card.center_y != card.start_y:
            if card.center_y < card.start_y:
                if card.center_y + self.default_speed > card.start_y:
                    card.change_y = card.start_y - card.center_y
                elif card.center_y + self.default_speed < card.start_y:
                    card.change_y = self.default_speed
            elif card.center_y > card.start_y:
                if card.center_y - self.default_speed < card.start_y:
                    card.change_y = -(abs(card.center_y) - abs(card.start_y))
                elif card.center_y - self.default_speed > card.start_y:
                    card.change_y = -self.default_speed

        return False
