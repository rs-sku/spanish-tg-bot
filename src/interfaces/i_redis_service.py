from abc import ABC, abstractmethod


class RedisServiceInterface(ABC):
    @abstractmethod
    def add_words(self, chat_id: int, words: list[str]) -> None:
        pass

    @abstractmethod
    def get_random_word(self, chat_id: int) -> str | None:
        pass

    @abstractmethod
    def move_word(self, chat_id: int, word_tr: dict[str, str]) -> None:
        pass

    @abstractmethod
    def get_all_words(chat_id: str) -> set[str]:
        pass
