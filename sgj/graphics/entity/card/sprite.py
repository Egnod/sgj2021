import math

import arcade
from pyglet.input import Joystick

from sgj.graphics.constants import *


class CardSprite(arcade.Sprite):
    """
    Sprite that represents our main card.

    Derives from arcade.Sprite.
    """

    def __init__(self, filename, scale, joystick, card_meta):
        """Set up the space ship."""

        # Call the parent Sprite constructor
        super().__init__(filename, scale)

        # Info on where we are going.
        # Angle comes in automatically from the parent class.
        self.thrust = 0
        self.speed = 0
        self.max_speed = 30
        self.drag = 0.05
        self.respawning = 0
        self.joystick: Joystick = joystick
        self.remove = False
        self.for_show = False
        self.select_cards = [
            "./sgj/graphics/assets/sprites/cards/des1.png",
            "./sgj/graphics/assets/sprites/cards/des2.png",
            "./sgj/graphics/assets/sprites/cards/des3.png",
            "./sgj/graphics/assets/sprites/cards/des4.png",
        ]
        self.card_meta = card_meta
        print(card_meta)

        # Mark that we are respawning.
        self.respawn()

    def respawn(self):
        """
        Called when we die and need to make a new ship.
        'respawning' is an invulnerability timer.
        """
        # If we are in the middle of respawning, this is non-zero.
        self.respawning = 1
        self.center_x = arcade.get_window().width / 2
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

    def draw(self, *, filter=None, pixelated=None, blend_function=None):
        super(CardSprite, self).draw(
            filter=filter,
            pixelated=pixelated,
            blend_function=blend_function,
        )

        arcade.draw_rectangle_filled(
            self.center_x,
            self.center_y,
            self.width,
            self.height,
            (0, 0, 0, 100),
        )

        start_x = self.center_x
        start_y = self.center_y
        lr_shift = 30

        arcade.draw_text(
            self.card_meta["name"],
            start_x,
            start_y + math.floor(self.width / 1.5),
            width=math.floor(self.width) - lr_shift,
            multiline=True,
            anchor_y="center",
            anchor_x="center",
            align="center",
        )

        arcade.draw_text(
            self.card_meta["description"],
            start_x,
            start_y,
            width=math.floor(self.width) - lr_shift,
            multiline=True,
            anchor_y="center",
            anchor_x="center",
        )

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
            self.change_x = -self.speed

            if self.right < 0:  # remove after off screen
                self.remove_from_sprite_lists()

        elif self.for_show:
            if self.center_y + self.speed > SCREEN_HEIGHT / 2:
                self.change_y = SCREEN_HEIGHT / 2 - self.center_y
                self.for_show = False
            else:
                self.change_y = self.speed

        else:
            self.stop()

        """ Call the parent class. """
        super().update()
