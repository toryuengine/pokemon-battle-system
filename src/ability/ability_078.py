from ability.base_ability import BaseAbility

TYPE_ID_STEEL = 16


# じりょく: はがねタイプの相手を交代できなくする
class MagnetPull(BaseAbility):
    def __init__(self):
        super().__init__(id=78)

    def traps_opponent(self, battle, opponent) -> bool:
        return TYPE_ID_STEEL in (opponent.type1, opponent.type2)
