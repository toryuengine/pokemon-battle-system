from pokemon import Pokemon


class Battle:
    def __init__(self, pokemon1: Pokemon, pokemon2: Pokemon):
        self.pokemon1 = pokemon1
        self.pokemon2 = pokemon2
        self.current_hp1 = pokemon1.status.hp
        self.current_hp2 = pokemon2.status.hp

    def get_current_hp(self, target: Pokemon) -> int:
        if target is self.pokemon1:
            return self.current_hp1
        if target is self.pokemon2:
            return self.current_hp2
        raise ValueError("target is not part of this battle")

    def apply_damage(self, target: Pokemon, damage: int):
        if target is self.pokemon1:
            self.current_hp1 = max(0, self.current_hp1 - damage)
        elif target is self.pokemon2:
            self.current_hp2 = max(0, self.current_hp2 - damage)
        else:
            raise ValueError("target is not part of this battle")

    def is_fainted(self, target: Pokemon) -> bool:
        return self.get_current_hp(target) <= 0

    def get_winner(self):
        pokemon1_fainted = self.is_fainted(self.pokemon1)
        pokemon2_fainted = self.is_fainted(self.pokemon2)

        if pokemon1_fainted and pokemon2_fainted:
            return None
        if pokemon1_fainted:
            return self.pokemon2
        if pokemon2_fainted:
            return self.pokemon1
        return None
