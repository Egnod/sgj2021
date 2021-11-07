import arcade
import arcade.gui

from sgj.game_manager import GameManager
from sgj.graphics.game_view import GameView


class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()


class StartView(arcade.View):
    def __init__(self, window=None):
        super().__init__(window)

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.v_box = arcade.gui.UIBoxLayout()

        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        quit_button = QuitButton(text="Quit", width=200)
        self.v_box.add(quit_button)

        start_button.on_click = self.on_click_start

        self.back_sound = arcade.Sound("./GameData/Sounds/menu_sound.wav")
        self.player = None

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box,
            ),
        )

    def on_click_start(self, event):
        game_view = GameView(GameManager("./GameData/GameData.json"))
        game_view.start_new_game(1)

        self.back_sound.stop(self.player)
        self.window.show_view(game_view)

    def on_show(self):
        """This is run once when we switch to this view"""
        arcade.set_background_color(arcade.csscolor.BLACK)
        self.player = self.back_sound.play(0.25)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_draw(self):
        """Draw this view"""
        arcade.start_render()
        self.manager.draw()
