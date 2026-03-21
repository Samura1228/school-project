from aiogram import Router, types, F
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database import get_user_language, set_user_language
from utils.localization import get_text
from handlers.menu import get_main_menu

router = Router()

@router.message(lambda message: message.text in [get_text("menu_settings", "en"), get_text("menu_settings", "ru")])
async def show_settings(message: types.Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    builder = ReplyKeyboardBuilder()
    builder.button(text=get_text("change_language", lang))
    builder.button(text=get_text("back", lang))
    builder.adjust(1)
    
    await message.answer(
        get_text("settings_title", lang),
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@router.message(lambda message: message.text in [get_text("change_language", "en"), get_text("change_language", "ru")])
async def change_language(message: types.Message):
    user_id = message.from_user.id
    current_lang = get_user_language(user_id)
    
    # Toggle language
    new_lang = 'ru' if current_lang == 'en' else 'en'
    set_user_language(user_id, new_lang)
    
    await message.answer(
        get_text("language_changed", new_lang),
        reply_markup=get_main_menu(user_id)
    )

@router.message(lambda message: message.text in [get_text("back", "en"), get_text("back", "ru")])
async def back_to_menu(message: types.Message):
    user_id = message.from_user.id
    await message.answer(
        get_text("menu_play", get_user_language(user_id)), # Just a placeholder text, the keyboard is what matters
        reply_markup=get_main_menu(user_id)
    )