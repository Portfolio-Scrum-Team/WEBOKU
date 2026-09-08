from weboku.climber import Climber


def test_climber_starts_at_base():
    climber = Climber()

    assert climber.current_ring is None
    assert climber.current_column is None
    assert climber.at_base is True
    assert climber.at_roof is False
    assert climber.position is None
def test_climber_moves_to_position():
    climber = Climber()

    climber.move_to(5, 2)

    assert climber.current_ring == 5
    assert climber.current_column == 2
    assert climber.position == (5, 2)
    assert climber.at_base is False
def test_climber_records_movement_history():
    climber = Climber()

    climber.move_to(5, 2)

    assert climber.movement_history == [
        {
            "from": None,
            "to": (5, 2),
        }
    ]

    climber.move_to(4, 2)

    assert climber.movement_history == [
        {
            "from": None,
            "to": (5, 2),
        },
        {
            "from": (5, 2),
            "to": (4, 2),
        },
    ]
def test_climber_rejects_invalid_ring():
    climber = Climber()

    try:
        climber.move_to(10, 2)
        assert False
    except ValueError:
        assert True


def test_climber_rejects_invalid_column():
    climber = Climber()

    try:
        climber.move_to(5, 10)
        assert False
    except ValueError:
        assert True
def test_climber_reset():
    climber = Climber()

    climber.move_to(5, 2)
    climber.move_to(4, 2)

    climber.reset()

    assert climber.current_ring is None
    assert climber.current_column is None
    assert climber.at_base is True
    assert climber.at_roof is False
    assert climber.position is None
    assert climber.movement_history == []
def test_climber_reaches_princess():
    climber = Climber()

    climber.move_to(1, 9)
    climber.reach_princess()

    assert climber.at_roof is True
    assert climber.at_base is False
    assert climber.has_reached_princess() is True