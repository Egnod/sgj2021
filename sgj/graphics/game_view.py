import arcade

from sgj.graphics.card_sprite import CardSprite
from sgj.graphics.constants import *
from sgj.graphics.select_card_sprite import SelectCardSprite


class GameView(arcade.View):
    """Main application class."""

    def __init__(self):
        super().__init__()

        self.game_over = False
        self.background = None

        # Sprite lists
        self.card_sprite_list = arcade.SpriteList()
        self.select_card_sprite_list = arcade.SpriteList()
        self.held_card = None

        # Sounds
        self.laser_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound1 = arcade.load_sound(":resources:sounds/explosion1.wav")
        self.hit_sound2 = arcade.load_sound(":resources:sounds/explosion2.wav")
        self.hit_sound3 = arcade.load_sound(":resources:sounds/hit1.wav")
        self.hit_sound4 = arcade.load_sound(":resources:sounds/hit2.wav")

        self.explosion_list = []

        self.check_unheld = None

        for joystick in self.window.joysticks:
            joystick.push_handlers(self)

    def start_new_game(self, player_count):
        """Set up the game and initialize the variables."""

        self.game_over = False
        arcade.set_background_color(arcade.csscolor.BLACK)
        self.background = arcade.load_texture("./sgj/graphics/assets/imgs/bg.gif")

        # Sprite lists
        self.card_sprite_list = arcade.SpriteList()

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        arcade.draw_lrwh_rectangle_textured(
            0,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            self.background,
        )

        self.card_sprite_list.draw()
        self.select_card_sprite_list.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """Called when the user presses a mouse button."""

        cards = arcade.get_sprites_at_point((x, y), self.select_card_sprite_list)

        if len(cards) > 0:
            self.held_card = cards[-1]

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """User moves mouse"""

        # If we are holding cards, move them with the mouse
        if card := self.held_card:
            card.center_x += dx
            card.center_y += dy

    def on_mouse_release(
        self,
        x: float,
        y: float,
        button: int,
        modifiers: int,
    ):
        """Called when the user presses a mouse button."""

        if self.held_card:
            self.check_unheld = self.held_card
            self.held_card = None

    def on_key_press(self, symbol, modifiers):
        """Called whenever a key is pressed."""

    def on_update(self, x):
        """Move everything"""

        if self.game_over:
            return

        if not self.card_sprite_list:
            if len(self.window.joysticks) > 0:
                joystick = self.window.joysticks[0]
            else:
                joystick = None

            card_sprite = CardSprite(
                "./sgj/graphics/assets/sprites/cards/test.png",
                SCALE,
                joystick,
            )
            self.card_sprite_list.append(card_sprite)

            select_cards_sprite = [
                SelectCardSprite(
                    card,
                    SELECT_CARD_SCALE,
                    joystick,
                    index=index,
                    selects_count=len(card_sprite.select_cards),
                )
                for index, card in enumerate(card_sprite.select_cards)
            ]

            self.select_card_sprite_list.extend(select_cards_sprite)

        elif self.check_unheld:
            selected_card = None

            if arcade.check_for_collision_with_list(
                self.check_unheld,
                self.card_sprite_list,
            ):
                selected_card = self.check_unheld

            if not selected_card:
                for card in self.select_card_sprite_list:
                    card.check_or_move_to_start()

            self.check_unheld = None

        self.card_sprite_list.update()
        self.select_card_sprite_list.update()
