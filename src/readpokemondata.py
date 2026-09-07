import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_pokemon_data = None
_move_data = None
_type_data = None
_type_chart_data = None


def load_pokemon_data(path=DATA_DIR / "pokemon.json"):
    global _pokemon_data
    if _pokemon_data is None:
        with open(path, encoding="utf-8") as f:
            _pokemon_data = json.load(f)
    return _pokemon_data


def load_move_data(path=DATA_DIR / "move.json"):
    global _move_data
    if _move_data is None:
        with open(path, encoding="utf-8") as f:
            _move_data = json.load(f)
    return _move_data


def load_type_data(path=DATA_DIR / "type.json"):
    global _type_data
    if _type_data is None:
        with open(path, encoding="utf-8") as f:
            _type_data = json.load(f)
    return _type_data


def load_type_chart_data(path=DATA_DIR / "type_chart.json"):
    global _type_chart_data
    if _type_chart_data is None:
        with open(path, encoding="utf-8") as f:
            _type_chart_data = json.load(f)
    return _type_chart_data
