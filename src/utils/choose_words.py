import random
from src.core.constansts import Constants
import logging

logger = logging.getLogger(__name__)


def choose_words(
    count: int, path: str = Constants.WORDS_FILE_PATH.value, base_word: str = None
) -> list[str]:
    logging.info(f"Reading {path=}")
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    res = []
    while len(res) < count:
        word = random.choice(lines).strip().capitalize()
        if word != base_word and word not in res:
            res.append(word)
    return res
