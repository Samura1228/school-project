from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database import get_random_questions, update_xp, update_streak, update_best_score, get_user_language, get_user
from utils.game_logic import calculate_xp, calculate_streak_bonus
from utils.localization import get_text
from handlers.menu import get_main_menu

router = Router()

class GameStates(StatesGroup):
    playing = State()

@router.message(lambda message: message.text in [get_text("menu_play", "en"), get_text("menu_play", "ru")])
async def start_game(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    questions = get_random_questions(10)
    
    if not questions:
        await message.answer(get_text("no_questions", lang))
        return
        
    await state.set_state(GameStates.playing)
    await state.update_data(
        questions=questions,
        current_index=0,
        score=0,
        xp_gained=0,
        lang=lang
    )
    
    await send_question(message, questions[0], 0, 10, lang)

async def send_question(message: types.Message, question, index, total, lang):
    text_key = f"text_{lang}"
    options_key = f"options_{lang}"
    
    question_text = question.get(text_key, question['text_en'])
    options = question.get(options_key, question['options_en'])
    
    header = get_text("question_header", lang, current=index+1, total=total)
    text = f"{header}\n\n{question_text}"
    
    builder = ReplyKeyboardBuilder()
    for option in options:
        builder.button(text=option)
    builder.adjust(2)
    
    await message.answer(text, reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(GameStates.playing)
async def handle_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data['questions']
    current_index = data['current_index']
    lang = data['lang']
    current_question = questions[current_index]
    
    user_answer = message.text
    
    options_key = f"options_{lang}"
    options = current_question.get(options_key, current_question['options_en'])
    correct_option = options[current_question['correct_index']]
    
    is_correct = (user_answer == correct_option)
    
    xp = calculate_xp(is_correct, current_question['difficulty'])
    new_score = data['score'] + (10 if is_correct else 0)
    new_xp = data['xp_gained'] + xp
    
    feedback = get_text("correct", lang) if is_correct else get_text("wrong", lang, answer=correct_option)
    await message.answer(feedback)
    
    next_index = current_index + 1
    
    if next_index < len(questions):
        await state.update_data(
            current_index=next_index,
            score=new_score,
            xp_gained=new_xp
        )
        await send_question(message, questions[next_index], next_index, len(questions), lang)
    else:
        await finish_game(message, state, new_score, new_xp, lang)

async def finish_game(message: types.Message, state: FSMContext, score, xp_gained, lang):
    user_id = message.from_user.id
    
    # Update Streak
    streak_updated = update_streak(user_id)
    streak_bonus = 0
    if streak_updated:
        user = get_user(user_id)
        streak_bonus = calculate_streak_bonus(user[4])
        xp_gained += streak_bonus
        
    # Update XP and Level
    leveled_up = update_xp(user_id, xp_gained)
    
    # Update Best Score
    update_best_score(user_id, score)
    
    summary = (
        f"{get_text('sprint_finished', lang)}\n\n"
        f"{get_text('score', lang)}: {score}/100\n"
        f"{get_text('xp_gained', lang)}: {xp_gained}\n"
    )
    
    if streak_bonus > 0:
        summary += f"{get_text('streak_bonus', lang)}: +{streak_bonus} XP\n"
        
    if leveled_up:
        summary += f"{get_text('level_up', lang)}\n"
        
    await message.answer(summary, reply_markup=get_main_menu(user_id))
    await state.clear()