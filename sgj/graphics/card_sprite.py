import arcade
from pyglet.input import Joystick

from sgj.graphics.constants import *


class CardSprite(arcade.Sprite):
    """
    Sprite that represents our main card.

    Derives from arcade.Sprite.
    """

    def __init__(self, filename, scale, joystick):
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

        # Mark that we are respawning.
        self.respawn()

    def respawn(self):
        """
        Called when we die and need to make a new ship.
        'respawning' is an invulnerability timer.
        """
        # If we are in the middle of respawning, this is non-zero.
        self.respawning = 1
        self.center_x = SCREEN_WIDTH / 2
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
            if self.center_y + self.speed > SCREEN_HEIGHT / 2:
                self.change_y = SCREEN_HEIGHT / 2 - self.center_y
                self.for_show = False
            else:
                self.change_y = self.speed

        else:
            self.stop()

        """ Call the parent class. """
        super().update()
