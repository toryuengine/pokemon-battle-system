from typing import List

from pokemon import Pokemon


# 手持ちポケモンと、場に設置された罠（相手側からの設置技）を管理する
class Trainer:
    def __init__(self, party: List[Pokemon]):
        self.party = party
        self.active_index = 0

        # 自分の場に設置されている罠。設置技はここを書き換える
        self.stealth_rock = False
        self.spikes = 0  # 0〜3
        self.toxic_spikes = 0  # 0〜2

    @property
    def active(self) -> Pokemon:
        return self.party[self.active_index]

    # 手持ち全員が瀕死かどうか
    def is_defeated(self) -> bool:
        for pokemon in self.party:
            if pokemon.current_status.current_hp > 0:
                return False
        return True

    # 場に出ていない手持ちの中から、生きている最初の1体のインデックスを探す（いなければNone）
    def find_next_alive_index(self):
        for index, pokemon in enumerate(self.party):
            if index != self.active_index and pokemon.current_status.current_hp > 0:
                return index
        return None
