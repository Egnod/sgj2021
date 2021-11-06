from functools import partial

from sgj.graphics.constants import SCREEN_WIDTH, SELECT_CARD_SCALE, HORIZONTAL_CARDS_PADDING


class SelectCardController:
    def __init__(self, event_card, cards):
        self.default_speed = 30  # Default speed for any card actions

        self.event_card = event_card
        self.cards = cards

        self.events_stack = []

    def render_events(self):
        new_stack = []

        for event in self.events_stack:
            result = event()

            if not result:
                new_stack.append(event)

        self.events_stack = new_stack

    def pre_render(self):
        PADDING = SCREEN_WIDTH * HORIZONTAL_CARDS_PADDING
        chunk_size = (SCREEN_WIDTH - PADDING * 2) / len(self.cards)
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
        if not card.hovered:
            card.hovered = True
            self.events_stack.append(partial(self._set_hover, card))

    def unset_hover(self, card):
        """
        Actions on card un-hover.
        """
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

    def _set_chosen(self, card):
        speed = 15
        expand_speed = 5

        if (
            card.center_x == self.event_card.center_x
            and card.center_y == self.event_card.center_y
            and card.height == self.event_card.height
            and card.width == self.event_card.width
        ):
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

        return False

    def _unset_hover(self, card):
        speed = 10

        if card.center_y == card.start_y:
            return True

        if card.center_y - speed < card.start_y:
            card.change_y = card.start_y - card.center_y
        else:
            card.change_y = -speed

        return False

    def _set_hover(self, card):
        speed = 10
        target_y = card.start_y + 30

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
