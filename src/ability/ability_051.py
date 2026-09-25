from ability.shared import HealingAbsorbAbility

DRY_SKIN_FIRE_MULTIPLIER = 1.25
DRY_SKIN_WEATHER_RATIO = 1 / 8


# かんそうはだ: みず技を受けると最大HPの1/4回復する。受けるほのお技の威力が1.25倍。
# あめの間はターン終了時に最大HPの1/8回復し、にほんばれの間は最大HPの1/8のダメージを受ける
class DrySkin(HealingAbsorbAbility):
    absorbed_type = "みず"

    def __init__(self):
        super().__init__(id=51)

    def get_received_power_multiplier(self, defender, move) -> float:
        if not move.is_typeless and move.type == "ほのお":
            return DRY_SKIN_FIRE_MULTIPLIER
        return 1.0

    def on_end_of_turn(self, battle, pokemon):
        weather = battle.get_effective_weather()
        if weather == "rain":
            battle.apply_heal(pokemon, DRY_SKIN_WEATHER_RATIO)
        elif weather == "sun":
            battle.apply_damage(pokemon, max(1, int(pokemon.status.hp * DRY_SKIN_WEATHER_RATIO)))
