from datetime import datetime
from functools import partial
from typing import List

import arcade

from sgj.graphics.constants import (
    HORIZONTAL_CARDS_PADDING,
    SELECT_CARD_SCALE,
)
from sgj.graphics.entity.select.sprite import SelectCardSprite


class SelectCardController:
    def __init__(self, event_card, cards):
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

        self.game_view = None

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
            card.start_y = card.height + 20

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
        if not card.hovered and (
            not card.hovered_at
            or (datetime.now() - card.hovered_at).total_seconds() > 0.05
        ):
            card.hovered = True
            self.events_stack.append(partial(self._set_hover, card))

    def unset_hover(self, card):
        """
        Actions on card un-hover.
        """
        if (
            card.hovered_at
            and (datetime.now() - card.hovered_at).total_seconds() < 0.05
        ):
            return None

        card.hovered = False
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
        card.scale = 0.4

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

    def _set_turnover_draw(self, card: SelectCardSprite):
        if not self.turnover_card:
            return True

        if not self.chosen_card_texture_changed:
            alpha = 255
            alpha_speed = 5

        else:
            alpha = 0
            alpha_speed = -5

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
            return True

        if self.chosen_effect_finish:
            self.turnover_card.update_animation()

            if self.turnover_card.alpha >= 255 and not self.chosen_card_texture_changed:
                texture = arcade.load_texture(
                    "./sgj/graphics/assets/sprites/cards/des4.png",
                )
                card.append_texture(texture)
                card.set_texture(1)

                card.center_x = self.event_card.center_x
                card.center_y = self.event_card.center_y
                card.width = self.event_card.width
                card.height = self.event_card.height

                self.chosen_card_texture_changed = True

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

        if card.center_y == card.start_y or card.hovered:
            return True

        if card.center_y - speed < card.start_y:
            card.change_y = card.start_y - card.center_y
        else:
            card.change_y = -speed

        return False

    def _set_hover(self, card):
        speed = 10
        target_y = card.start_y + 30

        card.hovered_at = datetime.now()

        if card.center_y == target_y:
            return True

        if card.center_y + speed > target_y:
            card.center_y = target_y - card.center_y
        else:
            card.change_y = speed

        return False

    def _set_hide(self, card):
        card.change_y -= self.default_speed

        if card.bottom < 0:  # remove after off screen
            card.remove_from_sprite_lists()
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
