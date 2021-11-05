
import arcade
from pyglet.input import Joystick

from sgj.graphics.constants import *


class SelectCardSprite(arcade.Sprite):
    """
    Sprite that represents our select card.

    Derives from arcade.Sprite.
    """

    def __init__(self, filename, scale, joystick, index, selects_count):
        """Set up the space ship."""

        # Call the parent Sprite constructor
        super().__init__(filename, scale)

        # Info on where we are going.
        # Angle comes in automatically from the parent class.
        self.index = index
        self.selects_count = selects_count
        self.thrust = 0
        self.speed = 0
        self.max_speed = 30
        self.drag = 0.05
        self.respawning = 0
        self.joystick: Joystick = joystick

        self.remove = False
        self.for_show = False
        self.to_start = False

        self.start_y = None
        self.start_x = None

        self.show_primary_card = False
        self.show_primary_card_setted = False
        self.show_primary_card_setted_at = None

        self.selected_effect = False

        self.unshow_primary_card = False

        # Mark that we are respawning.
        self.respawn()

    def respawn(self):
        """
        Called when we die and need to make a new ship.
        'respawning' is an invulnerability timer.
        """
        # If we are in the middle of respawning, this is non-zero.
        self.respawning = 1

        chunk_size = SCREEN_WIDTH / self.selects_count
        pos_shift = chunk_size / 2
        self.start_x = self.center_x = chunk_size * self.index + pos_shift

        self.center_y = -self.height

        self.angle = 0

        self.show()

    @property
    def selected_target_y(self):
        return self.start_y + 30 if self.start_y else 0

    def check_or_move_to_start(self):
        self.thrust = 30
        self.to_start = True

    def hide(self):
        """
        Hide card after use.
        """
        self.thrust = 30
        self.remove = True

    def set_primary_card(self):
        """
        Show primary card.
        """

        if self.center_y != self.start_y:
            return None

        self.show_primary_card = True
        self.show_primary_card_setted = False

    def unset_primary_card(self):
        """
        Unshow primary card.
        """

        if self.center_y != self.selected_target_y:
            return None

        self.show_primary_card = False
        self.show_primary_card_setted = False
        self.unshow_primary_card = True

    def wipe_primary_card_actions(self):
        """
        Wipe all primary properties.
        """
        self.show_primary_card = False
        self.show_primary_card_setted = False
        self.unshow_primary_card = False

    def set_selected_card(self):
        self.scale = 0.4

    def unset_selected_card(self):
        self.scale = SELECT_CARD_SCALE

    def show(self):
        """
        Show card for use.
        """

        self.thrust = 30
        self.for_show = True

    def update(self):
        """
        Update card state.
        """

        if self.speed > 0:
            self.speed -= self.drag
            if self.speed < 0:
                self.speed = 0

        if self.speed < 0:
            self.speed += self.drag
            if self.speed > 0:
                self.speed = 0

        self.speed += self.thrust
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < -self.max_speed:
            self.speed = -self.max_speed

        self.change_y = self.change_x = 0

        if self.remove:
            self.change_y = -self.speed

            if self.bottom < 0:  # remove after off screen
                self.remove_from_sprite_lists()

        elif self.for_show:
            if self.center_y + self.speed > (self.height + 20):
                self.change_y = (self.height + 20) - self.center_y
                self.start_y = self.center_y + self.change_y
                self.for_show = False
            else:
                self.change_y = self.speed

        elif self.to_start:
            self.change_y = self.change_x = 0

            if self.center_x != self.start_x:
                if self.center_x < self.start_x:
                    if self.center_x + self.speed > self.start_x:
                        self.change_x = self.start_x - self.center_x
                    elif self.center_x + self.speed < self.start_x:
                        self.change_x = self.speed
                elif self.center_x > self.start_x:
                    if self.center_x - self.speed < self.start_x:
                        self.change_x = -(abs(self.center_x) - abs(self.start_x))
                    elif self.center_x - self.speed > self.start_x:
                        self.change_x = -self.speed

            if self.center_y != self.start_y:
                if self.center_y < self.start_y:
                    if self.center_y + self.speed > self.start_y:
                        self.change_y = self.start_y - self.center_y
                    elif self.center_y + self.speed < self.start_y:
                        self.change_y = self.speed
                elif self.center_y > self.start_y:
                    if self.center_y - self.speed < self.start_y:
                        self.change_y = -(abs(self.center_y) - abs(self.start_y))
                    elif self.center_y - self.speed > self.start_y:
                        self.change_y = -self.speed

            if self.start_x == self.center_x and self.start_y == self.center_y:
                self.to_start = False

        elif self.show_primary_card and not self.show_primary_card_setted:
            self.speed = 10

            if self.center_y != self.selected_target_y:
                self.change_y = self.speed
            else:
                self.show_primary_card_setted = True

        elif self.unshow_primary_card:
            self.speed = 10

            if self.center_y != self.start_y:
                self.change_y = -self.speed
            else:
                self.unshow_primary_card = False

        else:
            self.stop()

        """ Call the parent class. """
        super().update()
