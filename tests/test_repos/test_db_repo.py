import pytest


@pytest.mark.asyncio
async def test_add_and_count_words(db_repo):
    words = [
        {"word": "Hola", "translation": "Привет", "is_base": True},
        {"word": "Adiós", "translation": "Пока", "is_base": True},
    ]
    await db_repo.add_all_words(words)
    count = await db_repo.count_words()
    assert count == 2


@pytest.mark.asyncio
async def test_add_user_word(db_repo):
    chat_id = 123
    await db_repo._add_user(chat_id)
    await db_repo.add_all_words(
        [{"word": "Hola", "translation": "Привет", "is_base": True}]
    )

    result = await db_repo.add_user_word(chat_id, "Hola", "Привет")
    assert result is True

    result2 = await db_repo.add_user_word(chat_id, "Hola", "Привет")
    assert result2 is False


@pytest.mark.asyncio
async def test_get_random_words(db_repo):
    chat_id = 123
    await db_repo._add_user(chat_id)
    words = [
        {"word": "Hola", "translation": "Привет", "is_base": True},
        {"word": "Adiós", "translation": "Пока", "is_base": True},
    ]
    await db_repo.add_all_words(words)

    rows = await db_repo.get_random_words(chat_id, is_base=True, limit=2)
    retrieved_words = [row["word"] for row in rows]
    assert set(retrieved_words) <= {"Hola", "Adiós"}


@pytest.mark.asyncio
async def test_delete_user_word(db_repo):
    chat_id = 123
    await db_repo._add_user(chat_id)
    await db_repo.add_all_words(
        [{"word": "Hola", "translation": "Привет", "is_base": True}]
    )
    await db_repo.add_user_word(chat_id, "Hola", "Привет")

    deleted = await db_repo.delete_user_word(chat_id, "Hola")
    assert deleted is True

    deleted2 = await db_repo.delete_user_word(chat_id, "Hola")
    assert deleted2 is False
