from ability.base_ability import BaseAbility


# いかりのつぼ: 急所に当たると攻撃が最大（+6）まで上がる
class AngerPoint(BaseAbility):
    def __init__(self):
        super().__init__(id=48)

    def on_critical_hit_received(self, battle, pokemon):
        battle.get_stages(pokemon).atk = 6
