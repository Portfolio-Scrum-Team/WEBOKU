import time

from weboku.timer import GameTimer


def test_timer_starts_stopped():
    timer = GameTimer(60)

    assert timer._start_time is None
    assert timer.elapsed == 0
    assert timer.remaining == 60
    assert timer.expired is False


def test_timer_starts():
    timer = GameTimer(60)

    timer.start()

    assert timer._start_time is not None


def test_timer_elapsed_increases():
    timer = GameTimer(60)

    timer.start()

    time.sleep(0.05)

    assert timer.elapsed > 0


def test_timer_remaining_decreases():
    timer = GameTimer(60)

    timer.start()

    time.sleep(0.05)

    assert timer.remaining < 60
    assert timer.remaining > 0


def test_timer_stop():
    timer = GameTimer(60)

    timer.start()

    time.sleep(0.05)

    timer.stop()

    elapsed_when_stopped = timer.elapsed

    time.sleep(0.05)

    assert timer.elapsed == elapsed_when_stopped


def test_timer_reset():
    timer = GameTimer(60)

    timer.start()

    time.sleep(0.05)

    timer.reset()

    assert timer._start_time is None
    assert timer.elapsed == 0
    assert timer.remaining == 60
    assert timer.expired is False


def test_timer_expires():
    timer = GameTimer(0.05)

    timer.start()

    time.sleep(0.1)

    assert timer.expired is True
    assert timer.remaining == 0


def test_timer_does_not_control_game_over():
    timer = GameTimer(0.05)

    timer.start()

    time.sleep(0.1)

    # The timer only reports that it expired.
    # Game is responsible for deciding what happens next.
    assert timer.expired is True
