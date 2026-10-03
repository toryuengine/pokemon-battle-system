from ability.base_ability import BaseAbility

# ゆうばくで相手に与えるダメージ（相手の最大HPに対する割合）
AFTERMATH_DAMAGE_RATIO = 1 / 4


# ゆうばく: 接触技で瀕死にされると、相手に相手の最大HPの1/4のダメージを与える
# 場（自分・相手のどちらか）にしめりけのポケモンがいると発動しない
class Aftermath(BaseAbility):
    def __init__(self):
        super().__init__(id=32)

    def on_contact_received(self, battle, pokemon, attacker, move):
        if not battle.is_fainted(pokemon) or battle.is_fainted(attacker):
            return
        if battle.is_damp_active():
            return
        battle.apply_damage(attacker, max(1, int(attacker.status.hp * AFTERMATH_DAMAGE_RATIO)))
