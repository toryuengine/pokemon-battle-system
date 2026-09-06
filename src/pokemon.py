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
class Move:
    id: int
    name: str
    type: str
    category: str
    power: int
    pp: int
    hitrate: int


@dataclass
class Pokemon:
    name: str
    type1: int
    type2: Optional[int]
    status: PokemonStatus
    item: int
    ability: int
    moves: List[Move]
