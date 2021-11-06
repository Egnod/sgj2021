import arcade
from pyglet.input import Joystick


class SelectCardSprite(arcade.Sprite):
    """
    Sprite that represents our select card.

    Derives from arcade.Sprite.
    """

    def __init__(self, filename, scale, joystick, index, selects_count, event_card):
        """Set up the space ship."""

        # Call the parent Sprite constructor
        super().__init__(filename, scale)

        # Info on where we are going.
        # Angle comes in automatically from the parent class.
        self.index = index
        self.selects_count = selects_count
        self.thrust = 0
        self.speed = 30
        self.joystick: Joystick = joystick

        self.remove = False
        self.for_show = False
        self.to_start = False

        self.start_y = None
        self.start_x = None

        self.event_card = event_card

        self.chosen = False
        self.hovered = False
        self.hovered_at = None

    def update(self):
        """
        Update card state.
        """
        super().update()

        self.stop()
