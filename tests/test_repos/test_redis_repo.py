from src.core.constansts import Constants


def test_in_process(redis_repo):
    service, r_mock = redis_repo
    r_mock.get.return_value = "1"
    assert service.in_process(123) is True
    r_mock.get.assert_called_once_with("user:123")


def test_set_and_remove_in_process(redis_repo):
    service, r_mock = redis_repo
    service.set_in_process(123)
    r_mock.set.assert_called_once_with("user:123", 1, ex=60)
    service.remove_in_process(123)
    r_mock.delete.assert_called_once_with("user:123")


def test_add_words(redis_repo):
    service, r_mock = redis_repo
    chat_id = 123
    words = ["Hola", "Adiós"]
    service.add_words(chat_id, words)
    r_mock.set.assert_called_once_with(chat_id, Constants.ATTEMPTS_COUNT.value)
    r_mock.sadd.assert_called_once_with(
        f"{chat_id}:{Constants.ATTEMPTS_COUNT.value}", *words
    )


def test_get_random_word(redis_repo):
    service, r_mock = redis_repo
    chat_id = 123
    r_mock.get.return_value = "2"
    r_mock.srandmember.return_value = "Hola"
    word = service.get_random_word(chat_id)
    assert word == "Hola"
    r_mock.srandmember.assert_called_once_with(f"{chat_id}:2")


def test_move_word(redis_repo):
    service, r_mock = redis_repo
    chat_id = 123
    r_mock.get.return_value = "2"
    service.move_word(chat_id, "Hola")
    r_mock.smove.assert_called_once_with("123:2", "123:1", "Hola")


def test_get_all_words(redis_repo):
    service, r_mock = redis_repo
    chat_id = 123
    r_mock.get.return_value = "2"
    r_mock.smembers.return_value = {"Hola", "Adiós"}
    res = service.get_all_words(chat_id)
    assert res == {"Hola", "Adiós"}
    r_mock.smembers.assert_called_once_with("123:2")


def test_delete_words(redis_repo):
    service, r_mock = redis_repo
    chat_id = 123
    r_mock.keys.return_value = ["123:1", "123:2"]
    service.delete_words(chat_id)
    r_mock.delete.assert_called_once_with("123:1", "123:2")


def test_reduce_attempts_count(redis_repo):
    service, r_mock = redis_repo
    chat_id = 123
    r_mock.get.return_value = "3"
    new_count = service.reduce_attempts_count(chat_id)
    assert new_count == 2
    r_mock.set.assert_called_once_with(123, 2)
