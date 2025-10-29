from enum import Enum


class ButtonsText(Enum):
    ADD_WORD = "Добавить слово"
    ADD_ALL = "Добавить все"
    DELETE_WORD = "Удалить слово"
    DELETE_CURRENT = "Удалить "
    BACK = "⬅️"
    FORWARD = "➡️"
    VIEW_COLLECTION = "Посмотреть все слова"
    TEST = "Тест 📝"
    NEW_WORDS = "Новые слова 📜"
    REPEAT = "Повторение 🔁"
    BASE = "Базовый"
    ADVANCED = "Продвинутый"
    MANAGE_COLLECTION = "Управлять коллекцией 🕹️"


class MsgsText(Enum):
    START = (
        "Bienvenido amigo! Желаю хорошо провести время за изучением нового!\n\n"
        "P.S. Вы можете поучаствовать в этом проекте здесь \n👇\n"
        "<a href='https://github.com/rs-sku/spanish-tg-bot'>перейти</a>\n"
        "\n И так же связаться со мной \n👇\n"
        "<a href='https://t.me/rs_sku'>@rs_sku</a>"
    )
    CHOOSE_DIFF = "Выберите уровень сложности слов 🎮"
    SHOWED_WORDS = "Ваши слова 👇 Как запомните - жмите на кнопку 📝\n\n"
    TRANSLATE = "❓ Переведите слово: "
    WRONG_ANS = "Неправильно 😔\n"
    CORRECT_ANSWER = "Правильно ✔️\n"
    FINISH_LEARNING = (
        "Поздравляю! Вы выучили все новые слова и теперь можете выбрать, какие из них добавить в коллекцию 😎"
    )
    FINISH_REPEAT = "Поздравляю! Вы успешно закрепили знания 😎"
    NO_REPEAT = "В Вашей коллекции ещё нет слов, начните с новых 📜"
    WRONG_WORD_INPUT = "Неверный формат ввода 🤔"
    CAN_NOT_DELETE = "В коллекции нет такого слова, нажмите снова 🙄"
    NO_DELETE = "Нечего удалять 🙃"
    WORD_ADDED = " успешно добавлено в коллекцию 👌"
    WORD_DELETED = " успешно удалено из коллекции👌"
    WORDS_ADDED = "Все слова успешно добавлены в коллекцию 👌"
    ALREADY_HAS_WORD = "В коллекции уже есть данное слово 🙃"
    TYPE_WORD_TO_ADD = "Введите русский вариант слова и подождите пару секунд ✍️"
    TYPE_WORD_TO_DELETE = "Введите русский вариант слова из Вашей коллекции ✍️"
    BAD_WORD = "Плохое слово 🤬"
    NOT_RELLEVANT_ACTION = "Действие уже не актуально для Вас 🙄"
    CHOOSE_ACTION = "Выберите действие 👇"


class Actions(Enum):
    NEW = "new"
    REPEAT = "repeat"


class CallbackDataPrefixes(Enum):
    SAVE = "save"
    DELETE = "del"
    ALL = "all"
