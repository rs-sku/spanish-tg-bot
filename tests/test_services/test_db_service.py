import pytest


@pytest.mark.asyncio
async def test_get_repeat_words(db_service):
    service, repo = db_service
    chat_id = 123
    rows = [{"word": "Hola", "translation": "Привет"}]
    repo.get_repeat_words.return_value = rows

    result = await service.get_repeat_words(chat_id)

    repo.get_repeat_words.assert_awaited_once_with(chat_id)
    assert result == [{"Hola": "Привет"}]


@pytest.mark.asyncio
async def test_get_repeat_words_empty(db_service):
    service, repo = db_service
    chat_id = 123
    repo.get_repeat_words.return_value = []

    result = await service.get_repeat_words(chat_id)

    repo.get_repeat_words.assert_awaited_once_with(chat_id)
    assert result is None


@pytest.mark.asyncio
async def test_save_user_words(db_service):
    service, repo = db_service
    chat_id, words = 123, ["Hola", "Adiós"]

    await service.save_user_words(chat_id, words)

    repo.add_user_words.assert_awaited_once_with(chat_id, words)


@pytest.mark.asyncio
async def test_get_random_variants(db_service):
    service, repo = db_service
    chat_id = 123
    rows = [{"word": "uno"}, {"word": "dos"}, {"word": "tres"}]
    repo.get_random_words.return_value = rows

    result = await service.get_random_variants(chat_id)

    repo.get_random_words.assert_awaited_once()
    assert result == ["uno", "dos", "tres"]


@pytest.mark.asyncio
async def test_get_random_words(db_service):
    service, repo = db_service
    chat_id = 123
    rows = [{"word": "Hola", "translation": "Привет"}]
    repo.get_random_words.return_value = rows

    result = await service.get_random_words(chat_id, True)

    repo.get_random_words.assert_awaited_once()
    assert result == [{"Hola": "Привет"}]


@pytest.mark.asyncio
async def test_add_user_word(db_service):
    service, repo = db_service
    chat_id, word, translation = 123, "Hola", "Привет"
    repo.add_user_word.return_value = True

    result = await service.add_user_word(chat_id, word, translation)

    repo.add_user_word.assert_awaited_once_with(chat_id, word, translation)
    assert result is True


@pytest.mark.asyncio
async def test_delete_user_word_success(db_service):
    service, repo = db_service
    chat_id, translation = 123, "Привет"
    rows = [{"word": "Hola"}]
    repo.get_by_translation.return_value = rows
    repo.delete_user_word.return_value = True

    result = await service.delete_user_word(chat_id, translation)

    repo.get_by_translation.assert_awaited_once_with(chat_id, translation)
    repo.delete_user_word.assert_awaited_once_with(chat_id, "Hola")
    assert result is True


@pytest.mark.asyncio
async def test_delete_user_word_not_found(db_service):
    service, repo = db_service
    chat_id, translation = 123, "Привет"
    repo.get_by_translation.return_value = []

    result = await service.delete_user_word(chat_id, translation)

    repo.get_by_translation.assert_awaited_once_with(chat_id, translation)
    assert result is False


@pytest.mark.asyncio
async def test_delete_user_word_delete_failed(db_service):
    service, repo = db_service
    chat_id, translation = 123, "Привет"
    rows = [{"word": "Hola"}]
    repo.get_by_translation.return_value = rows
    repo.delete_user_word.return_value = False

    result = await service.delete_user_word(chat_id, translation)

    repo.get_by_translation.assert_awaited_once_with(chat_id, translation)
    repo.delete_user_word.assert_awaited_once_with(chat_id, "Hola")
    assert result is False
