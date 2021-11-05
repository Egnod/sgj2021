from typing import Optional
import gspread
from tinydb import TinyDB, Query


def get_sprite_path(name: str, sprite_name: Optional[str] = None):
    import os
    if sprite_name is not None:
        return os.path.join("GameData", "Images", "Events", name, sprite_name)
    return os.path.join("GameData", "Images", "Events", name)


class DataDumper(object):
    COL_NAME: int = 1
    COL_DEPENDENCIES: int = 2
    COL_INTRO_TEXT: int = 3
    COL_DECISIONS_TEXT: int = 5
    COL_CONSEQUENCES_TEXT: int = 6
    COL_PRICES: int = 7
    COL_REWARDS: int = 8

    SPRITE_NAME_INTRO = 'intro.png'

    def __init__(self, table_id):
        self._table_id = table_id
        self._db = TinyDB('GameData.json')

    def load_data(self):
        gc = gspread.service_account()
        table = gc.open_by_key(self._table_id)
        sheet = table.worksheet('Sheet1')
        self.fill_game_data(sheet)
        pass

    @staticmethod
    def construct_dependencies(val: Optional[str]):
        if val is None:
            return []
        return val.splitlines()

    @staticmethod
    def fill_event_by_idx(event: dict, sheet: gspread.Worksheet, row: int):
        name = event['name']
        event.update({
            'description': sheet.cell(row, DataDumper.COL_INTRO_TEXT).value,
            'sprite': get_sprite_path(name, DataDumper.SPRITE_NAME_INTRO),
            'dependencies': DataDumper.construct_dependencies(sheet.cell(row,
                                       DataDumper.COL_DEPENDENCIES).value),
            'decisions': DataDumper.fill_decisions_from_row(name, sheet, row)
        })

    @staticmethod
    def fill_rewards(value: str):
        HAPPINESS_PREFIX = 'h:'
        FATUM_PREFIX = 'f:'
        ENERGY_PREFIX = 'e:'
        result = {}
        for reward in value.split(', '):
            if reward.startswith(HAPPINESS_PREFIX):
                result['happiness'] = int(reward.removeprefix(HAPPINESS_PREFIX))
            elif reward.startswith(FATUM_PREFIX):
                result['fatum'] = int(reward.removeprefix(FATUM_PREFIX))
            elif reward.startswith(HAPPINESS_PREFIX):
                result['energy'] = int(reward.removeprefix(ENERGY_PREFIX))
        return result

    @staticmethod
    def fill_decisions_from_row(name, sheet, row):
        DECISION_PREFIX = 'dec'
        CONSEQUENCE_PREFIX = 'dec'
        IMAGE_FORMAT_SUFFIX = '.png'
        decision_sprite_name = lambda idx: DECISION_PREFIX + str(
            idx) + IMAGE_FORMAT_SUFFIX
        consequence_sprite_name = lambda idx: CONSEQUENCE_PREFIX + str(
            idx) + IMAGE_FORMAT_SUFFIX

        decisions = []
        for idx in range(4):
            sheet_idx = idx + 1
            decision = {
                'description': sheet.cell(row + idx,
                                          DataDumper.COL_DECISIONS_TEXT).value,
                'sprite': get_sprite_path(name, decision_sprite_name(sheet_idx)),
                'consequence': {
                    'text': sheet.cell(row + idx,
                                       DataDumper.COL_CONSEQUENCES_TEXT).value,
                    'sprite': get_sprite_path(name, consequence_sprite_name(sheet_idx)),
                    'price': sheet.cell(row + idx,
                                        DataDumper.COL_CONSEQUENCES_TEXT).value,
                    'rewards': DataDumper.fill_rewards(sheet.cell(row + idx,
                                                       DataDumper.COL_CONSEQUENCES_TEXT)
                                                       .value)
                }
            }
            decisions.append(decision)
        return decisions

    def fill_game_data(self, sheet: gspread.Worksheet):
        DATA_TOP_OFFSET = 3

        events = [{'name': x, 'row': idx} for idx, x in
                  enumerate(sheet.col_values(DataDumper.COL_NAME)[DATA_TOP_OFFSET:])
                  if x != '']
        for event in events:
            self.fill_event_by_idx(event, sheet, event['row'])


def __main__():
    sheet_id = '17oyKkXhXdL5eIoKB0IGNwRlBrB6N5CD0BYO1YjR-LxM'
    dd = DataDumper(sheet_id)
    dd.load_data()


if __name__ == '__main__':
    __main__()
