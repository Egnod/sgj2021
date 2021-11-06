import arcade
from arcade.experimental import Shadertoy

from sgj.game_manager import GameManager
from sgj.graphics.constants import *
from sgj.graphics.entity.card.sprite import CardSprite
from sgj.graphics.entity.news.news import News
from sgj.graphics.entity.select.controller import SelectCardController
from sgj.graphics.entity.select.sprite import SelectCardSprite
from sgj.graphics.entity.stats.angry import AngryStat


class GameView(arcade.View):
    """Main application class."""

    def __init__(self, manager: GameManager):
        super().__init__()

        self.game_over = False

        self.card_chosen = False

        self.manager = manager

        # Sprite lists
        self.card_sprite_list = arcade.SpriteList()
        self.select_card_sprite_list = arcade.SpriteList(use_spatial_hash=True)
        self.select_cards_controller: SelectCardController = SelectCardController(
            None,
            [],
        )
        self.select_cards_controller.set_game_view(self)

        self.held_card = None

        self.check_unheld = None

        self.shadertoy = Shadertoy.create_from_file(
            self.window.get_size(),
            "./GameData/Shaders/bg.glsl",
        )

        self.angry_stat = AngryStat(manager, self.window)

        self.news = News()

        self.shadertoy_time = 0.0

        for joystick in self.window.joysticks:
            joystick.push_handlers(self)

    def start_new_game(self, player_count):
        """Set up the game and initialize the variables."""

        self.game_over = False

        self.card_chosen = False

        # Sprite lists
        self.card_sprite_list = arcade.SpriteList()
        self.select_card_sprite_list = arcade.SpriteList(use_spatial_hash=True)
        self.select_cards_controller: SelectCardController = SelectCardController(
            None,
            [],
        )
        self.select_cards_controller.set_game_view(self)

        self.held_card = None

        self.check_unheld = None

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        self.window.use()
        self.window.clear()

        self.shadertoy_time += 0.01


        self.card_sprite_list.draw()
        self.select_card_sprite_list.draw()
        self.select_cards_controller.draw_events()

        self.angry_stat.draw_bar()

        self.news.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """Called when the user presses a mouse button."""

        cards = arcade.get_sprites_at_point((x, y), self.select_card_sprite_list)

        card = next(iter(cards), None)

        if (
            card
            and not self.card_chosen
            and self.manager.is_decision_available(card.index)
        ):
            self.held_card = card
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
                card = cards[-1]

                if not card.hover_start:
                    self.select_cards_controller.set_hover(card)
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

        if self.card_chosen:
            return None

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
            self.select_cards_controller.set_turnover(selected_card)

            for card in self.select_card_sprite_list:
                if card != selected_card:
                    self.select_cards_controller.set_hide(card)

        if self.held_card:
            self.held_card = None

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            if self.news.is_blocking_other():
                self.news.deactivate()
            else:
                self.news.activate("123")

    def on_update(self, x):
        """Move everything"""

        if self.game_over:
            return

        if not self.card_sprite_list:
            if len(self.window.joysticks) > 0:
                joystick = self.window.joysticks[0]
            else:
                joystick = None

            event = self.manager.get_next_event()

            card_sprite = CardSprite(
                "./sgj/graphics/assets/sprites/cards/test.png",  # event["sprite"]
                EVENT_CARD_SCALE,
                joystick,
            )
            self.card_sprite_list.append(card_sprite)

            select_cards_sprite = [
                SelectCardSprite(
                    "./GameData/Images/Events/Village accident/dec4.png",
                    SELECT_CARD_SCALE,
                    joystick,
                    index=index,
                    selects_count=len(card_sprite.select_cards),
                    event_card=card_sprite,
                    card_meta=card,
                    is_available=self.manager.is_decision_available(index),
                )
                for index, card in enumerate(event["decisions"])
            ]

            self.select_card_sprite_list.extend(select_cards_sprite)

            self.select_cards_controller.cards = self.select_card_sprite_list
            self.select_cards_controller.event_card = self.card_sprite_list[0]

            self.select_cards_controller.pre_render()

        self.news.update()
        # Не рисуем ничего больше пока есть новости
        # TODO: может, надо просто блочить клики
        # TODO: if self.game_manager.get_news()
        if self.news.is_blocking_other():
            return

        self.card_sprite_list.update()
        self.select_card_sprite_list.update()
        self.select_cards_controller.render_events()
