import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import create_tables, add_question, get_random_questions
from handlers import start, menu, game

# Configure logging
logging.basicConfig(level=logging.INFO)

async def load_initial_questions():
    # Check if questions exist
    existing = get_random_questions(1)
    if not existing:
        logging.info("Loading initial questions...")
        try:
            with open('data/questions.json', 'r') as f:
                questions = json.load(f)
                for q in questions:
                    add_question(q['text'], q['options'], q['correct_index'], q['difficulty'])
            logging.info(f"Loaded {len(questions)} questions.")
        except Exception as e:
            logging.error(f"Error loading questions: {e}")

async def main():
    # Initialize Database
    create_tables()
    await load_initial_questions()

    # Initialize Bot and Dispatcher
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        logging.error("BOT_TOKEN is not set in .env file!")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register Routers
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(game.router)

    # Start Polling
    logging.info("Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped!")