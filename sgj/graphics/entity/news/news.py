import arcade


class News:
    def __init__(self):
        TEXTURE_PATH = "./sgj/graphics/assets/sprites/news_back.png"
        self.TEXT_AREA_WIDTH_SIZE = 0.6
        self.TEXT_AREA_HEIGHT_SIZE = 0.75
        self.MOVING_SPEED = 10

        self.news_back = arcade.Sprite(TEXTURE_PATH, scale=1)
        self._setup_pos(self.news_back)
        self.news_back.position = self.pos_hidden
        self.pos_target = self.pos_hidden

        self.text = ""
        self._is_blocking_other = False

    def _setup_pos(self, back_image: arcade.Sprite):
        x_pos = arcade.get_window().width // 2
        half_height = back_image.height // 2
        self.pos_hidden = x_pos, arcade.get_window().height + half_height
        self.pos_shown = x_pos, arcade.get_window().height - half_height + 100

    def is_blocking_other(self):
        return self._is_blocking_other

    def activate(self):
        self._is_blocking_other = True
        self.pos_target = self.pos_shown

    def deactivate(self):
        self._is_blocking_other = False
        self.pos_target = self.pos_hidden

    def set_text(self, text: str):
        self.text = text

    def draw(self):
        self.news_back.draw()

        text_x = (
            self.news_back.left
            + self.news_back.width * (1 - self.TEXT_AREA_WIDTH_SIZE) // 2
        )
        text_y = (
            self.news_back.bottom + self.news_back.height * self.TEXT_AREA_HEIGHT_SIZE
        )
        text_width = int(self.news_back.width * self.TEXT_AREA_WIDTH_SIZE)
        arcade.draw_text(
            self.text,
            text_x,
            text_y,
            multiline=True,
            width=text_width,
            color=arcade.color.BLACK,
        )

    def _move_to_target(self):
        if self.news_back.position == self.pos_target:
            return
        if self.news_back.center_y >= self.pos_target[1]:
            self.news_back.center_y += (
                self.MOVING_SPEED
                if self.pos_target[1] > self.news_back.center_y
                else -self.MOVING_SPEED
            )
            return
        self.news_back.position = self.pos_target

    def update(self):
        self._move_to_target()
