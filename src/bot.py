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
from src.services.coordinator import Coordinator
from enum import Enum

import random


class ButtonsText(Enum):
    ADD_WORD = "Добавить слово для повторения ➕"
    DELETE_WORD = "Удалить слово из повторяемых ➖"
    TEST = "Тест 📝"
    NEW_WORDS = "Новые слова 📜"
    REPEAT = "Повторение 🔁"
    BASE = "Базовый"
    ADVANCED = "Продвинутый"


class MsgsText(Enum):
    START = "Bienvenido amigo! Желаю хорошо провести время за изучением нового ☝"
    CHOOSE_DIFF = "Выберите уровень сложности слов 🎮"
    SHOWED_WORDS = "Ваши слова 👇 Как запомните - жмите на кнопку 📝\n\n"
    TRANSLATE = "❓ Переведите слово: "
    WRONG_ANS = "Неправильно 😔\n"
    CORRECT_ANSWER = "Правильно ✔️\n"
    FINISH_LEARNING = (
        "Поздравляю! Вы выучили все новые слова и теперь они доступны для повторения. "
        "Так же можно получить ещё порцию новых слов 😎"
    )
    FINISH_REPEAT = "Поздравляю! Вы успешно закрепили знания 😎"
    NO_REPEAT = "У вас ещё нет сохранённых слов, начните с новых 📜"
    WRONG_WORD_INPUT = "Неверный формат ввода 🤔"
    CAN_NOT_DELETE = "В коллекции для повторения нет такого слова, нажмите снова 🙄"
    WORD_ADDED = " добавлено в коллекцию для повторения"
    WORD_DELETED = " успешно удалено 👌"
    ALREADY_HAS_WORD = "В коллекции для повторения уже есть данное слово, нажмите снова"
    TYPE_WORD_TO_ADD = "Введите русский вариант слова"
    TYPE_WORD_TO_DELETE = "Введите русский вариант слова из коллекции для повторения"
    IS_SPANISH = "Это испанское слово, нажмите снова 😅"


class Actions(Enum):
    NEW = "new"
    REPEAT = "repeat"


class AnswerRequest(StatesGroup):
    waiting_for_answer = State()


class AddWordRequest(StatesGroup):
    waiting_for_word = State()


class DeleteWordRequest(StatesGroup):
    waiting_for_word = State()


