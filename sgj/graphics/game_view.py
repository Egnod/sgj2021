import arcade

from sgj.graphics.card_sprite import CardSprite
from sgj.graphics.constants import *
from sgj.graphics.select_card_controller import SelectCardController
from sgj.graphics.select_card_sprite import SelectCardSprite


class GameView(arcade.View):
    """Main application class."""

    def __init__(self):
        super().__init__()

        self.game_over = False

        self.card_chosen = False

        # Sprite lists
        self.card_sprite_list = arcade.SpriteList()
        self.select_card_sprite_list = arcade.SpriteList(use_spatial_hash=True)
        self.select_cards_controller = None
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
        #  self.background = arcade.load_texture("./sgj/graphics/assets/imgs/bg.gif")

        # Sprite lists
        self.card_sprite_list = arcade.SpriteList()

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        self.card_sprite_list.draw()
        self.select_card_sprite_list.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """Called when the user presses a mouse button."""

        cards = arcade.get_sprites_at_point((x, y), self.select_card_sprite_list)

        if len(cards) > 0 and not self.card_chosen:
            self.held_card = cards[-1]
            self.select_cards_controller.set_selected_scale(self.held_card)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """User moves mouse"""
        # If we are holding cards, move them with the mouse
        if card := self.held_card:
            card.center_x += dx
            card.center_y += dy

        elif not self.card_chosen:
            cards = arcade.get_sprites_at_point((x, y), self.select_card_sprite_list)

            if len(cards) > 0:
                self.select_cards_controller.set_hover(cards[-1])
            else:
                for card in self.select_card_sprite_list:
                    if not card.chosen:
                        self.select_cards_controller.unset_hover(card)

    def on_mouse_release(
        self,
        x: float,
        y: float,
        button: int,
        modifiers: int,
    ):
        """Called when the user presses a mouse button."""

        selected_card = None

        if self.held_card and arcade.check_for_collision_with_list(
            self.held_card,
            self.card_sprite_list,
        ):
            selected_card = self.held_card

        if not selected_card:
            for card in self.select_card_sprite_list:
                self.select_cards_controller.set_to_start(card)
                self.select_cards_controller.set_default_scale(card)
        else:
            self.card_chosen = True
            self.select_cards_controller.set_chosen(selected_card)

            for card in self.select_card_sprite_list:
                if card != selected_card:
                    self.select_cards_controller.set_hide(card)

        if self.held_card:
            self.held_card = None

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
                    event_card=card_sprite,
                )
                for index, card in enumerate(card_sprite.select_cards)
            ]

            self.select_card_sprite_list.extend(select_cards_sprite)

            self.select_cards_controller = SelectCardController(
                self.card_sprite_list[0],
                self.select_card_sprite_list,
            )

            self.select_cards_controller.pre_render()

        self.card_sprite_list.update()
        self.select_card_sprite_list.update()
        self.select_cards_controller.render_events()
