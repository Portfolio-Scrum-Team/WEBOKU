from weboku.scoring import (
    Scoring,
    SYMBOL_BONUSES,
)


def test_scoring_starts_at_zero():
    scoring = Scoring()

    assert scoring.score == 0


def test_correct_move_value_1():
    scoring = Scoring()

    scoring.add_correct_move(1)

    assert scoring.score == 12


def test_correct_move_value_5():
    scoring = Scoring()

    scoring.add_correct_move(5)

    assert scoring.score == 20


def test_correct_move_value_9():
    scoring = Scoring()

    scoring.add_correct_move(9)

    assert scoring.score == 36


def test_symbol_bonuses_total_100():
    assert sum(SYMBOL_BONUSES.values()) == 100


def test_objective_completion():
    scoring = Scoring()

    scoring.add_objective_completion()

    assert scoring.score == 100


def test_multiple_objective_completions():
    scoring = Scoring()

    scoring.add_objective_completion(3)

    assert scoring.score == 300


def test_movement_points():
    scoring = Scoring()

    scoring.add_movement(15)

    assert scoring.score == 15


def test_final_bonus():
    scoring = Scoring()

    scoring.add_final_bonus(500)

    assert scoring.score == 500


def test_rescue_credit_bonus():
    scoring = Scoring()

    scoring.add_rescue_credit_bonus(3)

    assert scoring.score == 300


def test_rescue_credit_bonus_with_custom_value():
    scoring = Scoring()

    scoring.add_rescue_credit_bonus(3, 200)

    assert scoring.score == 600


def test_invalid_correct_move_value():
    scoring = Scoring()

    try:
        scoring.add_correct_move(10)
        assert False
    except ValueError:
        assert True


def test_invalid_objective_count():
    scoring = Scoring()

    try:
        scoring.add_objective_completion(0)
        assert False
    except ValueError:
        assert True


def test_negative_movement_points():
    scoring = Scoring()

    try:
        scoring.add_movement(-10)
        assert False
    except ValueError:
        assert True


def test_negative_final_bonus():
    scoring = Scoring()

    try:
        scoring.add_final_bonus(-100)
        assert False
    except ValueError:
        assert True


def test_negative_rescue_credits():
    scoring = Scoring()

    try:
        scoring.add_rescue_credit_bonus(-1)
        assert False
    except ValueError:
        assert True


def test_negative_points_per_credit():
    scoring = Scoring()

    try:
        scoring.add_rescue_credit_bonus(2, -100)
        assert False
    except ValueError:
        assert True


def test_scoring_reset():
    scoring = Scoring()

    scoring.add_correct_move(9)
    scoring.add_objective_completion()
    scoring.add_movement(15)

    scoring.reset()

    assert scoring.score == 0
