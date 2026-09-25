from item.base_item import BaseItem

LEFTOVERS_HEAL_RATIO = 1 / 16
BLACK_SLUDGE_DAMAGE_RATIO = 1 / 8
SHELL_BELL_RATIO = 1 / 8
BIG_ROOT_MULTIPLIER = 1.3
TYPE_ID_POISON = 7


def _heal_by_max_hp_ratio(pokemon, ratio):
    max_hp = pokemon.status.hp
    heal_amount = max(1, int(max_hp * ratio))
    pokemon.current_status.current_hp = min(max_hp, pokemon.current_status.current_hp + heal_amount)


# たべのこし: 毎ターン終了時に最大HPの1/16回復
class Leftovers(BaseItem):
    def on_end_of_turn(self, battle, pokemon):
        _heal_by_max_hp_ratio(pokemon, LEFTOVERS_HEAL_RATIO)


# くろいヘドロ: 毎ターン終了時、どくタイプなら最大HPの1/16回復、それ以外は1/8ダメージ
class BlackSludge(BaseItem):
    def on_end_of_turn(self, battle, pokemon):
        if TYPE_ID_POISON in (pokemon.type1, pokemon.type2):
            _heal_by_max_hp_ratio(pokemon, LEFTOVERS_HEAL_RATIO)
        else:
            battle.apply_damage(pokemon, max(1, int(pokemon.status.hp * BLACK_SLUDGE_DAMAGE_RATIO)))


# かいがらのすず: 与えたダメージの1/8回復
class ShellBell(BaseItem):
    def on_after_damage(self, battle, attacker, defender, move, total_damage: int):
        heal_amount = max(1, int(total_damage * SHELL_BELL_RATIO))
        attacker.current_status.current_hp = min(attacker.status.hp, attacker.current_status.current_hp + heal_amount)


# おおきなねっこ: 吸収技の回復量1.3倍
class BigRoot(BaseItem):
    def get_drain_multiplier(self) -> float:
        return BIG_ROOT_MULTIPLIER
