from item.base_item import BaseItem


# しろいハーブ: 能力ランクが下がると、下がっている能力ランクを全て0に戻す（1回で消費）
class WhiteHerb(BaseItem):
    def activate(self, battle, pokemon):
        stages = battle.get_stages(pokemon)
        lowered_stats = [name for name, value in vars(stages).items() if value < 0]
        if not lowered_stats:
            return
        for stat_name in lowered_stats:
            setattr(stages, stat_name, 0)
        battle.consume_item(pokemon)


# パワフルハーブ: 溜め技の溜めターンを1回だけ省略する（晴れのソーラービーム等、元々溜めない場合は呼ばれない）
class PowerHerb(BaseItem):
    def try_skip_charge_turn(self, battle, pokemon) -> bool:
        battle.consume_item(pokemon)
        return True
