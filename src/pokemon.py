from dataclasses import dataclass
from typing import List, Optional

from readpokemondata import load_move_data, load_pokemon_data


@dataclass
class PokemonStatus:
    hp: int
    atk: int
    defense: int
    spatk: int
    spdef: int
    spd: int


@dataclass
class Move:
    id: int
    name: str
    type: str
    category: str
    power: int
    pp: int
    hitrate: int


class Pokemon:
    def __init__(self, pokemon_id: int, indivisual_id: int):
        pokemon_data = load_pokemon_data()
        move_data = load_move_data()

        entry = pokemon_data[pokemon_id]
        set_data = entry["indivisual"][indivisual_id]

        self.name: str = entry["name"]
        self.type1: int = entry["type1"]
        self.type2: Optional[int] = entry["type2"]
        self.ability: List[int] = entry["ability"]
        self.status: PokemonStatus = _parse_status(set_data["status"])
        self.item: int = set_data["item"]

        self.moves: List[Move] = []
        for move_id in set_data["move"]:
            self.moves.append(_parse_move(move_id, move_data[str(move_id)]))

    def __repr__(self):
        return (
            f"Pokemon(name={self.name!r}, type1={self.type1!r}, type2={self.type2!r}, "
            f"status={self.status!r}, item={self.item!r}, ability={self.ability!r}, "
            f"moves={self.moves!r})"
        )


def _parse_status(status_data) -> PokemonStatus:
    return PokemonStatus(
        hp=status_data["hp"],
        atk=status_data["atk"],
        defense=status_data["def"],
        spatk=status_data["spatk"],
        spdef=status_data["spdef"],
        spd=status_data["spd"],
    )


def _parse_move(move_id: int, move_data) -> Move:
    return Move(
        id=move_id,
        name=move_data["name"],
        type=move_data["type"],
        category=move_data["category"],
        power=move_data["power"],
        pp=move_data["pp"],
        hitrate=move_data["hitrate"],
    )
