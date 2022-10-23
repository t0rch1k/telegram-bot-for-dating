import logging
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from create_bot import Bot, dp
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from database import sqlliteClient
import KeyBoards.KeyBoards as KB


async def main_menu(message: types.Message, state: FSMContext):
    global cur_pos
    info = sqlliteClient.check_if_exist(message.from_user.id)
    if info:
        await message.answer("Choose an action on the keyboard", reply_markup=KB.main_menu_KeyBoard)
    else:
        await cm_start(message, state)


async def change_anket_menu(message: types.Message):
    info = sqlliteClient.take_user_info(message.from_user.id)
    await message.answer_photo(photo=info[0][5], caption= \
        f"{info[0][1]}, {info[0][2]}\n {info[0][4]}", reply_markup=KB.change_anket_menu)


async def back_to_main_menu(message: types.Message):
    await message.answer("Select an action on the keyboard", reply_markup=KB.main_menu_KeyBoard)


ankets = []
num_anket = 0

async def show_ankets(message: types.Message):
    global ankets
    global num_anket
    ankets = sqlliteClient.take_all_ankets()

    for anket in ankets:
        if anket[0] == message.from_user.id:
            num_anket = anket[6]
            break

    await message.answer_photo(photo=ankets[num_anket][5], caption= \
        f"{ankets[num_anket][1]}, {ankets[num_anket][2]}\n {ankets[num_anket][4]}", reply_markup=KB.next_anket)


async def next_anket(callback: types.CallbackQuery):
    global ankets
    global num_anket
    try:
        num_anket += 1
        sqlliteClient.increase_cur_anket(callback.from_user.id, num_anket)

        await callback.message.answer_photo(photo=ankets[num_anket][5], caption= \
            f"{ankets[num_anket][1]}, {ankets[num_anket][2]}\n {ankets[num_anket][4]}", reply_markup=KB.next_anket)
    except IndexError as e:
        await callback.message.answer("All profiles have already been viewed", reply_markup=KB.end_anekets_KeyBoard)


async def reload_ankets(message: types.Message):
    if num_anket == len(ankets):
        sqlliteClient.reload_ankets(message.from_user.id)
    else:
        pass


class FSMCChangeAnket(StatesGroup):
    answer = State()


async def message_change_photo(message: types.Message, state=None):
    await FSMCChangeAnket.answer.set()
    await message.answer("Submit a new photo")


async def take_modified_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    user_id = message.from_user.id
    sqlliteClient.change_photo(user_id, photo)
    await message.answer("Photo has been updated")
    await state.finish()


async def message_change_description(message: types.Message, state=None):
    await FSMCChangeAnket.answer.set()
    await message.answer("Submit a new description")


async def take_modified_description(message: types.Message, state: FSMContext):
    description = message.text
    user_id = message.from_user.id
    sqlliteClient.change_description(user_id, description)
    await message.answer("Description has been updated")
    await state.finish()


async def delete_profile(message: types.Message):
    sqlliteClient.delete_user(message.from_user.id)
    await message.answer("Your profile has been deleted")


class FSMClient(StatesGroup):
    name = State()
    age = State()
    sex = State()
    description = State()
    photo = State()


async def cm_start(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["id"] = message.from_user.id

    await FSMClient.name.set()
    await message.answer('Enter your name')


async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMClient.next()
    await message.answer("Enter your age")


async def load_age(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text
    builder = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    builder.add(types.KeyboardButton(text='the male'))
    builder.add(types.KeyboardButton(text='women'))

    await FSMClient.next()
    await message.answer("Enter your gender", reply_markup=builder)


async def load_sex(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sex'] = message.text

    remove = ReplyKeyboardRemove()

    await FSMClient.next()
    await message.answer("Enter your description", reply_markup=remove)


async def load_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text

    await FSMClient.next()
    await message.answer("Attach your photo")


async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
        data['cur_anket'] = 0

    await sqlliteClient.sql_add_command(state)
    logging.info(f"The user data was recorded")
    await message.answer("All information is recorded")
    await state.finish()


def register_handlers_client(dp: Dispatcher):

    dp.register_message_handler(main_menu, Text(equals="Main menu", ignore_case=True))
    dp.register_message_handler(main_menu, commands='start')

    dp.register_message_handler(back_to_main_menu, Text(equals="Cancel", ignore_case=True))

    dp.register_message_handler(reload_ankets, Text(equals="View old profiles"))

    dp.register_callback_query_handler(next_anket, Text(equals="next"))

    dp.register_message_handler(show_ankets, Text(equals="View all profiles", ignore_case=True))

    dp.register_message_handler(change_anket_menu, Text(equals="My profile", ignore_case=True))

    dp.register_message_handler(message_change_photo, Text(equals="Edit photo", ignore_case=True), state=None)
    dp.register_message_handler(take_modified_photo, state=FSMCChangeAnket.answer, content_types=['photo'])

    dp.register_message_handler(message_change_description, Text(equals="Edit Description", ignore_case=True), state=None)
    dp.register_message_handler(take_modified_description, state=FSMCChangeAnket.answer)

    dp.register_message_handler(load_name, state=FSMClient.name)
    dp.register_message_handler(load_age, lambda message: message.text.isdigit(), state=FSMClient.age)
    dp.register_message_handler(load_sex, lambda message: message.text in ['M', "m", "W", "w"], state=FSMClient.sex)
    dp.register_message_handler(load_description, state=FSMClient.description)
    dp.register_message_handler(load_photo, state=FSMClient.photo, content_types=['photo'])

