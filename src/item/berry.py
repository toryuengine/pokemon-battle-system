from item.base_item import BaseItem

PINCH_BERRY_HP_RATIO = 1 / 4
SITRUS_BERRY_HP_RATIO = 1 / 2
SITRUS_BERRY_HEAL_RATIO = 1 / 4
RESIST_BERRY_MULTIPLIER = 0.5


# 状態異常・こんらんを回復するきのみ（ラムのみ・クラボのみ・カゴのみ・キーのみ）
# cures_conditionsには回復できる状態異常（status_condition）のタプルを渡す（Noneなら全ての状態異常を回復する）。
# cures_confusionにはこんらんを回復できるかを渡す
class StatusCureBerry(BaseItem):
    def __init__(self, id: int, cures_conditions=(), cures_confusion=False):
        super().__init__(id)
        self.cures_conditions = cures_conditions
        self.cures_confusion = cures_confusion

    def activate(self, battle, pokemon):
        if self._cure(battle, pokemon):
            battle.consume_item(pokemon)

    # なげつけるで投げつけられた相手が食べた扱いになり、相手の状態異常を回復する
    def on_flung(self, battle, target, source):
        self._cure(battle, target)

    # pokemonの対応する状態異常・こんらんを回復する。回復したらTrueを返す
    def _cure(self, battle, pokemon) -> bool:
        status = pokemon.current_status
        cures_condition = status.status_condition is not None and (
            self.cures_conditions is None or status.status_condition in self.cures_conditions)
        cures_confusion = self.cures_confusion and status.confusion_turns_remaining > 0
        if cures_condition:
            battle.cure_status(pokemon)
        if cures_confusion:
            status.confusion_turns_remaining = 0
        return cures_condition or cures_confusion


# オボンのみ: HPが半分以下になったら最大HPの1/4回復する
class SitrusBerry(BaseItem):
    def activate(self, battle, pokemon):
        status = pokemon.current_status
        max_hp = pokemon.status.hp
        if status.current_hp <= int(max_hp * SITRUS_BERRY_HP_RATIO):
            heal_amount = int(max_hp * SITRUS_BERRY_HEAL_RATIO)
            status.current_hp = min(max_hp, status.current_hp + heal_amount)
            battle.consume_item(pokemon)

    # なげつけるで投げつけられた相手が、HPに関係なく食べた扱いになる
    def on_flung(self, battle, target, source):
        battle.apply_heal(target, SITRUS_BERRY_HEAL_RATIO)


# ピンチ実（チイラのみ・ヤタピのみ・カムラのみ）: HPが1/4以下（くいしんぼうなら1/2以下）になったら
# stat_nameの能力ランク+1（既に+6なら発動しない）
class PinchBerry(BaseItem):
    def __init__(self, id: int, stat_name: str):
        super().__init__(id)
        self.stat_name = stat_name

    def activate(self, battle, pokemon):
        stages = battle.get_stages(pokemon)
        hp_ratio = battle.get_ability(pokemon).pinch_berry_hp_ratio or PINCH_BERRY_HP_RATIO
        if (pokemon.current_status.current_hp <= int(pokemon.status.hp * hp_ratio)
                and getattr(stages, self.stat_name) < 6):
            battle.change_stage(pokemon, self.stat_name, 1)
            battle.consume_item(pokemon)

    # なげつけるで投げつけられた相手が、HPに関係なく食べた扱いになる
    def on_flung(self, battle, target, source):
        battle.change_stage(target, self.stat_name, 1)


# 半減実（オッカのみ等）: resist_typeの効果抜群の技を受けたとき、ダメージを半分にして消費する
# 複数回攻撃なら最初の1発だけ（1発目で消費されるため）
class ResistBerry(BaseItem):
    def __init__(self, id: int, resist_type: str):
        super().__init__(id)
        self.resist_type = resist_type

    def get_received_damage_multiplier(self, defender, move, effectiveness: float) -> float:
        if move.is_typeless or effectiveness <= 1 or move.type != self.resist_type:
            return 1.0
        return RESIST_BERRY_MULTIPLIER

    def on_received_damage_reduced(self, battle, defender):
        battle.consume_item(defender)
