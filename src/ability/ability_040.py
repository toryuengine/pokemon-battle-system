from ability.base_ability import BaseAbility


# ぶきよう: 持ち物の効果が無くなる（くろいてっきゅう等、ぶきようでも効果が残る持ち物を除く）。なげつけるも失敗する
# 持ち物そのものは持ったままなので、トリック・はたきおとす等で持ち物をやり取りすることはできる
class Klutz(BaseAbility):
    ignores_held_item = True

    def __init__(self):
        super().__init__(id=40)
