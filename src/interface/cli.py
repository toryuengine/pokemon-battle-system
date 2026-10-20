"""バトルファクトリーのCLI。進め方は3つあり、どれも同じ FactoryChallenge の上で Agent だけを差し替える（CLAUDE.md 4節）。

    cd src
    python -m interface.cli play  [--seed N] [--advisor random]       人間が遊ぶ（advisorを付けるとAIの助言を表示）
    python -m interface.cli watch [--agent random] [--seed N] [--pause]  AIの挑戦を表示しながら見る
    python -m interface.cli auto  [--agent random] [--challenges N] [--seed N]  AIに表示なしで多数回挑戦させて成績を出す

auto は experiments/evaluate.py と同じ処理（学習・比較用の自動プレイ）。
--seed を省くと毎回違う挑戦になる（使ったシードは最初に表示するので、同じ挑戦をやり直せる）。
"""
import argparse
import random
from typing import Callable, Optional

from agents.registry import AGENTS, make_agent
from factory import rules
from factory.challenge import BattleRecord, FactoryChallenge
from interface.human_agent import HumanAgent, QuitGame
from interface.spectator import SpectatorAgent


# 1戦の結果のまとめ（勝敗・連勝・周クリアのBP）。対戦の直後（交換の前・負けたときの連勝のリセットの前）に作る
def battle_summary(record: BattleRecord, challenge: FactoryChallenge) -> list:
    if not record.won:
        return [f"【{record.battle_number}戦目で負け】 連勝は {record.battle_number - 1} で終わりました"
                f"（BP 合計 {challenge.state.bp}）"]
    lines = [f"【{record.battle_number}戦目 勝ち】 連勝 {challenge.state.win_streak}"]
    if record.nejiki is not None:
        lines.append(f"ネジキに勝った！ {'銀' if record.nejiki == 'silver' else '金'}のプリントをもらった")
    if record.battle_in_round == rules.BATTLES_PER_ROUND:
        lines.append(f"{record.round_number}周目 クリア！ BP +{rules.bp_for_round(record.round_number)}"
                     f"（合計 {challenge.state.bp}）")
    return lines


# 負けるまで1戦ずつ進め、結果を出す。max_battlesで打ち切れる。最後の戦の記録を返す（1戦もしなければNone）
def run_challenge(challenge: FactoryChallenge, output_fn: Callable[[str], None],
                  max_battles: Optional[int] = None) -> Optional[BattleRecord]:
    record = None
    played = 0
    while max_battles is None or played < max_battles:
        record = challenge.play_next(
            on_battle_end=lambda result: [output_fn(line) for line in battle_summary(result, challenge)])
        played += 1
        if not record.won:
            break
    return record


def _seed(seed: Optional[int]) -> int:
    return seed if seed is not None else random.SystemRandom().randrange(10 ** 9)


def play(seed: Optional[int], advisor_name: Optional[str], input_fn=input, output_fn=print):
    seed = _seed(seed)
    output_fn(f"バトルファクトリー（シングル・オープンレベル）  seed={seed}")
    advisor = make_agent(advisor_name, random.Random(f"advisor-{seed}")) if advisor_name else None
    agent = HumanAgent(input_fn, output_fn, advisor=advisor, advisor_name=advisor_name or "AI")
    challenge = FactoryChallenge(agent, random.Random(seed))
    try:
        while True:
            run_challenge(challenge, output_fn)
            if input_fn("もう一度挑戦しますか？ (y/N) > ").strip().lower() != "y":
                break
    except QuitGame:
        output_fn(f"やめました（連勝 {challenge.state.win_streak}・BP {challenge.state.bp}）")
    except EOFError:
        output_fn("")


def watch(agent_name: str, seed: Optional[int], max_battles: Optional[int], pause: bool,
          input_fn=input, output_fn=print):
    seed = _seed(seed)
    output_fn(f"観戦: agent={agent_name} seed={seed}")
    pause_fn = (lambda: input_fn("")) if pause else None
    agent = SpectatorAgent(make_agent(agent_name, random.Random(f"agent-{seed}")), output_fn, pause_fn)
    try:
        run_challenge(FactoryChallenge(agent, random.Random(seed)), output_fn, max_battles)
    except (EOFError, KeyboardInterrupt):
        output_fn("")


def main():
    parser = argparse.ArgumentParser(description="バトルファクトリー（シングル・オープンレベル）のCLI")
    sub = parser.add_subparsers(dest="mode", required=True)

    play_parser = sub.add_parser("play", help="人間が遊ぶ")
    play_parser.add_argument("--seed", type=int, default=None)
    play_parser.add_argument("--advisor", choices=sorted(AGENTS), default=None, help="助言を表示する Agent")

    watch_parser = sub.add_parser("watch", help="AIの挑戦を表示しながら見る")
    watch_parser.add_argument("--agent", choices=sorted(AGENTS), default="random")
    watch_parser.add_argument("--seed", type=int, default=None)
    watch_parser.add_argument("--max-battles", type=int, default=None, help="この戦数で打ち切る")
    watch_parser.add_argument("--pause", action="store_true", help="1ターンごとにEnterを待つ")

    auto_parser = sub.add_parser("auto", help="AIに表示なしで多数回挑戦させて成績を出す")
    auto_parser.add_argument("--agent", choices=sorted(AGENTS), default="random")
    auto_parser.add_argument("--challenges", type=int, default=1000)
    auto_parser.add_argument("--seed", type=int, default=0)
    auto_parser.add_argument("--max-battles", type=int, default=None, help="1回の挑戦を打ち切る戦数")

    args = parser.parse_args()
    if args.mode == "play":
        play(args.seed, args.advisor)
    elif args.mode == "watch":
        watch(args.agent, args.seed, args.max_battles, args.pause)
    else:
        # 自動プレイは評価スクリプトと同じものを使う（interface から experiments への依存はこの入口だけ）
        from experiments.evaluate import evaluate
        print(evaluate(args.agent, args.challenges, args.seed, args.max_battles).format())


if __name__ == "__main__":
    main()
