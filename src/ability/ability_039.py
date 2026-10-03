import random

from ability.base_ability import BaseAbility
from ability.shared import CONTACT_EFFECT_CHANCE


# メロメロボディ: 接触技を受けると30%の確率で相手をメロメロにする
# 性別の条件・どんかんで防がれる点はメロメロ（技）と同じ。相手にみがわりがいても防げない
class CuteCharm(BaseAbility):
    def __init__(self):
        super().__init__(id=39)

    def on_contact_received(self, battle, pokemon, attacker, move):
        if random.random() >= CONTACT_EFFECT_CHANCE:
            return
        battle.perform_attract(pokemon, attacker)
