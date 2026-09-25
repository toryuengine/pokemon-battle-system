from ability.base_ability import BaseAbility

# 複数の特性で共通する効果の型。個々の特性はこれを継承して、対象のタイプ・天候・状態異常だけを指定する

# しんりょく・もうか・げきりゅう・むしのしらせ: 残りHPが最大HPの1/3以下で、対応タイプの技の威力が1.5倍
PINCH_HP_RATIO = 1 / 3
PINCH_POWER_MULTIPLIER = 1.5

# ちくでん・ちょすい・かんそうはだ: 対応タイプの技を受けると最大HPの1/4回復する
ABSORB_HEAL_RATIO = 1 / 4

# すながくれ・ゆきがくれ: 対応する天候の間、受ける技の命中率が0.8倍
WEATHER_EVASION_MULTIPLIER = 0.8

# すいすい・ようりょくそ: 対応する天候の間、素早さが2倍
WEATHER_SPEED_MULTIPLIER = 2.0

# あめうけざら・アイスボディ: 対応する天候の間、ターン終了時に最大HPの1/16回復する
WEATHER_HEAL_RATIO = 1 / 16

# フィルター・ハードロック: 効果抜群の技のダメージが0.75倍
SUPER_EFFECTIVE_REDUCTION = 0.75


class PinchTypeBoostAbility(BaseAbility):
    boosted_type = None

    def get_power_multiplier(self, attacker, move, power) -> float:
        if move.is_typeless or move.type != self.boosted_type:
            return 1.0
        if attacker.current_status.current_hp <= attacker.status.hp * PINCH_HP_RATIO:
            return PINCH_POWER_MULTIPLIER
        return 1.0


# 対応タイプの相手の技（ダメージ技・相手に向けた変化技）を無効化し、代わりにon_absorbの効果を得る
class TypeAbsorbAbility(BaseAbility):
    is_breakable = True
    absorbed_type = None

    def on_try_hit(self, battle, attacker, defender, move) -> bool:
        if move.is_typeless or move.type != self.absorbed_type:
            return False
        self.on_absorb(battle, defender)
        return True

    def on_absorb(self, battle, pokemon):
        pass


class HealingAbsorbAbility(TypeAbsorbAbility):
    def on_absorb(self, battle, pokemon):
        battle.apply_heal(pokemon, ABSORB_HEAL_RATIO)


# 特定の状態異常にかからない（すでにかかっている状態異常を治す効果は未実装）
class StatusImmunityAbility(BaseAbility):
    is_breakable = True
    immune_condition = None

    def can_receive_status(self, battle, pokemon, condition) -> bool:
        return condition != self.immune_condition


class WeatherEvasionAbility(BaseAbility):
    is_breakable = True
    weather = None

    def get_evasion_multiplier(self, battle, defender) -> float:
        if battle.get_effective_weather() == self.weather:
            return WEATHER_EVASION_MULTIPLIER
        return 1.0


class WeatherSpeedAbility(BaseAbility):
    weather = None

    def get_speed_multiplier(self, battle, pokemon) -> float:
        if battle.get_effective_weather() == self.weather:
            return WEATHER_SPEED_MULTIPLIER
        return 1.0


class WeatherHealAbility(BaseAbility):
    weather = None

    def on_end_of_turn(self, battle, pokemon):
        if battle.get_effective_weather() == self.weather:
            battle.apply_heal(pokemon, WEATHER_HEAL_RATIO)


# 場に出ると天候を変える。第4世代仕様で、特性による天候はターン経過で終わらない
class WeatherSetterAbility(BaseAbility):
    weather = None

    def on_switch_in(self, battle, pokemon):
        battle.set_weather(self.weather, permanent=True)


class CriticalHitImmunityAbility(BaseAbility):
    is_breakable = True
    prevents_critical_hit = True


class SuperEffectiveReductionAbility(BaseAbility):
    is_breakable = True

    def get_received_damage_multiplier(self, defender, move, effectiveness) -> float:
        if effectiveness > 1:
            return SUPER_EFFECTIVE_REDUCTION
        return 1.0


# 第4世代のシングルバトルでは対戦結果に影響しない特性（野生との遭遇・ダブルバトル専用の効果等）
class NoBattleEffectAbility(BaseAbility):
    pass


# 対戦に影響する効果を持つが、前提となる仕組み（技の接触判定・性別・交代の強制・持ち物を奪う技等）が
# まだ無いため未実装の特性。クラスとしては保持しておき、仕組みが揃ったら個別に実装する
class UnimplementedAbility(BaseAbility):
    pass
