from statistics import mean
from typing import Optional

from sgj.events_deck import EventsDeck


class GameManager:
    ENERGY_ROUND_CHARGE = 5

    def __init__(self, db_filepath: str):
        self.events_deck = EventsDeck(db_filepath)

        self.energy_min_max = [0, 100]
        self.energy = self.energy_min_max[1]
        self.angry_min_max = [0, 100]
        self.angry = mean(self.angry_min_max)
        self.fatum_min_max = [0, 10]
        self.fatum = self.fatum_min_max[0]

        self.cur_event = None
        self.cur_multiplier = 1.0

        self.news = []  # type: list

        self.is_first_get = True
        self.first_event = None

    def get_stat(self):
        return {
            "energy": self.energy,
            "fatum": self.fatum,
            "angry": self.angry,
        }

    def set_energy_round_charge(self) -> None:
        """Increment energy on start new round (if not max yet)."""
        if self.energy < self.energy_min_max[1]:
            if self.energy + self.ENERGY_ROUND_CHARGE > self.energy_min_max[1]:
                self.energy += self.energy_min_max[1] - self.energy

            else:
                self.energy += self.ENERGY_ROUND_CHARGE

    def get_next_event(self) -> dict:
        if self.is_first_get:  # тестим и показываем игроку первое событие в начале игры
            self.cur_event = self.events_deck.get_exact_event('Тихая деревня')
            self.is_first_get = False
        else:
            self.cur_event = self.events_deck.get_random_event(self.cur_multiplier)
        self._shift_news()
        return self.cur_event

    def is_decision_available(self, idx: int):
        """
        Returns false in case of resources is not enough for this decision
        """
        result = True
        dec = self.cur_event["decisions"][idx]
        result &= dec["price"]["energy"] <= self.energy
        result &= dec["price"].get("fatum", 0) <= self.fatum
        return result

    def get_news(self) -> Optional[list[str, dict]]:
        """
        Returns None in case of no news. Else return text and processed rewards
        """
        import sys

        min_delay = sys.maxsize
        text = None
        rewards = None

        for news in self.news:
            if news[0] < min_delay:
                min_delay = news[0]
                text = news[1]
                rewards = news[2]

        if rewards is not None:
            self._process_rewards(rewards)

        if text:
            return {'text': text, 'rewards': rewards}
        return None

    def _shift_news(self):
        for news in self.news:
            news[0] -= 1

    def _process_news(self, news: dict):
        if news["text"] != "":
            self.news.append((news["delay"], news["text"], news["rewards"]))

    def _process_rewards(self, rewards: dict):
        def trim(a, b, x):
            if x < a:
                return a
            if x > b:
                return b
            return x

        self.energy += trim(*self.energy_min_max, rewards.get("energy", 0))
        self.fatum += trim(*self.fatum_min_max, rewards.get("fatum", 0))
        self.angry += trim(*self.angry_min_max, rewards.get("angry", 0))

    def process_decision(self, idx: int) -> bool:
        """
        Returns false in case of resources is not enough for this decision
        """
        if not self.is_decision_available(idx):
            return False

        dec = self.cur_event["decisions"][idx]

        self.energy -= int(dec["price"]["energy"])
        self._process_rewards(dec["consequence"]["rewards"])
        self._process_news(dec["consequence"]["news"])


def main():
    from sgj.graphics.constants import DATABASE_FILEPATH

    gm = GameManager(DATABASE_FILEPATH)
    gm.get_next_event()
    gm.process_decision(1)


if __name__ == "__main__":
    main()
