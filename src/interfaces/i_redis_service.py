from abc import ABC, abstractmethod


class RedisServiceInterface(ABC):
    @abstractmethod
    async def add_words(self, chat_id: int, words: list[str]) -> None:
        pass

    @abstractmethod
    def get_random_word(self, chat_id: int) -> dict[str, str] | set[str]:
        pass

    @abstractmethod
    def move_word(self, chat_id: int, word_tr: dict[str, str]) -> None:
        pass
