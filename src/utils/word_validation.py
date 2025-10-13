import re
from ruslingua import AsyncRusLingua


async def validate_word(word: str) -> bool:
    ruslingua = AsyncRusLingua()
    definition = await ruslingua.get_definition(word)
    if not definition:
        return False
    definition = re.sub(r"[^а-яёА-ЯЁ\-]", "", definition)
    overlap = ""
    for char in definition:
        if char.isupper() or char == "-":
            overlap += char
        else:
            break
    overlap = overlap[:-1] if overlap[-1] == "-" else overlap
    return word.lower() == overlap.lower()
