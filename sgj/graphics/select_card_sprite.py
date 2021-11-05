import math

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

        # Mark that we are respawning.
        self.respawn()

    def respawn(self):
        """
        Called when we die and need to make a new ship.
        'respawning' is an invulnerability timer.
        """
        # If we are in the middle of respawning, this is non-zero.
        self.respawning = 1
        print(self.index, math.floor(self.selects_count / 2))

        if self.selects_count % 2:
            self.center_x = SCREEN_WIDTH / 2

            if self.index < math.floor(self.selects_count / 2):
                self.center_x -= (self.width * self.index) * self.selects_count

            elif self.index > math.floor(self.selects_count / 2):
                self.center_x += (self.width * self.index) * self.selects_count

        else:
            self.center_x = SCREEN_WIDTH / 2 - self.width * self.selects_count

            if self.index < math.floor(self.selects_count / 2):
                self.center_x -= (self.width * self.index) * self.selects_count

            elif self.index > math.floor(self.selects_count / 2):
                self.center_x += (self.width * self.index) * self.selects_count

        self.center_y = -self.height
        self.angle = 0

        self.show()

    def hide(self):
        """
        Hide card after use.
        """
        self.thrust = 30
        self.remove = True

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

        if self.remove:
            self.change_x = self.speed

            if self.left > SCREEN_WIDTH:  # remove after off screen
                self.remove_from_sprite_lists()

        elif self.for_show:
            if self.center_y + self.speed > (self.height + 20):
                self.change_y = (self.height + 20) - self.center_y
                self.for_show = False
            else:
                self.change_y = self.speed

        else:
            self.stop()

        """ Call the parent class. """
        super().update()
