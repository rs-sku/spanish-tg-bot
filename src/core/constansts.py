from enum import Enum


class Constants(Enum):
    BASE_WORDS_FILE_PATH = "src/data/base_words.txt"
    WORDS_FILE_PATH = "src/data/words.txt"
    DEST = "russian"
    ATTEMPTS_COUNT = 1
    SHOW_COUNT = 5
    VARIANTS_COUNT = 3
    INTERNAL_ERROR = "Something went wrong... Попробуйте снова"
    MIN_WORDS_TABLE_SIZE = 500
