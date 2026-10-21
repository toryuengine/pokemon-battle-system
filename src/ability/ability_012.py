from ability.base_ability import BaseAbility


# どんかん: メロメロ状態にならない。トレース・へんしんで得た時など、すでにメロメロ状態ならすぐに治す
class Oblivious(BaseAbility):
    is_breakable = True
    prevents_infatuation = True

    def __init__(self):
        super().__init__(id=12)

    def on_update(self, battle, pokemon):
        if pokemon.current_status.infatuated_by is None:
            return
        pokemon.current_status.infatuated_by = None
        battle.reveal_ability(pokemon, self)
