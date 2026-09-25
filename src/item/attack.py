from item.base_item import BaseItem
from move.base_move import CATEGORY_PHYSICAL

LIFE_ORB_MULTIPLIER = 1.3
LIFE_ORB_RECOIL_RATIO = 1 / 10
EXPERT_BELT_MULTIPLIER = 1.2
METRONOME_BOOST_PER_USE = 0.1
METRONOME_MAX_MULTIPLIER = 2.0
THICK_CLUB_MULTIPLIER = 2.0
# ふといホネの効果を受けられる種族
THICK_CLUB_POKEMON_NAMES = {"カラカラ", "ガラガラ"}
FLINCH_ITEM_CHANCE = 0.1


# ちからのハチマキ・ものしりメガネ: categoryの技の威力を上げる（第4世代では技の威力に掛かる）
class CategoryBoostItem(BaseItem):
    def __init__(self, id: int, category: int, multiplier: float):
        super().__init__(id)
        self.category = category
        self.multiplier = multiplier

    def get_power_multiplier(self, attacker, move) -> float:
        return self.multiplier if move.category == self.category else 1.0


# しんぴのしずく・さざなみのおこう等: move_typeの技の威力を上げる
class TypeBoostItem(BaseItem):
    def __init__(self, id: int, move_type: str, multiplier: float):
        super().__init__(id)
        self.move_type = move_type
        self.multiplier = multiplier

    def get_power_multiplier(self, attacker, move) -> float:
        return self.multiplier if move.type == self.move_type else 1.0


# ふといホネ: カラカラ・ガラガラが持つと攻撃の実数値が2倍
class ThickClub(BaseItem):
    def get_attack_stat_multiplier(self, attacker, move) -> float:
        if move.category == CATEGORY_PHYSICAL and attacker.name in THICK_CLUB_POKEMON_NAMES:
            return THICK_CLUB_MULTIPLIER
        return 1.0


# いのちのたま: ダメージ1.3倍、攻撃するたびに最大HPの1/10を失う
class LifeOrb(BaseItem):
    def get_damage_multiplier(self, attacker, effectiveness: float) -> float:
        return LIFE_ORB_MULTIPLIER

    def on_after_damage(self, battle, attacker, defender, move, total_damage: int):
        battle.apply_damage(attacker, max(1, int(attacker.status.hp * LIFE_ORB_RECOIL_RATIO)))


# たつじんのおび: 効果抜群の技のダメージ1.2倍
class ExpertBelt(BaseItem):
    def get_damage_multiplier(self, attacker, effectiveness: float) -> float:
        return EXPERT_BELT_MULTIPLIER if effectiveness > 1 else 1.0


# メトロノーム: 同じ技を連続で使うたびにダメージが1割ずつ上がる（最大2倍）
# 連続使用回数はBattle側がcurrent_status.consecutive_move_countに記録している
class Metronome(BaseItem):
    def get_damage_multiplier(self, attacker, effectiveness: float) -> float:
        multiplier = 1.0 + METRONOME_BOOST_PER_USE * attacker.current_status.consecutive_move_count
        return min(METRONOME_MAX_MULTIPLIER, multiplier)


# ピントレンズ・するどいツメ: 急所ランク+1
class CritBoostItem(BaseItem):
    def get_crit_stage_bonus(self, attacker) -> int:
        return 1


# おうじゃのしるし・するどいキバ: 元々ひるみ効果を持たないダメージ技に、10%のひるみ効果を付ける
class FlinchItem(BaseItem):
    def on_after_damage(self, battle, attacker, defender, move, total_damage: int):
        if battle.is_fainted(defender):
            return
        if not any(effect[0] == "flinch" for effect in move.effects):
            battle.try_apply_flinch(defender, FLINCH_ITEM_CHANCE)
