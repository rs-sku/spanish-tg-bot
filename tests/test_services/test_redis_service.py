def test_add_words(redis_service):
    service, repo_mock = redis_service
    repo_mock.in_process.return_value = False
    chat_id, words = 123, [{"Hola": "Привет"}]
    service.add_words(chat_id, words)
    repo_mock.set_in_process.assert_called_once_with(123)
    repo_mock.delete_words.return_value = None
    repo_mock.add_words.assert_called_once_with(chat_id, [{"Hola": "Привет"}])
    repo_mock.remove_in_process.assert_called_once_with(123)


def test_get_random_word_first(redis_service):
    service, repo_mock = redis_service
    word = "Hola"
    chat_id = 123
    repo_mock.get_random_word.return_value = word
    res = service.get_random_word(chat_id)
    repo_mock.get_random_word.assert_called_once_with(chat_id)
    assert res == word


def test_get_random_word_second(redis_service):
    service, repo_mock = redis_service
    word = "Hola"
    chat_id = 123
    repo_mock.get_random_word.side_effect = [None, word]
    repo_mock.reduce_attempts_count.return_value = 1
    res = service.get_random_word(chat_id)
    assert res == word
    assert repo_mock.get_random_word.call_count == 2


def test_get_random_word_third(redis_service):
    service, repo_mock = redis_service
    word = "Hola"
    chat_id = 123
    repo_mock.get_random_word.return_value = None
    repo_mock.reduce_attempts_count.return_value = 0
    repo_mock.get_all.return_value = {word}
    repo_mock.delete_words.return_value = None
    res = service.get_random_word(chat_id)
    repo_mock.get_random_word.assert_called_once_with(chat_id)
    repo_mock.reduce_attempts_count.assert_called_once_with(chat_id)
    repo_mock.get_all.assert_called_once_with(chat_id)
    repo_mock.delete_words.assert_called_once_with(chat_id)
    assert res == {word}


def test_move_word(redis_service):
    service, repo_mock = redis_service
    chat_id, val = 123, "some_value"
    service.move_word(chat_id, val)
    repo_mock.move_word.assert_called_once_with(chat_id, val)
