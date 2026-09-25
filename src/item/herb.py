from item.base_item import BaseItem


# しろいハーブ: 能力ランクが下がると、下がっている能力ランクを全て0に戻す（1回で消費）
class WhiteHerb(BaseItem):
    def activate(self, battle, pokemon):
        if self._restore_lowered_stats(battle, pokemon):
            battle.consume_item(pokemon)

    # なげつけるで投げつけられた相手の、下がっている能力ランクを0に戻す
    def on_flung(self, battle, target, source):
        self._restore_lowered_stats(battle, target)

    # 下がっている能力ランクを全て0に戻す。戻したらTrueを返す
    def _restore_lowered_stats(self, battle, pokemon) -> bool:
        stages = battle.get_stages(pokemon)
        lowered_stats = [name for name, value in vars(stages).items() if value < 0]
        for stat_name in lowered_stats:
            setattr(stages, stat_name, 0)
        return bool(lowered_stats)


# パワフルハーブ: 溜め技の溜めターンを1回だけ省略する（晴れのソーラービーム等、元々溜めない場合は呼ばれない）
class PowerHerb(BaseItem):
    def try_skip_charge_turn(self, battle, pokemon) -> bool:
        battle.consume_item(pokemon)
        return True
