import math

import arcade

from sgj.game_manager import GameManager


class FatumStat:
    BAR_WIDTH = 500
    BAR_HEIGHT = 45
    BAR_OFFSET = (10 * 2) + BAR_HEIGHT
    BAR_ANGLE = 90

    def __init__(self, manager, window):
        self.manager: GameManager = manager
        self.center_x = window.width - self.BAR_HEIGHT - self.BAR_OFFSET
        self.center_y = window.height / 2

    def draw_current_value(self):
        max_len = len(str(self.manager.energy_min_max[1]))
        arcade.draw_text(
            f"{math.floor(self.manager.fatum):{max_len}}/{self.manager.fatum_min_max[1]}",
            self.center_x,
            self.center_y,
            rotation=self.BAR_ANGLE,
            color=arcade.color.BLACK,
            font_size=15,
            anchor_y="center",
            anchor_x="center",
        )

    def draw_bar(self):
        if self.manager.fatum < self.manager.fatum_min_max[1]:
            arcade.draw_rectangle_filled(
                center_x=self.center_x,
                center_y=self.center_y,
                width=self.BAR_WIDTH,
                height=self.BAR_HEIGHT,
                color=(*arcade.color.BLACK, 30),
                tilt_angle=self.BAR_ANGLE,
            )

        if self.manager.fatum > self.manager.fatum_min_max[0]:
            health_width = self.BAR_WIDTH * (
                self.manager.fatum / self.manager.fatum_min_max[1]
            )

            arcade.draw_rectangle_filled(
                center_x=self.center_x,
                center_y=self.center_y - 0.5 * (self.BAR_WIDTH - health_width),
                width=health_width,
                height=self.BAR_HEIGHT,
                color=(*arcade.color.VIOLET, 60),
                tilt_angle=self.BAR_ANGLE,
            )

        self.draw_current_value()
