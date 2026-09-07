import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_pokemon_data = None
_move_data = None


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
