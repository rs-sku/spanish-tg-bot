from googletrans import Translator

from src.core.constansts import Constants


class TranslatorClient:
    def __init__(self, translator: Translator) -> None:
        self._t = translator

    async def translate_one(self, word: str, dest: str) -> str:
        res = await self._t.translate(text=word, dest=dest)
        return res.text
