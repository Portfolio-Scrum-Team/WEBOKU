SYMBOL_BONUSES = {
    1: 2,
    2: 4,
    3: 6,
    4: 8,
    5: 10,
    6: 12,
    7: 14,
    8: 18,
    9: 26,
}

CORRECT_MOVE_POINTS = 10
OBJECTIVE_COMPLETION_POINTS = 100

FORWARD_RING_POINTS = {
    5: 10,
    4: 15,
    3: 20,
    2: 25,
    1: 30,
}


class Scoring:
    def __init__(self):
        self.score = 0

    def add_correct_move(self, value):
        if value not in SYMBOL_BONUSES:
            raise ValueError("Value must be between 1 and 9")

        self.score += CORRECT_MOVE_POINTS
        self.score += SYMBOL_BONUSES[value]

    def add_objective_completion(self, count=1):
        if count < 1:
            raise ValueError("Count must be at least 1")

        self.score += OBJECTIVE_COMPLETION_POINTS * count

    def add_movement(self, points):
        if points < 0:
            raise ValueError("Points cannot be negative")

        self.score += points

    def add_final_bonus(self, points):
        if points < 0:
            raise ValueError("Points cannot be negative")

        self.score += points

    def add_rescue_credit_bonus(self, credits, points_per_credit=100):
        if credits < 0:
            raise ValueError("Credits cannot be negative")

        if points_per_credit < 0:
            raise ValueError("Points per credit cannot be negative")

        self.score += credits * points_per_credit

    def reset(self):
        self.score = 0