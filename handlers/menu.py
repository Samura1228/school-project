from aiogram import Router, types, F
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database import get_user, get_leaderboard

router = Router()

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="PLAY SPRINT")
    builder.button(text="MY PROFILE")
    builder.button(text="LEADERBOARD")
    builder.button(text="HELP")
    builder.adjust(1, 2, 1)
    return builder.as_markup(resize_keyboard=True)

@router.message(F.text == "MY PROFILE")
async def show_profile(message: types.Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Please type /start to register first.")
        return
        
    # user: (id, username, xp, level, streak, last_played, best_score)
    username = user[1]
    xp = user[2]
    level = user[3]
    streak = user[4]
    best_score = user[6]
    
    xp_needed = level * 100
    
    text = (
        f"PROFILE: {username}\n"
        f"------------------\n"
        f"Level: {level}\n"
        f"XP: {xp}/{xp_needed}\n"
        f"Daily Streak: {streak} days\n"
        f"Best Score: {best_score}"
    )
    await message.answer(text)

@router.message(F.text == "LEADERBOARD")
async def show_leaderboard(message: types.Message):
    leaders = get_leaderboard()
    
    text = "LEADERBOARD\n------------------\n"
    for i, (name, lvl, xp, score) in enumerate(leaders, 1):
        text += f"{i}. {name} - Lvl {lvl} (Best: {score})\n"
        
    await message.answer(text)

@router.message(F.text == "HELP")
async def show_help(message: types.Message):
    text = (
        "HOW TO PLAY:\n"
        "1. Click PLAY SPRINT to start a session.\n"
        "2. Answer 10 questions as fast as you can.\n"
        "3. Earn XP for correct answers.\n"
        "4. Level up and climb the leaderboard!\n\n"
        "Daily Streak: Play every day to earn bonus XP!"
    )
    await message.answer(text)