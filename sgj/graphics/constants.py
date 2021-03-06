import os

STARTING_ASTEROID_COUNT = 5
EVENT_CARD_SCALE = 0.3
SELECT_CARD_SCALE = 0.2
OFFSCREEN_SPACE = 300
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Trixter"
HORIZONTAL_CARDS_PADDING = 0.2
DATABASE_FILEPATH = os.path.join("..", "GameData", "GameData.json")
SPRITE_DIR = os.path.join("GameData", "Images")
SOUNDS_DIR = os.path.join("GameData", "Sounds")
DECISIONS_COUNT = 4
MAX_VOLUME = 100

trim = lambda a, b, x: max(min(x, b), a)
