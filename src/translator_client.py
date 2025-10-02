from googletrans import Translator

from src.core.constansts import Constants


class TranslatorClient:
    def __init__(self, translator: Translator) -> None:
        self._t = translator
        self._dest = Constants.DEST.value

    async def translate_one(self, word: str) -> str:
        res = await self._t.translate(text=word, dest="russian")
        return res.text
