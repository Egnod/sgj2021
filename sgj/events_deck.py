import random
from copy import copy


class EventsDeck:
    def __init__(self, db_filepath: str):
        from tinydb import TinyDB, Query
        db = TinyDB(db_filepath)
        self.events = db.get(Query().events.exists())['events']  # type: list
        self.unused_events_shuffled = copy(self.events)  # type: list
        random.shuffle(self.unused_events_shuffled)

    @staticmethod
    def multiply_event(event: dict, multiplier: float):
        def mul_dict(d: dict, mul: float):
            for k, v in d.items():
                d[k] = v * mul

        for decision in event["decisions"]:
            mul_dict(decision['price'], multiplier)
            mul_dict(decision['consequence']['rewards'], multiplier)
            mul_dict(decision['consequence']['news']['rewards'], multiplier)

        return event

    def get_random_event(self, multiplier: float = 1):
        return self.multiply_event(self.unused_events_shuffled.pop(), multiplier)

    def get_random_events(self, count: int, multiplier: float = 1):
        return [self.get_random_event(multiplier) for _ in range(count)]


def main():
    from sgj.graphics.constants import DATABASE_FILEPATH
    ed = EventsDeck(DATABASE_FILEPATH)
    foo = ed.get_random_event(2)
    from pprint import pprint
    pprint(foo)


if __name__ == "__main__":
    main()
