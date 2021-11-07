import math

import arcade
from pyglet.input import Joystick


class SelectCardSprite(arcade.Sprite):
    """
    Sprite that represents our select card.

    Derives from arcade.Sprite.
    """

    def __init__(
        self,
        filename,
        scale,
        joystick,
        index,
        selects_count,
        event_card,
        card_meta,
        is_available,
    ):
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

        self.card_meta = card_meta

        # TODO: card.card_meta["consequence"]["sprite"]
        self.consequence_texture = arcade.load_texture(
            "./GameData/Images/Interface/card_texture.png",
        )

        self.remove = False
        self.for_show = False
        self.to_start = False

        self.start_y = None
        self.start_x = None

        self.event_card = event_card

        self.chosen = False
        self.hovered = False
        self.hovered_at = None
        self.hover_start = True

        self.is_available = is_available

        # self.card_message = arcade.Sprite("./GameData/Images/Interface/card_message.jpg")

    def get_description(self):
        if self.is_available:
            return self.card_meta["description"]

        else:
            return "Не хватает ресурсов (энергия/фатум)"

    def get_consequence(self):
        return self.card_meta["consequence"]["text"]

    def set_to_consequence_texture(self):
        self.append_texture(self.consequence_texture)

        self.set_texture(-1)

    def draw(self, *, filter=None, pixelated=None, blend_function=None):
        super(SelectCardSprite, self).draw(
            filter=filter,
            pixelated=pixelated,
            blend_function=blend_function,
        )

        if self.chosen:
            return

        arcade.draw_rectangle_filled(
            self.center_x,
            self.center_y,
            self.width,
            self.height,
            (0, 0, 0, 100),
        )

        start_x = self.center_x
        start_y = self.center_y + self.width / 2
        lr_shift = 30

        arcade.draw_text(
            self.get_description(),
            start_x,
            start_y,
            width=math.floor(self.width) - lr_shift,
            multiline=True,
            anchor_y="top",
            anchor_x="center",
            color=arcade.color.WHITE,
        )

    def update(self):
        """
        Update card state.
        """
        super().update()

        self.stop()
