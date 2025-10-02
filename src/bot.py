from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BotCommand,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from aiogram.types.callback_query import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.core.constansts import Constants
from src.services.db_service import DbService
from src.services.redis_service import RedisService
from enum import Enum

from src.utils.choose_words import choose_words


class ButtonsText(Enum):
    ADD_WORD = "Добавить слово ➕"
    DELETE_WORD = "Удалить слово ➖"
    TEST = "Тест 📝"
    NEW_WORDS = "Новые слова 📜"
    REPEAT = "Повторение 🔁"
    BASE = "Базовый"
    ADVANCED = "Продвинутый"


class MsgsText(Enum):
    START = "Bienvenido amigo! Желаю хорошо провести время за изучением нового ☝"
    CHOOSE_DIFF = "Выберите уровень сложности слов 🎮"
    SHOWED_WORDS = "Твои слова 👇 Как запомнишь - жми на кнопку 📝\n\n"
    TRANSLATE = "❓ Переведите слово: "
    WRONG_ANS = "Неправильно 😔\n"
    CORRECT_ANSWER = "Правильно ✔️\n"
    FINISH_LEARNING = (
        "Поздравляю! Вы выучили все новые слова, теперь они доступны для повторения. "
        "Так же можно получить порцию новых слов 😎"
    )


class AnswerRequest(StatesGroup):
    waiting_for_answer = State()


class LangBot:
    def __init__(
        self,
        dp: Dispatcher,
        bot_obj: Bot,
        db_service: DbService,
        redis_service: RedisService,
    ) -> None:
        self._dp = dp
        self._bot_obj = bot_obj
        self._db_service = db_service
        self._redis_service = redis_service

    async def start(self) -> None:
        await self._set_commands()
        self._start_cmd_handler()
        self._handle_show_new_words()
        self._handle_learn_new_words()
        self._handle_answer()
        self._handle_difficulty()
        await self._dp.start_polling(self._bot_obj)

    def _start_cmd_handler(self) -> None:
        @self._dp.message(CommandStart())
        async def handle(msg: Message) -> None:
            keyboard = self._build_main_keyboard()
            await msg.answer(text=MsgsText.START.value, reply_markup=keyboard)

    async def _set_commands(self) -> None:
        commands = [BotCommand(command="start", description="Start cmd")]
        await self._bot_obj.set_my_commands(commands)

    def _build_main_keyboard(self) -> None:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=ButtonsText.NEW_WORDS.value),
                    KeyboardButton(text=ButtonsText.REPEAT.value),
                ],
                [
                    KeyboardButton(text=ButtonsText.ADD_WORD.value),
                ],
            ],
            resize_keyboard=True,
        )
        return keyboard

    def _handle_difficulty(self) -> None:
        @self._dp.message(F.text == ButtonsText.NEW_WORDS.value)
        async def handle(msg: Message) -> None:
            builder = InlineKeyboardBuilder()
            builder.button(
                text=ButtonsText.BASE.value, callback_data=ButtonsText.BASE.value
            )
            builder.button(
                text=ButtonsText.ADVANCED.value,
                callback_data=ButtonsText.ADVANCED.value,
            )
            builder.adjust(1)
            await msg.answer(
                text=MsgsText.CHOOSE_DIFF.value, reply_markup=builder.as_markup()
            )

    def _handle_show_new_words(self) -> None:
        @self._dp.callback_query(
            F.data.in_([ButtonsText.BASE.value, ButtonsText.ADVANCED.value])
        )
        async def handle(callback: CallbackQuery) -> None:
            chat_id = callback.message.chat.id
            diff = callback.data
            path = (
                Constants.BASE_WORDS_FILE_PATH.value
                if diff == ButtonsText.BASE.value
                else Constants.WORDS_FILE_PATH.value
            )
            words = choose_words(Constants.SHOW_COUNT.value, path)
            await self._redis_service.set_user_words(chat_id, words)
            ans = self._redis_service.show_all_words()
            builder = InlineKeyboardBuilder()
            builder.button(
                text=ButtonsText.TEST.value, callback_data=ButtonsText.TEST.value
            )
            builder.adjust(1)
            await callback.message.edit_text(
                text=f"{MsgsText.SHOWED_WORDS.value}{ans}",
                reply_markup=builder.as_markup(),
            )
            await callback.answer()

    def _build_choice_inline_keyboard(
        self, variants: list[str]
    ) -> InlineKeyboardBuilder:
        builder = InlineKeyboardBuilder()
        for v in variants:
            builder.button(text=v, callback_data=v)
        builder.adjust(1)
        return builder

    async def _generate_question(
        self,
        chat_id: int,
        state: FSMContext,
        word_data: tuple[dict[str, str] | str] | None = None,
        variants: list[str] | None = None,
    ) -> tuple[str | InlineKeyboardBuilder]:
        if not word_data:
            word_data = self._redis_service.show_word(chat_id)
            if not word_data:
                return
        if not variants:
            variants = choose_words(Constants.VARIANTS_COUNT.value)
        word_tr, redis_key = word_data
        word = list(word_tr.keys())[0]
        if word not in variants:
            variants.append(word)
        state_data = {"word_tr": word_tr, "redis_key": redis_key, "variants": variants}
        await state.update_data(state_data)
        await state.set_state(AnswerRequest.waiting_for_answer)
        builder = self._build_choice_inline_keyboard(variants)
        text = f"{MsgsText.TRANSLATE.value}{list(word_tr.values())[0]}"
        return text, builder

    async def _finish_cycle(self, callback: CallbackQuery) -> None:
        text = MsgsText.FINISH_LEARNING.value
        await callback.message.answer(text=text)
        await callback.answer()

    def _handle_learn_new_words(self) -> None:
        @self._dp.callback_query(F.data == ButtonsText.TEST.value)
        async def handle(callback: CallbackQuery, state: FSMContext):
            text, builder = await self._generate_question(
                callback.message.chat.id, state
            )
            await callback.message.edit_text(
                text=text,
                reply_markup=builder.as_markup(),
            )
            await callback.answer()

    def _handle_answer(self) -> None:
        @self._dp.callback_query(AnswerRequest.waiting_for_answer)
        async def handle(callback: CallbackQuery, state: FSMContext) -> None:
            chat_id = callback.message.chat.id
            ans = callback.data
            state_data = await state.get_data()
            word_tr, redis_key, variants = (
                state_data["word_tr"],
                state_data["redis_key"],
                state_data["variants"],
            )
            await state.clear()
            correct_ans = list(word_tr.keys())[0]
            if ans == correct_ans:
                if not await self._generate_question(chat_id, state):
                    await self._finish_cycle(callback)
                    return
                else:
                    self._redis_service.reduce_word_attempts_count(
                        chat_id, word_tr, redis_key
                    )
                    next_step = await self._generate_question(chat_id, state)
                    if not next_step:
                        await self._finish_cycle(callback)
                        return
                    text, builder = next_step
                    new_text = f"{MsgsText.CORRECT_ANSWER.value}{text}"
                    await callback.message.edit_text(
                        text=new_text, reply_markup=builder.as_markup()
                    )
                    await callback.answer()
            else:
                text, builder = await self._generate_question(
                    chat_id, state, (word_tr, redis_key), variants
                )
                new_text = f"{MsgsText.WRONG_ANS.value}{text}"
                await callback.message.edit_text(
                    text=new_text, reply_markup=builder.as_markup()
                )
                await callback.answer()
