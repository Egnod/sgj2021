import math

import arcade


class VolumeStat:
    BAR_WIDTH = 200
    BAR_HEIGHT = 45
    BAR_OFFSET = 10
    BAR_ANGLE = 0

    def __init__(self, game_view, window):
        self.game_view = game_view
        self.center_x = window.width / 16
        self.center_y = window.height - self.BAR_HEIGHT - self.BAR_OFFSET

    def draw_current_value(self):
        arcade.draw_text(
            f"{math.floor(self.game_view.volume)}%",
            self.center_x,
            self.center_y,
            rotation=self.BAR_ANGLE,
            color=arcade.color.BLACK,
            font_size=15,
            width=self.BAR_WIDTH,
            anchor_x="center",
            anchor_y="center",
        )

    def draw_bar(self):
        arcade.draw_rectangle_filled(
            center_x=self.center_x,
            center_y=self.center_y,
            width=self.BAR_WIDTH,
            height=self.BAR_HEIGHT,
            color=(*arcade.color.BLACK, 30),
            tilt_angle=self.BAR_ANGLE,
        )

        volume_width = self.BAR_WIDTH * (self.game_view.volume / 100)

        arcade.draw_rectangle_filled(
            center_x=self.center_x - 0.5 * (self.BAR_WIDTH - volume_width),
            center_y=self.center_y,
            width=volume_width,
            height=self.BAR_HEIGHT,
            color=arcade.color.GREEN,
            tilt_angle=self.BAR_ANGLE,
        )

        self.draw_current_value()
