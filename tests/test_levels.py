import pytest

from weboku.levels import LEVELS, get_level, get_time_limit


def test_all_four_levels_exist():
    assert set(LEVELS.keys()) == {
        "beginner",
        "intermediate",
        "advanced",
        "pro",
    }


def test_beginner_time_limit():
    assert get_time_limit("beginner") == 600


def test_intermediate_time_limit():
    assert get_time_limit("intermediate") == 300


def test_advanced_time_limit():
    assert get_time_limit("advanced") == 120


def test_pro_time_limit():
    assert get_time_limit("pro") == 60


def test_get_beginner_level():
    level = get_level("beginner")

    assert level["name"] == "Beginner"
    assert level["seconds"] == 600


def test_get_intermediate_level():
    level = get_level("intermediate")

    assert level["name"] == "Intermediate"
    assert level["seconds"] == 300


def test_get_advanced_level():
    level = get_level("advanced")

    assert level["name"] == "Advanced"
    assert level["seconds"] == 120


def test_get_pro_level():
    level = get_level("pro")

    assert level["name"] == "Pro"
    assert level["seconds"] == 60


def test_invalid_level():
    with pytest.raises(ValueError):
        get_level("expert")


def test_invalid_time_limit():
    with pytest.raises(ValueError):
        get_time_limit("expert")