from aiogram import Router, types, F
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database import get_user, get_leaderboard, get_user_language
from utils.localization import get_text

router = Router()

def get_main_menu(user_id):
    lang = get_user_language(user_id)
    builder = ReplyKeyboardBuilder()
    builder.button(text=get_text("menu_play", lang))
    builder.button(text=get_text("menu_profile", lang))
    builder.button(text=get_text("menu_leaderboard", lang))
    builder.button(text=get_text("menu_settings", lang))
    builder.button(text=get_text("menu_help", lang))
    builder.adjust(1, 2, 2)
    return builder.as_markup(resize_keyboard=True)

@router.message(lambda message: message.text in [get_text("menu_profile", "en"), get_text("menu_profile", "ru")])
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    user = get_user(user_id)
    
    if not user:
        await message.answer(get_text("register_first", lang))
        return
        
    # user: (id, username, xp, level, streak, last_played, best_score, language)
    username = user[1]
    xp = user[2]
    level = user[3]
    streak = user[4]
    best_score = user[6]
    
    xp_needed = level * 100
    
    text = (
        f"{get_text('profile_title', lang, username=username)}\n"
        f"------------------\n"
        f"{get_text('level', lang)}: {level}\n"
        f"{get_text('xp', lang)}: {xp}/{xp_needed}\n"
        f"{get_text('streak', lang)}: {streak} {get_text('days', lang)}\n"
        f"{get_text('best_score', lang)}: {best_score}"
    )
    await message.answer(text)

@router.message(lambda message: message.text in [get_text("menu_leaderboard", "en"), get_text("menu_leaderboard", "ru")])
async def show_leaderboard(message: types.Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    leaders = get_leaderboard()
    
    text = f"{get_text('leaderboard_title', lang)}\n------------------\n"
    for i, (name, lvl, xp, score) in enumerate(leaders, 1):
        text += f"{i}. {name} - Lvl {lvl} ({get_text('best_score', lang)}: {score})\n"
        
    await message.answer(text)

@router.message(lambda message: message.text in [get_text("menu_help", "en"), get_text("menu_help", "ru")])
async def show_help(message: types.Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    await message.answer(get_text("help_text", lang))