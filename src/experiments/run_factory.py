"""Agentにバトルファクトリーを周回させ、連勝数を集計する（CLAUDE.md 4節の「自動プレイ」「比較」、5節の評価指標）

実行例（src/ をカレントにして）:
    python -m experiments.run_factory --agent random --level lv50 --runs 200 --seed 0
"""
import argparse
import random
import subprocess
import sys
from pathlib import Path

from agents.random_agent import RandomAgent
from factory import rules
from factory.challenge import FactoryChallenge

# 名前で選べるAgent。AI手法を足したらここに登録する（引数はrandom.Random）
AGENTS = {
    "random": lambda rng: RandomAgent(rng),
    "random-switch": lambda rng: RandomAgent(rng, switch_chance=0.1, trade_chance=0.3),
}


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=Path(__file__).resolve().parent, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


# 1回の挑戦をseedで再現できるように、生成用・Agent用・対戦エンジン用の乱数をすべてseedから決める
def run_one(agent_name: str, level: str, seed: int, max_battles: int):
    random.seed(seed)  # 対戦エンジンはまだrandomモジュールを直接使うため
    agent = AGENTS[agent_name](random.Random(f"agent-{seed}"))
    challenge = FactoryChallenge(level, agent, random.Random(f"factory-{seed}"))
    return challenge.run(max_battles=max_battles)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=sorted(AGENTS), nargs="+", default=["random"])
    parser.add_argument("--level", choices=[rules.LEVEL_50, rules.LEVEL_OPEN], default=rules.LEVEL_50)
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-battles", type=int, default=200, help="1回の挑戦の上限戦数（無限に勝ち続ける場合の打ち切り）")
    args = parser.parse_args(argv)

    print(f"level={args.level} runs={args.runs} seed={args.seed} commit={git_commit()}")
    for agent_name in args.agent:
        streaks = []
        brain_results = {21: [0, 0], 49: [0, 0]}  # [挑戦数, 勝利数]
        for i in range(args.runs):
            result = run_one(agent_name, args.level, args.seed + i, args.max_battles)
            streaks.append(result.win_streak)
            for record in result.battles:
                if record.is_brain_battle:
                    brain_results[record.battle_number][0] += 1
                    brain_results[record.battle_number][1] += record.won
        clear_rate = sum(1 for s in streaks if s >= rules.BATTLES_PER_ROUND) / len(streaks)
        brains = "  ".join(f"{n}戦目 {won}/{played}" for n, (played, won) in brain_results.items())
        print(f"{agent_name:>14}: 平均連勝 {sum(streaks) / len(streaks):.2f}  最大 {max(streaks)}  "
              f"1周クリア率 {clear_rate:.1%}  ネジキ {brains}")


if __name__ == "__main__":
    sys.exit(main())
