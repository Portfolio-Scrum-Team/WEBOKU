"""Minimal JSON save/load support for Weboku."""

from __future__ import annotations

import json
from pathlib import Path

SAVE_VERSION = 1
VALID_DIFFICULTIES = {"beginner", "easy", "normal", "hard", "expert"}
VALID_GAME_STATUS = {"READY", "PLAYING", "VICTORY", "GAME_OVER"}


class SaveLoadError(ValueError):
    """Raised when a save file is invalid or unsupported."""


def _json_safe(value):
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_safe(val) for key, val in value.items()}
    return value


def _validate_objective_list(values, label):
    if values is None:
        return []
    if not isinstance(values, list):
        raise SaveLoadError(f"Invalid {label}: expected a list.")

    result = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int):
            raise SaveLoadError(f"Invalid {label}: values must be integers.")
        if not 1 <= value <= 9:
            raise SaveLoadError(f"Invalid {label}: value outside 1-9.")
        if value in result:
            raise SaveLoadError(f"Invalid {label}: duplicate values are not allowed.")
        result.append(value)
    return result


def _validate_position(position):
    if position is None:
        return None
    if isinstance(position, str):
        pos = position.upper()
        if pos in {"BASE", "ROOF"}:
            return pos
        raise SaveLoadError(f"Invalid current position: {position!r}")
    if isinstance(position, (tuple, list)):
        if len(position) != 2:
            raise SaveLoadError("Invalid current position: must be a two-item list/tuple.")
        row, column = position
        if isinstance(row, bool) or isinstance(column, bool):
            raise SaveLoadError("Invalid current position: booleans are not valid positions.")
        if not isinstance(row, int) or not isinstance(column, int):
            raise SaveLoadError("Invalid current position: row and column must be integers.")
        if not (1 <= row <= 9 and 1 <= column <= 9):
            raise SaveLoadError("Invalid current position: must be within R1C1 to R9C9.")
        return [row, column]
    raise SaveLoadError("Invalid current position: unsupported type.")


class SaveLoad:
    def save(self, game, path):
        payload = {
            "version": SAVE_VERSION,
            "game": self._game_to_dict(game),
        }

        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(_json_safe(payload), ensure_ascii=False, indent=2), encoding="utf-8")
        return {"success": True, "path": str(file_path)}

    def load(self, path):
        file_path = Path(path)
        try:
            text = file_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise SaveLoadError("Save file not found.") from exc

        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SaveLoadError("Invalid JSON save file.") from exc

        if not isinstance(payload, dict):
            raise SaveLoadError("Save file must contain a JSON object.")
        if "version" not in payload:
            raise SaveLoadError("Missing save version.")
        if payload.get("version") != SAVE_VERSION:
            raise SaveLoadError(f"Unsupported save version: {payload.get('version')!r}")
        if "game" not in payload or not isinstance(payload["game"], dict):
            raise SaveLoadError("Missing or invalid top-level game data.")

        return self._validate_game_data(payload["game"])

    def _game_to_dict(self, game):
        data = {}

        for key in (
            "score",
            "difficulty",
            "game_status",
            "princess_life",
            "rescue_credits",
            "failed_timeouts",
            "completed_rings",
            "completed_columns",
            "completed_regions",
            "active_column",
            "current_position",
            "board",
        ):
            if hasattr(game, key):
                value = getattr(game, key)
                if isinstance(value, set):
                    value = sorted(value)
                elif isinstance(value, tuple):
                    value = list(value)
                data[key] = value

        if "completed_rings" not in data:
            data["completed_rings"] = []
        if "completed_columns" not in data:
            data["completed_columns"] = []
        if "completed_regions" not in data:
            data["completed_regions"] = []

        return data

    def _validate_game_data(self, game_data):
        if not isinstance(game_data, dict):
            raise SaveLoadError("Game data must be a dictionary.")

        if "difficulty" in game_data:
            difficulty = game_data["difficulty"]
            if not isinstance(difficulty, str) or difficulty not in VALID_DIFFICULTIES:
                raise SaveLoadError("Invalid difficulty.")

        if "game_status" in game_data:
            status = game_data["game_status"]
            if not isinstance(status, str) or status not in VALID_GAME_STATUS:
                raise SaveLoadError("Invalid game status.")

        if "princess_life" in game_data:
            princess_life = game_data["princess_life"]
            if isinstance(princess_life, bool) or not isinstance(princess_life, int):
                raise SaveLoadError("Invalid princess life: must be an integer.")
            if not 0 <= princess_life <= 27:
                raise SaveLoadError("Invalid princess life: must be between 0 and 27.")

        if "score" in game_data:
            score = game_data["score"]
            if isinstance(score, bool) or not isinstance(score, int):
                raise SaveLoadError("Invalid score: must be an integer.")

        if "rescue_credits" in game_data:
            rescue_credits = game_data["rescue_credits"]
            if isinstance(rescue_credits, bool) or not isinstance(rescue_credits, int):
                raise SaveLoadError("Invalid rescue credits: must be an integer.")
            if rescue_credits < 0:
                raise SaveLoadError("Invalid rescue credits: cannot be negative.")

        if "failed_timeouts" in game_data:
            failed_timeouts = game_data["failed_timeouts"]
            if isinstance(failed_timeouts, bool) or not isinstance(failed_timeouts, int):
                raise SaveLoadError("Invalid failed timeouts: must be an integer.")
            if failed_timeouts < 0:
                raise SaveLoadError("Invalid failed timeouts: cannot be negative.")

        if "active_column" in game_data and game_data["active_column"] is not None:
            active_column = game_data["active_column"]
            if isinstance(active_column, bool) or not isinstance(active_column, int):
                raise SaveLoadError("Invalid active column: must be an integer or null.")
            if not 1 <= active_column <= 9:
                raise SaveLoadError("Invalid active column: must be between 1 and 9.")

        if "completed_rings" in game_data:
            game_data["completed_rings"] = _validate_objective_list(game_data["completed_rings"], "completed_rings")
        if "completed_columns" in game_data:
            game_data["completed_columns"] = _validate_objective_list(game_data["completed_columns"], "completed_columns")
        if "completed_regions" in game_data:
            game_data["completed_regions"] = _validate_objective_list(game_data["completed_regions"], "completed_regions")

        if "current_position" in game_data:
            game_data["current_position"] = _validate_position(game_data["current_position"])

        if "board" in game_data:
            board = game_data["board"]
            if isinstance(board, dict):
                if "values" in board:
                    values = board["values"]
                    if not isinstance(values, list) or len(values) != 9:
                        raise SaveLoadError("Malformed board structure.")
                    for row in values:
                        if not isinstance(row, list) or len(row) != 9:
                            raise SaveLoadError("Malformed board structure.")
            elif isinstance(board, list):
                if len(board) != 9:
                    raise SaveLoadError("Malformed board structure.")
                for row in board:
                    if not isinstance(row, list) or len(row) != 9:
                        raise SaveLoadError("Malformed board structure.")
            else:
                raise SaveLoadError("Malformed board structure.")

        return {"version": SAVE_VERSION, "game": game_data}


def save_game(game, path):
    return SaveLoad().save(game, path)


def load_game(path):
    return SaveLoad().load(path)
