import arcade

from sgj.graphics.constants import *
from sgj.graphics.start_view import StartView
from sgj.graphics.window import Window


def main():
    """Start the game"""

    # Load fonts
    arcade.load_font("./sgj/graphics/assets/fonts/arcade.ttf")
    arcade.load_font("./sgj/graphics/assets/fonts/SF Atarian System.ttf")

    window = Window(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        SCREEN_TITLE,
        resizable=False,
        antialiasing=False,
    )
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
