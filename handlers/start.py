import logging
from aiogram import Router, types
from aiogram.filters import Command
from database import add_user
from handlers.menu import get_main_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    logging.info(f"Received /start command from {message.from_user.id}")
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    try:
        add_user(user_id, username)
        logging.info(f"User {user_id} added to database")
    except Exception as e:
        logging.error(f"Error adding user to database: {e}")
    
    await message.answer(
        f"Welcome to Economic Sprint, {username}!\n\n"
        "Improve your economic skills with quick 2-3 minute challenges.\n"
        "Earn XP, level up, and compete on the leaderboard!",
        reply_markup=get_main_menu()
    )