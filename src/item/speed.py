import random

from item.base_item import BaseItem

QUICK_CLAW_CHANCE = 0.2
IRON_BALL_SPEED_MULTIPLIER = 0.5


# せんせいのツメ: 20%の確率で、同じ優先度の中で先に行動する
class QuickClaw(BaseItem):
    def try_move_first(self) -> bool:
        return random.random() < QUICK_CLAW_CHANCE


# くろいてっきゅう: 素早さ半減。ひこうタイプでも地面にいる扱いになり、じめん技・まきびし・どくびしを受ける
class IronBall(BaseItem):
    forces_grounded = True

    def get_speed_multiplier(self) -> float:
        return IRON_BALL_SPEED_MULTIPLIER
