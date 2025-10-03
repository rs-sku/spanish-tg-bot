from enum import Enum


class Constants(Enum):
    BASE_WORDS_FILE_PATH = "data/espwords_base.txt"
    WORDS_FILE_PATH = "data/espwords.txt"
    DEST = "russian"
    ATTEMPTS_COUNT = 1
    SHOW_COUNT = 5
    VARIANTS_COUNT = 3
    INTERNAL_ERROR = "Something went wrong... Попробуйте снова"
