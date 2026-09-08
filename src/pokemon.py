import random
from dataclasses import dataclass
from typing import List, Optional

from move.base_move import BaseMove
from move.movefactory import create_move
from readpokemondata import load_pokemon_data


@dataclass
class PokemonStatus:
    hp: int
    atk: int
    defense: int
    spatk: int
    spdef: int
    spd: int


class Pokemon:
    def __init__(self, pokemon_id: int, indivisual_id: int):
        pokemon_data = load_pokemon_data()

        entry = pokemon_data[pokemon_id]
        set_data = entry["indivisual"][indivisual_id]

        self.name: str = entry["name"]
        self.type1: int = entry["type1"]
        self.type2: Optional[int] = entry["type2"]
        # 種族が持ちうる特性の中からこの個体の特性をランダムに1つ選ぶ
        self.ability: int = random.choice(entry["ability"])
        self.status: PokemonStatus = _parse_status(set_data["status"])
        self.item: int = set_data["item"]

        self.moves: List[BaseMove] = []
        for move_id in set_data["move"]:
            self.moves.append(create_move(move_id))

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
