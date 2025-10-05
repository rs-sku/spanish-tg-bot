from abc import ABC, abstractmethod


class DbServiceInterface(ABC):
    @abstractmethod
    async def get_repeat_words(self, chat_id: int) -> list[str] | None:
        pass

    @abstractmethod
    async def save_user_words(self, chat_id: int, words: list[dict[str, str]]) -> None:
        pass

    @abstractmethod
    async def get_random_variants(self, chat_id: int) -> list[str]:
        pass

    @abstractmethod
    async def get_random_words(
        self, chat_id: int, is_base: bool
    ) -> list[dict[str, str]]:
        pass

    @abstractmethod
    async def add_user_word(self, chat_id: int, word: str, translation: str) -> bool:
        pass

    @abstractmethod
    async def delete_user_word(self, chat_id: int, word: str) -> bool:
        pass
