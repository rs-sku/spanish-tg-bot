import pytest
import json
from src.core.constansts import Constants


@pytest.mark.asyncio
async def test_show_words_repeat(mocker, coordinator):
    coord, _ = coordinator
    coord._db_service.get_repeat_words = mocker.AsyncMock(
        return_value=[{"Hola": "Привет"}]
    )
    coord._redis_service.add_words = mocker.Mock()

    result = await coord.show_words(123, is_repeat=True)

    coord._db_service.get_repeat_words.assert_awaited_once_with(123)
    coord._redis_service.add_words.assert_called_once_with(
        123, [json.dumps({"Hola": "Привет"})]
    )
    assert "Hola - Привет" in result


@pytest.mark.asyncio
async def test_show_words_random(mocker, coordinator):
    coord, _ = coordinator
    coord._db_service.get_random_words = mocker.AsyncMock(
        return_value=[{"Adiós": "Пока"}]
    )
    coord._redis_service.add_words = mocker.Mock()

    result = await coord.show_words(123, is_repeat=False, is_base=True)

    coord._db_service.get_random_words.assert_awaited_once_with(123, True)
    coord._redis_service.add_words.assert_called_once_with(
        123, [json.dumps({"Adiós": "Пока"})]
    )
    assert "Adiós - Пока" in result


@pytest.mark.asyncio
async def test_show_words_repeat_no_words(mocker, coordinator):
    coord, _ = coordinator
    coord._db_service.get_repeat_words = mocker.AsyncMock(return_value=[])
    result = await coord.show_words(123, is_repeat=True)
    assert result is None


@pytest.mark.asyncio
async def test_get_random_word_or_save_string(mocker, coordinator):
    coord, _ = coordinator
    coord._redis_service.get_random_word = mocker.Mock(
        return_value=json.dumps(["Hola", "Привет"])
    )

    result = await coord.get_random_word_or_save(coord, 123)  # просто синхронный вызов

    assert result == ["Hola", "Привет"]


@pytest.mark.asyncio
async def test_get_random_word_or_save_saving(mocker, coordinator):
    coord, _ = coordinator
    redis_res = [
        json.dumps({"Hola": "Привет"}),
        json.dumps({"Adiós": "Пока"}),
    ]
    coord._redis_service.get_random_word = mocker.Mock(return_value=redis_res)
    coord._db_service.save_user_words = mocker.AsyncMock()

    await coord.get_random_word_or_save(123, saving=True)

    coord._db_service.save_user_words.assert_awaited_once_with(123, ["Hola", "Adiós"])


def test_move_word(mocker, coordinator):
    coord, _ = coordinator
    coord._redis_service.move_word = mocker.Mock()
    word_tr = {"Hola": "Привет"}

    coord.move_word(123, word_tr)

    coord._redis_service.move_word.assert_called_once_with(123, json.dumps(word_tr))


@pytest.mark.asyncio
async def test_add_user_word(mocker, coordinator):
    coord, translator = coordinator
    translator.translate_one = mocker.AsyncMock(return_value="hola")
    coord._db_service.add_user_word = mocker.AsyncMock(return_value=True)

    res = await coord.add_user_word(123, "привет")

    translator.translate_one.assert_awaited_once_with(
        "привет", Constants.SPANISH_DEST.value
    )
    coord._db_service.add_user_word.assert_awaited_once_with(123, "Hola", "Привет")
    assert res == "'Привет - Hola'"


@pytest.mark.asyncio
async def test_add_user_word_same_word(mocker, coordinator):
    coord, translator = coordinator
    translator.translate_one = mocker.AsyncMock(return_value="привет")

    with pytest.raises(ValueError):
        await coord.add_user_word(123, "привет")


@pytest.mark.asyncio
async def test_add_user_word_db_returns_false(mocker, coordinator):
    coord, translator = coordinator
    translator.translate_one = mocker.AsyncMock(return_value="hola")
    coord._db_service.add_user_word = mocker.AsyncMock(return_value=False)

    res = await coord.add_user_word(123, "привет")
    assert res is None


@pytest.mark.asyncio
async def test_delete_user_word_success(mocker, coordinator):
    coord, _ = coordinator
    coord._db_service.delete_user_word = mocker.AsyncMock(return_value=True)

    res = await coord.delete_user_word(123, "привет")

    coord._db_service.delete_user_word.assert_awaited_once_with(123, "Привет")
    assert res == "'Привет'"


@pytest.mark.asyncio
async def test_delete_user_word_not_found(mocker, coordinator):
    coord, _ = coordinator
    coord._db_service.delete_user_word = mocker.AsyncMock(return_value=False)

    res = await coord.delete_user_word(123, "привет")

    assert res is None


def test_validate_input_word_true(coordinator):
    coord, _ = coordinator
    assert coord.validate_input_word("Hola")


def test_validate_input_word_false(coordinator):
    coord, _ = coordinator
    assert not coord.validate_input_word("123Hola")
