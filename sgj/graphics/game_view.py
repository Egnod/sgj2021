import arcade
from arcade.experimental import Shadertoy

from sgj.game_manager import GameManager
from sgj.graphics.constants import *
from sgj.graphics.entity.Dude.dude import Dude
from sgj.graphics.entity.card.sprite import CardSprite
from sgj.graphics.entity.news.news import News
from sgj.graphics.entity.select.controller import SelectCardController
from sgj.graphics.entity.select.sprite import SelectCardSprite
from sgj.graphics.entity.stats.angry import AngryStat
from sgj.graphics.entity.stats.energy import EnergyStat
from sgj.graphics.entity.stats.fatum import FatumStat
from sgj.graphics.entity.stats.volume import VolumeStat
from sgj.sounds.sounds import play_effect, Effect, play_main_theme, set_volume, VOLUME


class GameView(arcade.View):
    """Main application class."""

    def __init__(self, manager: GameManager):
        super().__init__()

        self.game_over = False

        self.card_chosen = False

        self.manager = manager

        # Sprite lists
        self.card_sprite_list = arcade.SpriteList()
        self.select_card_sprite_list = arcade.SpriteList()
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
        self.volume_stat = VolumeStat(self, self.window)
        self.energy_stat = EnergyStat(manager, self.window)
        self.fatum_stat = FatumStat(manager, self.window)

        self.news = News()
        self.dude = Dude()

        self.volume_delta = 0

        self.background = arcade.load_texture("./GameData/Images/Interface/bg.png")

        self.back_sound = arcade.Sound("./GameData/Sounds/game_sound.wav")

        self.shadertoy_time = 0.0

        for joystick in self.window.joysticks:
            joystick.push_handlers(self)

    def start_new_game(self, player_count):
        """Set up the game and initialize the variables."""
        self.game_over = False
        play_main_theme()

        self.start_next_round()

    def start_next_round(self):
        self.manager.set_energy_round_charge()

        self.card_chosen = False

        # Sprite lists
        self.card_sprite_list = arcade.SpriteList()
        self.select_card_sprite_list = arcade.SpriteList()
        self.select_cards_controller: SelectCardController = SelectCardController(
            None,
            [],
        )
        self.select_cards_controller.set_game_view(self)

        self.held_card = None

        self.check_unheld = None

        event = self.manager.get_next_event()

        card_sprite = CardSprite(
            "./GameData/Images/Interface/card_texture.png",  # event["sprite"]
            EVENT_CARD_SCALE,
            None,
            card_meta=event,
        )
        self.card_sprite_list.append(card_sprite)

        select_cards_sprite = [
            SelectCardSprite(
                "./GameData/Images/Interface/card_texture.png",
                SELECT_CARD_SCALE,
                None,
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

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        self.window.background_color = arcade.color.WHITE

        self.window.use()
        self.window.clear()

        self.background.draw_scaled(
            self.window.width / 2,
            self.window.height / 2,
            self.window.height / self.background.height,
        )

        self.shadertoy_time += 0.01

        if self.card_sprite_list:
            self.card_sprite_list[0].draw()

        for card in self.select_card_sprite_list:
            card.draw()

        self.select_cards_controller.draw_events()

        global VOLUME
        if self.volume_delta != 0 and MAX_VOLUME >= VOLUME + self.volume_delta >= 0:
            new_volume = VOLUME + self.volume_delta
            set_volume(new_volume)

        self.volume_stat.draw_bar()
        self.angry_stat.draw_bar()
        self.energy_stat.draw_bar()
        self.fatum_stat.draw_bar()

        self.dude.draw()
        self.news.draw()

    def _process_new_round(self):
        if news := self.manager.get_news():
            play_effect(Effect.NEWS_QUICK)
            self.news.activate(*news)

            _, rewards = news
            self.dude.update_reaction_on_news(rewards)
        else:
            play_effect(Effect.EFFECT)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """Called when the user presses a mouse button."""
        play_effect(Effect.CLICK)

        if self.select_cards_controller.check_for_next_round():
            self._process_new_round()
            return

        cards = arcade.get_sprites_at_point((x, y), self.select_card_sprite_list)

        card = next(iter(cards), None)

        if (
            card
            and not self.card_chosen
            and self.manager.is_decision_available(card.index)
        ):
            self.held_card = card
            self.select_cards_controller.set_selected_scale(self.held_card)

        if self.news.is_blocking_other():
            self.news.deactivate()
            play_effect(Effect.TAP_SCROLL)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """User moves mouse"""
        # If we are holding cards, move them with the mouse

        if card := self.held_card:
            card.center_x += dx
            card.center_y += dy

        elif not self.card_chosen:
            cards = arcade.get_sprites_at_point((x, y), self.select_card_sprite_list)

            hovered_card = None

            if len(cards) > 0:
                hovered_card = cards[-1]

                if not hovered_card.hover_start:
                    self.select_cards_controller.set_hover(hovered_card)
                    play_effect(Effect.CARD_MOVING)
                else:
                    self.dude.try_react_on_hover()

            for card in self.select_card_sprite_list:
                if not card.chosen and card != hovered_card:
                    self.select_cards_controller.unset_hover(
                        card,
                        force=bool(hovered_card),
                    )

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
        if self.select_cards_controller.check_for_next_round():
            return

        if symbol == arcade.key.UP:
            self.volume_delta = 1

        elif symbol == arcade.key.DOWN:
            self.volume_delta = -1

    def on_key_release(self, _symbol: int, _modifiers: int):
        if _symbol == arcade.key.UP:
            self.volume_delta = 0

        elif _symbol == arcade.key.DOWN:
            self.volume_delta = 0

    def on_update(self, dt):
        """Move everything"""

        if self.game_over:
            return

        if self.select_cards_controller.after_consequence_end:
            self.start_next_round()
            return

        self.news.update()
        self.dude.update(dt)
        # Не рисуем ничего больше пока есть новости
        # TODO: может, надо просто блочить клики
        # TODO: if self.game_manager.get_news()
        if self.news.is_blocking_other():
            return

        self.card_sprite_list.update()
        self.select_card_sprite_list.update()
        self.select_cards_controller.render_events()
