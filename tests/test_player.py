from weboku.player import Player


def test_player_defaults():
    player = Player()
    assert player.name == "Player"
    assert str(player) == "Player"


def test_player_custom_name():
    player = Player("Nicole")
    assert player.name == "Nicole"
    assert str(player) == "Nicole"
