import arcade

from sgj.game_manager import GameManager


class AngryStat:
    BAR_WIDTH = 500
    BAR_HEIGHT = 20
    BAR_TOP_OFFSET = 10

    def __init__(self, manager, window):
        self.manager: GameManager = manager
        self.center_x = window.width / 2
        self.center_y = window.height - self.BAR_HEIGHT - self.BAR_TOP_OFFSET

    def draw_bar(self):
        if self.manager.angry < self.manager.angry_min_max[1]:
            arcade.draw_rectangle_filled(
                center_x=self.center_x,
                center_y=self.center_y,
                width=self.BAR_WIDTH,
                height=self.BAR_HEIGHT,
                color=arcade.color.GREEN,
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
        )
