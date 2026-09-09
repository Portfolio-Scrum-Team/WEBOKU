import json

import pytest

from weboku.save_load import SaveLoad, SaveLoadError, load_game, save_game


class FakeGame:
    def __init__(self):
        self.score = 1234
        self.difficulty = "beginner"
        self.game_status = "PLAYING"
        self.princess_life = 27
        self.rescue_credits = 0
        self.failed_timeouts = 0
        self.completed_rings = {1, 2, 3}
        self.completed_columns = {4, 5}
        self.completed_regions = {6, 7, 8}
        self.active_column = 2
        self.current_position = (5, 2)
        self.board = {"values": [[None for _ in range(9)] for _ in range(9)]}


@pytest.fixture
def fake_game():
    return FakeGame()


def test_save_creates_json(tmp_path, fake_game):
    path = tmp_path / "save.json"

    save_game(fake_game, path)

    assert path.exists()


def test_save_contains_version(tmp_path, fake_game):
    path = tmp_path / "save.json"

    save_game(fake_game, path)
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["version"] == 1


def test_save_contains_expected_game_state(tmp_path, fake_game):
    path = tmp_path / "save.json"

    save_game(fake_game, path)
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["game"]["score"] == 1234
    assert data["game"]["difficulty"] == "beginner"
    assert data["game"]["current_position"] == [5, 2]
    assert data["game"]["princess_life"] == 27


def test_json_is_valid(tmp_path, fake_game):
    path = tmp_path / "save.json"

    save_game(fake_game, path)
    loaded = json.loads(path.read_text(encoding="utf-8"))

    assert isinstance(loaded, dict)
    assert "game" in loaded


def test_load_restores_saved_data(tmp_path, fake_game):
    path = tmp_path / "save.json"

    save_game(fake_game, path)
    loaded = load_game(path)

    assert loaded["game"]["score"] == 1234
    assert loaded["game"]["current_position"] == [5, 2]
    assert loaded["game"]["difficulty"] == "beginner"


def test_tuple_position_round_trips_correctly(tmp_path, fake_game):
    path = tmp_path / "save.json"

    save_game(fake_game, path)
    loaded = load_game(path)

    assert loaded["game"]["current_position"] == [5, 2]


def test_invalid_json_rejected(tmp_path):
    path = tmp_path / "save.json"
    path.write_text("not json", encoding="utf-8")

    with pytest.raises((ValueError, SaveLoadError)):
        load_game(path)


def test_missing_version_rejected(tmp_path):
    path = tmp_path / "save.json"
    path.write_text(json.dumps({"game": {"score": 10}}), encoding="utf-8")

    with pytest.raises((ValueError, SaveLoadError)):
        load_game(path)


def test_unsupported_version_rejected(tmp_path):
    path = tmp_path / "save.json"
    data = {"version": 2, "game": {"score": 10, "difficulty": "beginner", "princess_life": 27}}
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises((ValueError, SaveLoadError)):
        load_game(path)


def test_invalid_princess_life_rejected(tmp_path):
    path = tmp_path / "save.json"
    data = {"version": 1, "game": {"score": 10, "difficulty": "beginner", "princess_life": 28}}
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises((ValueError, SaveLoadError)):
        load_game(path)


def test_invalid_objective_counts_rejected(tmp_path):
    path = tmp_path / "save.json"
    data = {"version": 1, "game": {"score": 10, "difficulty": "beginner", "princess_life": 27, "completed_rings": [10]}}
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises((ValueError, SaveLoadError)):
        load_game(path)


def test_duplicate_objective_values_rejected(tmp_path):
    path = tmp_path / "save.json"
    data = {"version": 1, "game": {"score": 10, "difficulty": "beginner", "princess_life": 27, "completed_rings": [1, 1, 2]}}
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises((ValueError, SaveLoadError)):
        load_game(path)


def test_invalid_difficulty_rejected(tmp_path):
    path = tmp_path / "save.json"
    data = {"version": 1, "game": {"score": 10, "difficulty": "godmode", "princess_life": 27}}
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises((ValueError, SaveLoadError)):
        load_game(path)


def test_invalid_position_rejected(tmp_path):
    path = tmp_path / "save.json"
    data = {"version": 1, "game": {"score": 10, "difficulty": "beginner", "princess_life": 27, "current_position": [9, 10]}}
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises((ValueError, SaveLoadError)):
        load_game(path)


def test_pickle_is_not_used(tmp_path, fake_game):
    path = tmp_path / "save.json"

    save_game(fake_game, path)
    text = path.read_text(encoding="utf-8")

    assert "pickle" not in text.lower()


def test_save_load_does_not_award_score_or_complete_objectives(tmp_path, fake_game):
    path = tmp_path / "save.json"

    save_game(fake_game, path)
    loaded = load_game(path)

    assert loaded["game"]["score"] == fake_game.score
    assert loaded["game"]["completed_rings"] == [1, 2, 3]
    assert loaded["game"]["current_position"] == [5, 2]


def test_save_load_class_works(tmp_path, fake_game):
    path = tmp_path / "save.json"
    saver = SaveLoad()

    saver.save(fake_game, path)
    loaded = saver.load(path)

    assert loaded["game"]["score"] == 1234
    assert loaded["game"]["difficulty"] == "beginner"
