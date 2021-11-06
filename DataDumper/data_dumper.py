import os
from typing import Optional

import gspread
import pandas
import pandas as pd
from tinydb import Query, TinyDB

from sgj.graphics.constants import DATABASE_FILEPATH, DECISIONS_COUNT


def get_sprite_path(name: str, sprite_name: Optional[str] = None):
    import os

    if sprite_name is not None:
        return os.path.join("GameData", "Images", "Events", name, sprite_name)
    return os.path.join("GameData", "Images", "Events", name)

def int_safe(val: str) -> int:
    return int(val) if val != '' else 0


class DataDumper(object):
    COL_NAME: int = 0
    COL_DEPENDENCIES: int = 1
    COL_INTRO_TEXT: int = 2
    COL_DECISIONS_TEXT: int = 4
    COL_CONSEQUENCES_TEXT: int = 5
    COL_PRICES: int = 6
    COL_REWARDS: int = 7
    COL_NEWS_DELAY: int = 8
    COL_NEWS_TEXT: int = 9
    COL_NEWS_REWARDS: int = 10

    SPRITE_NAME_INTRO = "intro.png"

    def __init__(self, table_id):
        self._table_id = table_id
        self._db = TinyDB(DATABASE_FILEPATH)  # type: TinyDB

    def load_data(self):

        gc = gspread.service_account()
        table = gc.open_by_key(self._table_id)
        sheet = table.worksheet("Sheet1")
        vals = pd.DataFrame(sheet.get_all_values())

        events = self.construct_events(vals)
        self._db.upsert({"events": events}, Query().events.exists())

    @staticmethod
    def fill_event_by_idx(event: dict, sheet: pd.DataFrame, row: int):
        name = event["name"]
        event.update(
            {
                "description": sheet[row][DataDumper.COL_INTRO_TEXT],
                "sprite": get_sprite_path(name, DataDumper.SPRITE_NAME_INTRO),
                "dependencies": sheet[row][DataDumper.COL_DEPENDENCIES].splitlines(),
                "decisions": DataDumper.get_decisions_from_row(name, sheet, row),
            },
        )

    @staticmethod
    def parse_price(value: str):
        result = {}
        prices = value.split(", ")
        assert(len(prices) > 0)

        result["energy"] = int_safe(prices[0])
        if len(prices) > 1:
            result["energy"] = int_safe(prices[0])
        return result

    @staticmethod
    def parse_rewards(value: str):
        HAPPINESS_PREFIX = "h:"
        FATUM_PREFIX = "f:"
        ENERGY_PREFIX = "e:"
        result = {}
        for reward in value.split(", "):
            if reward.startswith(HAPPINESS_PREFIX):
                result["happiness"] = int(reward.removeprefix(HAPPINESS_PREFIX))
            elif reward.startswith(FATUM_PREFIX):
                result["fatum"] = int(reward.removeprefix(FATUM_PREFIX))
            elif reward.startswith(HAPPINESS_PREFIX):
                result["energy"] = int(reward.removeprefix(ENERGY_PREFIX))
        return result

    @staticmethod
    def get_decisions_from_row(name, sheet: pd.DataFrame, row):
        DECISION_PREFIX = "dec"
        CONSEQUENCE_PREFIX = "dec"
        IMAGE_FORMAT_SUFFIX = ".png"
        decision_sprite_name = (
            lambda idx: DECISION_PREFIX
            + str(
                idx,
            )
            + IMAGE_FORMAT_SUFFIX
        )
        consequence_sprite_name = (
            lambda idx: CONSEQUENCE_PREFIX
            + str(
                idx,
            )
            + IMAGE_FORMAT_SUFFIX
        )

        decisions = []
        for idx in range(DECISIONS_COUNT):
            sheet_idx = idx + 1
            decision = {
                "description": sheet[row + idx][DataDumper.COL_DECISIONS_TEXT],
                "sprite": get_sprite_path(name, decision_sprite_name(sheet_idx)),
                "price": DataDumper.parse_price(
                    sheet[row + idx][DataDumper.COL_PRICES]
                ),
                "consequence": {
                    "text": sheet[row + idx][DataDumper.COL_CONSEQUENCES_TEXT],
                    "sprite": get_sprite_path(name, consequence_sprite_name(sheet_idx)),
                    "rewards": DataDumper.parse_rewards(
                        sheet[row + idx][DataDumper.COL_REWARDS],
                    ),
                    "news": {
                        "delay": int_safe(sheet[row + idx][DataDumper.COL_NEWS_DELAY]),
                        "text": sheet[row + idx][DataDumper.COL_NEWS_TEXT],
                        "rewards": DataDumper.parse_rewards(
                            sheet[row + idx][DataDumper.COL_NEWS_REWARDS]
                        ),
                    },
                },
            }
            decisions.append(decision)
        return decisions

    def construct_events(self, sheet: pandas.DataFrame):
        DATA_TOP_OFFSET = 2

        events = [
            {"name": x, "row": idx + DATA_TOP_OFFSET}
            for idx, x in enumerate(
                sheet[DATA_TOP_OFFSET:][DataDumper.COL_NAME],
            )
            if x != ""
        ]
        for event in events:
            # FIXME: Я не знаю почему тут надо транспонировать датафрейм. Вот бы кто
            #  рассказал
            self.fill_event_by_idx(event, sheet.transpose(), event["row"])

        return events


def __main__():
    sheet_id = "17oyKkXhXdL5eIoKB0IGNwRlBrB6N5CD0BYO1YjR-LxM"
    dd = DataDumper(sheet_id)
    dd.load_data()


if __name__ == "__main__":
    __main__()
