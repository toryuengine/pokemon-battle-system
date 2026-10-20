from typing import Callable, List, Optional

from pokemon import Pokemon


# 手動交代の判断（交代するかどうか・誰に交代するか）を決める関数の型。
# 毎ターンの技選択の前に(battle, trainer)で呼ばれ、交代先の手持ちのインデックスを返す（交代しないならNone）
SwitchPolicy = Callable[["Battle", "Trainer"], Optional[int]]


# 技選択の判断を決める関数の型。手動で交代しないターンに(battle, trainer, 選べる技の一覧)で呼ばれ、
# その一覧の中から1つ選んで返す。固定（溜め技・げきりん・アンコール・こだわり系）・制限（かなしばり・ちょうはつ・
# いちゃもん・PP切れ）の処理はBattle側で済ませてあり、選べる技が無い（わるあがき）・1つに固定されている場合は呼ばれない
MovePolicy = Callable[["Battle", "Trainer", List["BaseMove"]], "BaseMove"]

# 瀕死・とんぼがえり・バトンタッチで交代するとき、次に出す個体を決める関数の型。
# (battle, trainer, 交代先に選べる手持ちのインデックスの一覧, 理由)で呼ばれ、その一覧の中から1つ選んで返す。
# 理由は"faint"（瀕死）・"u_turn"（とんぼがえり）・"baton_pass"（バトンタッチ）のどれか
ReplacementPolicy = Callable[["Battle", "Trainer", List[int], str], int]


# 毎ターンchanceの確率で、交代できる手持ちの中からランダムに1体選んで交代する判断
def random_switch_policy(chance: float) -> SwitchPolicy:
    def policy(battle, trainer: "Trainer") -> Optional[int]:
        candidates = trainer.find_switch_candidates()
        if not candidates or battle.rng.random() >= chance:
            return None
        return battle.rng.choice(candidates)
    return policy


# 手持ちポケモンと、場に設置された罠（相手側からの設置技）を管理する
class Trainer:
    # switch_policyは手動交代の判断。Noneなら自分の意思では交代しない（瀕死時・とんぼがえり等の自動交代のみ）
    # move_policyは技選択の判断。Noneなら選べる技の中からランダムに選ぶ
    # replacement_policyは瀕死・とんぼがえり・バトンタッチの交代先の判断。Noneなら手持ち順で最初の生存個体を出す
    def __init__(self, party: List[Pokemon], switch_policy: Optional[SwitchPolicy] = None,
                 move_policy: Optional[MovePolicy] = None, replacement_policy: Optional[ReplacementPolicy] = None):
        self.party = party
        self.active_index = 0
        self.switch_policy = switch_policy
        self.move_policy = move_policy
        self.replacement_policy = replacement_policy

        # 自分の場に設置されている罠。設置技はここを書き換える
        self.stealth_rock = False
        self.spikes = 0  # 0〜3
        self.toxic_spikes = 0  # 0〜2

        # 自分の場に張られている壁の残りターン数。0なら無効
        self.reflect_turns_remaining = 0
        self.light_screen_turns_remaining = 0
        # 自分の場に張られているしんぴのまもりの残りターン数。0なら無効
        self.safeguard_turns_remaining = 0

        # 自分の場に向けて撃たれたみらいよちの、攻撃が来るまでの残りターン数（0なら無し）と、
        # 使った時点で計算済みのダメージ・命中率。攻撃はその時点で場に出ている個体が受ける
        self.future_sight_turns_remaining = 0
        self.future_sight_damage = 0
        self.future_sight_hitrate = 0

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

    # 場に出ていない手持ちのうち、生きていて交代先に選べる個体のインデックスの一覧
    def find_switch_candidates(self) -> List[int]:
        return [index for index, pokemon in enumerate(self.party)
                if index != self.active_index and pokemon.current_status.current_hp > 0]
