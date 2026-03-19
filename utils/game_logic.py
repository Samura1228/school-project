def calculate_xp(is_correct, difficulty):
    if is_correct:
        return 10 * difficulty
    else:
        return 1

def calculate_level(xp):
    level = 1
    xp_needed = 100
    
    while xp >= xp_needed:
        xp -= xp_needed
        level += 1
        xp_needed = level * 100
        
    return level

def calculate_streak_bonus(streak):
    return streak * 5