class LangBot:
    def __init__(self, dp: Dispatcher, bot_obj: Bot, coordinator: Coordinator) -> None:
        self._dp = dp
        self._bot_obj = bot_obj
        self._coordinator = coordinator

    async def start(self) -> None:
        await self._set_commands()
        self._start_cmd_handler()
        self._handle_show_new_words()
        self._handle_show_repeat_words()
        self._handle_test()
        self._handle_answer()
        self._handle_difficulty()
        self._handle_add_request()
        self._handle_del_request()
        self._handle_add_word()
        self._handle_delete_word()
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
                [
                    KeyboardButton(text=ButtonsText.DELETE_WORD.value),
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

    def _build_test_inline_keyboard(self, action: str) -> InlineKeyboardBuilder:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=ButtonsText.TEST.value,
            callback_data=f"{ButtonsText.TEST.value}:{action}",
        )
        builder.adjust(1)
        return builder

    def _handle_show_new_words(self) -> None:
        @self._dp.callback_query(
            F.data.in_([ButtonsText.BASE.value, ButtonsText.ADVANCED.value])
        )
        async def handle(callback: CallbackQuery) -> None:
            chat_id = callback.message.chat.id
            diff = callback.data
            is_base = True if diff == ButtonsText.BASE.value else False
            ans = await self._coordinator.show_words(chat_id, False, is_base)
            builder = self._build_test_inline_keyboard(Actions.NEW.value)
            await callback.message.edit_text(
                text=f"{MsgsText.SHOWED_WORDS.value}{ans}",
                reply_markup=builder.as_markup(),
            )
            await callback.answer()

    def _handle_show_repeat_words(self) -> None:
        @self._dp.message(F.text == ButtonsText.REPEAT.value)
        async def handle(msg: Message) -> None:
            chat_id = msg.chat.id
            ans = await self._coordinator.show_words(chat_id, True)
            if not ans:
                ans = MsgsText.NO_REPEAT.value
                await msg.answer(text=ans)
                return
            builder = self._build_test_inline_keyboard(Actions.REPEAT.value)
            await msg.answer(
                text=f"{MsgsText.SHOWED_WORDS.value}{ans}",
                reply_markup=builder.as_markup(),
            )

    def _build_choice_inline_keyboard(
        self, variants: list[str]
    ) -> InlineKeyboardBuilder:
        builder = InlineKeyboardBuilder()
        shuffled_variants = variants.copy()
        random.shuffle(shuffled_variants)
        for v in shuffled_variants:
            builder.button(text=v, callback_data=v)
        builder.adjust(1)
        return builder

    async def _generate_question(
        self,
        chat_id: int,
        state: FSMContext,
        action: str,
        word_tr: dict[str, str] = None,
        variants: list[str] | None = None,
    ) -> tuple[str | InlineKeyboardBuilder] | None:
        if not word_tr:
            if action == Actions.NEW.value:
                word_tr = await self._coordinator.get_random_word_or_save(chat_id, True)
            else:
                word_tr = await self._coordinator.get_random_word_or_save(chat_id)
            if not word_tr:
                return
        word = list(word_tr.keys())[0]
        if not variants:
            variants = await self._coordinator.get_random_variants(chat_id)
            while word in variants:
                variants = await self._coordinator.get_random_variants(chat_id)
        if word not in variants:
            variants.append(word)
        state_data = {
            "word_tr": word_tr,
            "variants": variants,
            "action": action,
        }
        await state.update_data(state_data)
        await state.set_state(AnswerRequest.waiting_for_answer)
        builder = self._build_choice_inline_keyboard(variants)
        text = f"{MsgsText.TRANSLATE.value}{list(word_tr.values())[0]}"
        return text, builder

    async def _finish_cycle(self, callback: CallbackQuery, text: str) -> None:
        await callback.message.answer(text=text)
        await callback.answer()

    def _handle_test(self) -> None:
        @self._dp.callback_query(F.data.startswith(ButtonsText.TEST.value))
        async def handle(callback: CallbackQuery, state: FSMContext):
            action = callback.data.split(":")[-1]
            text, builder = await self._generate_question(
                callback.message.chat.id, state, action=action
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
            word_tr, variants, action = (
                state_data["word_tr"],
                state_data["variants"],
                state_data["action"],
            )
            await state.clear()
            correct_ans = list(word_tr.keys())[0]
            if ans == correct_ans:
                await self._process_correct_ans(
                    callback, state, chat_id, word_tr, action
                )
            else:
                await self._process_wrong_ans(
                    callback, state, chat_id, word_tr, variants, action
                )

    async def _process_correct_ans(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        chat_id: int,
        word_tr: dict[str, str],
        action: str,
    ) -> None:
        self._coordinator.move_word(chat_id, word_tr)
        next_step = await self._generate_question(chat_id, state, action)
        if not next_step:
            ans = (
                MsgsText.FINISH_LEARNING.value
                if action == Actions.NEW.value
                else MsgsText.FINISH_REPEAT.value
            )
            await self._finish_cycle(callback, ans)
            return
        else:
            text, builder = next_step
            new_text = f"{MsgsText.CORRECT_ANSWER.value}{text}"
            await callback.message.edit_text(
                text=new_text, reply_markup=builder.as_markup()
            )
            await callback.answer()

    async def _process_wrong_ans(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        chat_id: int,
        word_tr: dict[str, str],
        variants: list[str],
        action: str,
    ) -> None:
        text, builder = await self._generate_question(
            chat_id, state, action, word_tr, variants
        )
        new_text = f"{MsgsText.WRONG_ANS.value}{text}"
        await callback.message.edit_text(
            text=new_text, reply_markup=builder.as_markup()
        )
        await callback.answer()

    def _handle_add_request(self) -> None:
        @self._dp.message(F.text == ButtonsText.ADD_WORD.value)
        async def handle(msg: Message, state: FSMContext) -> None:
            await state.set_state(AddWordRequest.waiting_for_word)
            await msg.answer(text=MsgsText.TYPE_WORD_TO_ADD.value)

    def _handle_del_request(self) -> None:
        @self._dp.message(F.text == ButtonsText.DELETE_WORD.value)
        async def handle(msg: Message, state: FSMContext) -> None:
            await state.set_state(DeleteWordRequest.waiting_for_word)
            await msg.answer(text=MsgsText.TYPE_WORD_TO_DELETE.value)

    def _handle_add_word(self) -> None:
        @self._dp.message(AddWordRequest.waiting_for_word)
        async def handle(msg: Message, state: FSMContext) -> None:
            chat_id = msg.chat.id
            word = msg.text
            if not self._coordinator.validate_input_word(word):
                await msg.answer(text=MsgsText.WRONG_WORD_INPUT.value)
                return
            try:
                res = await self._coordinator.add_user_word(chat_id, word)
            except ValueError:
                await msg.answer(text=MsgsText.IS_SPANISH.value)
                return
            ans = (
                f"{res}{MsgsText.WORD_ADDED.value}"
                if res
                else MsgsText.ALREADY_HAS_WORD.value
            )
            await state.clear()
            await msg.answer(text=ans)

    def _handle_delete_word(self) -> None:
        @self._dp.message(DeleteWordRequest.waiting_for_word)
        async def handle(msg: Message, state) -> None:
            chat_id = msg.chat.id
            word = msg.text
            if not self._coordinator.validate_input_word(word):
                await msg.answer(text=MsgsText.WRONG_WORD_INPUT.value)
                return
            res = await self._coordinator.delete_user_word(chat_id, word)
            ans = (
                f"{res}{MsgsText.WORD_DELETED.value}"
                if res
                else MsgsText.CAN_NOT_DELETE.value
            )
            await state.clear()
            await msg.answer(text=ans)
