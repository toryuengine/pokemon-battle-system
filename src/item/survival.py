import random

from item.base_item import BaseItem

FOCUS_BAND_CHANCE = 0.1


# きあいのタスキ: HP満タンから瀕死になる攻撃をHP1で耐える（1回で消費）
# 複数回攻撃の2発目以降は満タンではないので耐えられない
class FocusSash(BaseItem):
    def try_endure_fatal_hit(self, battle, defender) -> bool:
        if defender.current_status.current_hp != defender.status.hp:
            return False
        battle.consume_item(defender)
        return True


# きあいのハチマキ: 10%の確率で瀕死になる攻撃をHP1で耐える（消費しない）
class FocusBand(BaseItem):
    def try_endure_fatal_hit(self, battle, defender) -> bool:
        return random.random() < FOCUS_BAND_CHANCE
