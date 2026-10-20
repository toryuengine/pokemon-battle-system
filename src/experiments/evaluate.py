"""Agent にファクトリーを多数回挑戦させ、成績（CLAUDE.md 5節の評価指標）を出す。

    cd src
    python -m experiments.evaluate --agent random --challenges 1000 --seed 0

挑戦ごとに、ファクトリー（ポケモンの生成・対戦の乱数）と Agent に別々の乱数を渡す。ファクトリー側の乱数は
シードと挑戦の番号だけで決まるので、違う Agent でも同じシードなら最初のレンタル候補・相手は同じになる
（判断が変わればそれ以降の乱数の進み方は変わる）。
"""
import argparse
import random
import subprocess
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from agents.random_agent import RandomAgent
from factory import rules
from factory.challenge import ChallengeResult, FactoryChallenge

# 挑戦の番号ごとの乱数のシードを作るときの倍数（シードが違えば挑戦の乱数が重ならないように）
SEED_STRIDE = 1_000_003

# --agent で選べる Agent。(Agent用の乱数) -> Agent
AGENTS: Dict[str, Callable[[random.Random], object]] = {
    "random": lambda rng: RandomAgent(rng),
    "random-noswitch": lambda rng: RandomAgent(rng, switch_chance=0.0),
}


@dataclass
class EvaluationSummary:
    agent: str
    seed: int
    challenges: int
    commit: str
    win_streaks: List[int] = field(default_factory=list)
    # 周の番号 → (その周に挑んだ回数, クリアした回数)
    round_attempts: Dict[int, List[int]] = field(default_factory=dict)
    # "silver"/"gold" → (挑んだ回数, 勝った回数)
    nejiki_attempts: Dict[str, List[int]] = field(default_factory=dict)
    battles: int = 0
    draws: int = 0
    timeouts: int = 0
    elapsed_seconds: float = 0.0

    @property
    def mean_win_streak(self) -> float:
        return sum(self.win_streaks) / len(self.win_streaks)

    def add(self, result: ChallengeResult):
        self.win_streaks.append(result.win_streak)
        for record in result.battles:
            self.battles += 1
            self.draws += record.is_draw
            self.timeouts += record.timed_out
            if record.battle_in_round == 1:
                self.round_attempts.setdefault(record.round_number, [0, 0])[0] += 1
            if record.won and record.battle_in_round == rules.BATTLES_PER_ROUND:
                self.round_attempts[record.round_number][1] += 1
            if record.nejiki is not None:
                attempts = self.nejiki_attempts.setdefault(record.nejiki, [0, 0])
                attempts[0] += 1
                attempts[1] += record.won

    def format(self) -> str:
        lines = [
            f"agent={self.agent} seed={self.seed} challenges={self.challenges} commit={self.commit}",
            f"平均連勝数: {self.mean_win_streak:.3f}（最大 {max(self.win_streaks)}）",
            f"対戦数: {self.battles}（引き分け {self.draws}・ターン上限 {self.timeouts}）  時間: {self.elapsed_seconds:.1f}秒",
        ]
        for round_number in sorted(self.round_attempts):
            attempts, cleared = self.round_attempts[round_number]
            lines.append(f"  {round_number}周目: 挑戦 {attempts} 回・クリア {cleared} 回（{cleared / attempts:.1%}）")
        for kind in ("silver", "gold"):
            if kind in self.nejiki_attempts:
                attempts, won = self.nejiki_attempts[kind]
                lines.append(f"  ネジキ戦({kind}): {attempts} 戦 {won} 勝（{won / attempts:.1%}）")
        return "\n".join(lines)


def current_commit() -> str:
    try:
        # コミットしていない変更があれば末尾に"-dirty"が付く
        return subprocess.run(["git", "describe", "--always", "--dirty"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


# agent_nameの Agent に challenges 回挑戦させる。max_battlesを渡すと、1回の挑戦をその戦数で打ち切る
def evaluate(agent_name: str, challenges: int, seed: int, max_battles: Optional[int] = None) -> EvaluationSummary:
    make_agent = AGENTS[agent_name]
    summary = EvaluationSummary(agent_name, seed, challenges, current_commit())
    start = time.perf_counter()
    for index in range(challenges):
        factory_rng = random.Random(seed * SEED_STRIDE + index)
        agent_rng = random.Random(f"agent-{seed}-{index}")
        challenge = FactoryChallenge(make_agent(agent_rng), factory_rng)
        summary.add(challenge.play_challenge(max_battles=max_battles))
    summary.elapsed_seconds = time.perf_counter() - start
    return summary


def main():
    parser = argparse.ArgumentParser(description="Agent にバトルファクトリーを多数回挑戦させて成績を出す")
    parser.add_argument("--agent", choices=sorted(AGENTS), default="random")
    parser.add_argument("--challenges", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-battles", type=int, default=None, help="1回の挑戦を打ち切る戦数")
    args = parser.parse_args()
    print(evaluate(args.agent, args.challenges, args.seed, args.max_battles).format())


if __name__ == "__main__":
    main()
