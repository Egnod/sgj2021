import math

import arcade

from sgj.game_manager import GameManager


class AngryStat:
    BAR_WIDTH = 500
    BAR_HEIGHT = 45
    BAR_OFFSET = 10
    BAR_ANGLE = 0

    def __init__(self, manager, window):
        self.manager: GameManager = manager
        self.center_x = window.width / 2
        self.center_y = window.height - self.BAR_HEIGHT - self.BAR_OFFSET

    def draw_current_value(self):
        arcade.draw_text(
            f"{math.floor(self.manager.angry)}/{self.manager.angry_min_max[1]}",
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
        if self.manager.angry < self.manager.angry_min_max[1]:
            arcade.draw_rectangle_filled(
                center_x=self.center_x,
                center_y=self.center_y,
                width=self.BAR_WIDTH,
                height=self.BAR_HEIGHT,
                color=(*arcade.color.BLACK, 30),
                tilt_angle=self.BAR_ANGLE,
            )

        health_width = self.BAR_WIDTH * (
            self.manager.angry / self.manager.angry_min_max[1]
        )

        arcade.draw_rectangle_filled(
            center_x=self.center_x - 0.5 * (self.BAR_WIDTH - health_width),
            center_y=self.center_y,
            width=health_width,
            height=self.BAR_HEIGHT,
            color=arcade.color.RED,
            tilt_angle=self.BAR_ANGLE,
        )

        self.draw_current_value()
