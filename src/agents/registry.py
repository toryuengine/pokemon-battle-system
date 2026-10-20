"""名前で選べる Agent の一覧。

自動プレイ（experiments/evaluate.py）・観戦や助言（interface/cli.py）で、同じ名前で同じ Agent を作れるようにする
（CLAUDE.md 4節）。AI手法を足したら、ここにも登録する。
"""
import random
from typing import Callable, Dict

from agents.base import FactoryAgent
from agents.random_agent import RandomAgent

# 名前 → (Agent用の乱数) -> Agent
AGENTS: Dict[str, Callable[[random.Random], FactoryAgent]] = {
    "random": lambda rng: RandomAgent(rng),
    "random-noswitch": lambda rng: RandomAgent(rng, switch_chance=0.0),
}


def make_agent(name: str, rng: random.Random) -> FactoryAgent:
    if name not in AGENTS:
        raise ValueError(f"unknown agent {name!r}（選べるのは {', '.join(sorted(AGENTS))}）")
    return AGENTS[name](rng)
