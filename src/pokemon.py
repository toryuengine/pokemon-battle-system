from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PokemonStatus:
    hp: int
    atk: int
    defense: int
    spatk: int
    spdef: int
    spd: int


@dataclass
class PokemonSet:
    status: PokemonStatus
    item: int
    ability: int
    move: List[int]


@dataclass
class Pokemon:
    name: str
    type1: int
    type2: Optional[int]
    indivisual: List[PokemonSet]
