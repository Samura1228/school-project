from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database import get_random_questions, update_xp, update_streak, update_best_score
from utils.game_logic import calculate_xp, calculate_streak_bonus

router = Router()

class GameStates(StatesGroup):
    playing = State()

@router.message(F.text == "PLAY SPRINT")
async def start_game(message: types.Message, state: FSMContext):
    questions = get_random_questions(10)
    
    if not questions:
        await message.answer("No questions available yet. Please contact admin.")
        return
        
    await state.set_state(GameStates.playing)
    await state.update_data(
        questions=questions,
        current_index=0,
        score=0,
        xp_gained=0
    )
    
    await send_question(message, questions[0], 0)

async def send_question(message: types.Message, question, index):
    text = f"Question {index + 1}/10:\n\n{question['text']}"
    
    builder = ReplyKeyboardBuilder()
    for option in question['options']:
        builder.button(text=option)
    builder.adjust(2)
    
    await message.answer(text, reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(GameStates.playing)
async def handle_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data['questions']
    current_index = data['current_index']
    current_question = questions[current_index]
    
    user_answer = message.text
    correct_option = current_question['options'][current_question['correct_index']]
    
    is_correct = (user_answer == correct_option)
    
    xp = calculate_xp(is_correct, current_question['difficulty'])
    new_score = data['score'] + (10 if is_correct else 0)
    new_xp = data['xp_gained'] + xp
    
    feedback = "✅ Correct!" if is_correct else f"❌ Wrong. Answer: {correct_option}"
    await message.answer(feedback)
    
    next_index = current_index + 1
    
    if next_index < len(questions):
        await state.update_data(
            current_index=next_index,
            score=new_score,
            xp_gained=new_xp
        )
        await send_question(message, questions[next_index], next_index)
    else:
        await finish_game(message, state, new_score, new_xp)

async def finish_game(message: types.Message, state: FSMContext, score, xp_gained):
    user_id = message.from_user.id
    
    # Update Streak
    streak_updated = update_streak(user_id)
    streak_bonus = 0
    if streak_updated:
        # Fetch new streak to calculate bonus
        from database import get_user
        user = get_user(user_id)
        streak_bonus = calculate_streak_bonus(user[4])
        xp_gained += streak_bonus
        
    # Update XP and Level
    leveled_up = update_xp(user_id, xp_gained)
    
    # Update Best Score
    update_best_score(user_id, score)
    
    summary = (
        f"🏁 SPRINT FINISHED!\n\n"
        f"Score: {score}/100\n"
        f"XP Gained: {xp_gained}\n"
    )
    
    if streak_bonus > 0:
        summary += f"🔥 Streak Bonus: +{streak_bonus} XP\n"
        
    if leveled_up:
        summary += f"🎉 LEVEL UP!\n"
        
    from handlers.menu import get_main_menu
    await message.answer(summary, reply_markup=get_main_menu())
    await state.clear()